"""Export, review, check, and release an analytics workbench package draft.

awb-init's installer places this file at `src/packaging/draft.py`. `src/awb.py` runs its commands:

    python3 src/awb.py export <investigation> <package> [--chart RESULT[:COLUMNS][@first=N|@where=COLUMN=VALUE[,VALUE]]]...
        [--dataset NAME=RESULT[:COLUMNS]]... [--no-datasets] [--result RESULT]... [--round COLUMN=PLACES]...
    python3 src/awb.py review-rules check <investigation> <package>
    python3 src/awb.py review-rules add --area AREA --severity error|warning --rule TEXT --fix TEXT [--pattern REGEX] [--scope line|slide|document]
        [--package INVESTIGATION/PACKAGE] --confirmed
    python3 src/awb.py review-receipt record <investigation> <package> --kind full|scoped --report FILE|- [--accept TEXT]...
    python3 src/awb.py review-receipt show <investigation> <package>
    python3 src/awb.py check-draft <investigation> <package> [--verify-only]
    python3 src/awb.py release <investigation> <package>
    python3 src/awb.py copy-releases <investigation> [<package>]

Each prints one line of JSON. The manifest is the draft's `manifest.json`; chart and dataset files
are CSV; review rules live in `foundation/review-rules.md`, and the last review's record in the package's
`review/`, beside `draft/`. Standard library only; `export` also needs the project's `src/provenance.py`.
"""

import argparse
import bisect
import csv
import difflib
import hashlib
import html
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, namedtuple
from datetime import datetime
from decimal import MAX_EMAX, MAX_PREC, MIN_EMIN, ROUND_HALF_UP, Context, Decimal, InvalidOperation, localcontext
from pathlib import Path

MANIFEST = "manifest.json"
# The optional audience-facing account of method; when the draft holds it, the names, numbers, claims,
# Markdown, and review-rule checks read it beside findings.md and methodology.md.
METHODOLOGY_NOTE = "methodology-note.md"
_SIMPLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_EVIDENCE_SCHEMA = "awb-evidence/3"
_EVIDENCE_LINK = re.compile(r"evidence/([A-Za-z0-9][A-Za-z0-9._-]*)\.json")
_DISPOSITIONS = ("omit", "release_with_caveat")
_STORAGE_LINE = "Released packages are kept at:"
_REASON = "Revalidation reason or caveat"
_BLOCKED = ("the current state differs from the recorded producing state; an export would not serialize "
            "the represented result. Stop: changed results need separately authorized analytical work")
# A plain word is never flagged as a name: it collides with ordinary prose ("claims", "period").
_PLAIN_WORD = re.compile(r"[A-Za-z]+")

# SQL names: comments and string literals are blanked first so paths and prose never count.
_SQL_NOISE = re.compile(r"--[^\n]*|/\*.*?\*/|'(?:[^']|'')*'", re.DOTALL)
_IDENT = r'(?:"[^"]+"|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|[A-Za-z_][\w$]*))*'
_CREATE = re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:TEMP|TEMPORARY|MATERIALIZED)\s+)?"
                     rf"(?:VIEW|TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?({_IDENT})", re.IGNORECASE)
# A source not followed by `(` (a table function) or `)` (EXTRACT(year FROM column)).
_SOURCE = re.compile(rf"\b(?:FROM|JOIN)\s+({_IDENT})(?![\w$\"])(?!\s*[.()])", re.IGNORECASE)
_CTE = re.compile(rf"(?:\bWITH(?:\s+RECURSIVE)?|,)\s*({_IDENT})\s*(?:\([^)]*\)\s*)?AS\s*"
                  r"(?:NOT\s+)?(?:MATERIALIZED\s+)?\(", re.IGNORECASE)
_NOT_TABLES = {"lateral", "unnest", "values", "select"}


# ---------------------------------------------------------------- shared paths and records

def _simple(value, what):
    if not _SIMPLE.fullmatch(value):
        raise SystemExit(f"{what} must be a simple name (letters, digits, '.', '_', '-'): {value!r}")
    return value


def _rel(root, path):
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _package_dir(root, investigation, package):
    return root / "deliveries" / investigation / package


def _read_json(path):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return record


def _write_text(path, text):
    # Atomic, so an interrupted write never leaves a half manifest or rule file.
    path = Path(path)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_json(path, record):
    _write_text(path, json.dumps(record, indent=2) + "\n")


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _print(report):
    print(json.dumps(report))


def _is_unknown(value):
    return isinstance(value, dict) and set(value) == {"unknown"}


def _toml():
    try:
        import tomllib
    except ImportError:  # Python 3.10
        import tomli as tomllib
    return tomllib


_UNUSABLE = f"not {_EVIDENCE_SCHEMA} with result-scoped settings; rerun the result"


def _usable_evidence(record):
    """Evidence this helper reads: awb-evidence/3 whose settings name their result."""
    if not isinstance(record, dict) or record.get("schema") != _EVIDENCE_SCHEMA:
        return False
    return isinstance(record.get("settings"), dict) and bool(record["settings"].get("result"))


def _evidence_files(root, investigation):
    """Yield (path, evidence or None, problem or None) for each awb-evidence file."""
    directory = root / "investigations" / investigation / "evidence"
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            yield path, None, f"{_rel(root, path)}: unreadable ({error})"
            continue
        # Export-check lists and other files can sit beside the evidence.
        schema = record.get("schema") if isinstance(record, dict) else None
        if _usable_evidence(record):
            yield path, record, None
        elif str(schema).startswith("awb-evidence/"):
            yield path, None, f"{_rel(root, path)}: {_UNUSABLE}"


# ---------------------------------------------------------------- Markdown as it renders
#
# Every draft check but numbers reads the narratives (findings.md, methodology.md, and methodology-note.md
# when the draft holds it) through `_view`, one reading of what renders, so a form that hides text from the
# reader hides it from every such check, and a form that shows text shows it to every such check. The
# numbers check reads source lines (`_unfenced`), as the check-draft help text says, outside the fenced code
# and comments this reading drops, so a `<!--` that opens no comment hides nothing from it. The reading covers the
# Markdown subset helpers.md lists. A block form outside it that could hide or move text is refused
# (`markdown_problems`) rather than guessed at, so it never passes.

# One source line as it renders. kind is "text", "heading", "fence" (a code fence's opening line),
# "code" (inside a fence, its closing line included), "hidden" (inside a comment block), or "html" (the
# text after a comment block's end on its line). plain is the rendered text with code spans and
# autolinks kept for the names scan; prose is the same with them blanked, for wording, and spaced is
# prose with markup characters read as word breaks (see `_inline`). Link targets
# are in neither, so a link's text joins the words around it; links lists the targets opened on the
# line. title: a heading's text as it shows, code spans and autolinks unwrapped, so formatting never sets
# two headings apart. group: the paragraph or heading the line belongs to, None for blank, fence, and
# hidden lines. start: the line opens a paragraph. declares: it opens a top-level paragraph at column 0,
# the only place a **Claim strength:** line counts. item: the list depth of the item the line opens (1 at the
# top level), or 0 when the line opens no item. listed: the list depth of the item the line is in, 0 outside
# any list; a paragraph it opens continues an item of that depth (see `_blocks`), and a paragraph opened in a
# block quote outside any list is a block of its own.
_Line = namedtuple("_Line", "number kind level title plain prose spaced links group start declares item listed")

_FENCE = re.compile(r"( {0,3})(`{3,}|~{3,})")
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
_URI = r"[A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*"
_AUTOLINK = re.compile(rf"<({_URI})>")
_TOKEN = re.compile(r"\S+")
_QUOTE = re.compile(r" {0,3}> ?")
_ITEM = re.compile(r"( {0,3})([-*+]|(\d{1,9})[.)])(?=[ \t]|$)( *)(.*)")
_RULE = re.compile(r" {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
_ATX = re.compile(r" {0,3}(#{1,6})(?=[ \t]|$)(.*)")
_UNDERLINE = re.compile(r" {0,3}(?:=+|-+)[ \t]*$")
_COMMENT_OPEN = re.compile(r" {0,3}<!--")
# A link reference or footnote definition renders nothing where it stands.
_DEFINITION = re.compile(r" {0,3}\[[^\]]+\]:")
# HTML blocks as CommonMark starts them: types 1 to 6 interrupt a paragraph; a lone tag (type 7) does not.
_HTML_BLOCK = re.compile(
    r" {0,3}(?:<(?:script|pre|style|textarea)(?:\s|>|$)|<\?|<![A-Za-z]|<!\[CDATA\["
    r"|</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog"
    r"|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe"
    r"|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table"
    r"|tbody|td|tfoot|th|thead|title|tr|track|ul)(?:\s|/?>|$))", re.IGNORECASE)
_HTML_LINE = re.compile(r" {0,3}(?:<[A-Za-z][A-Za-z0-9-]*(?:\s+[A-Za-z_:][\w.:-]*(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'"
                        r"|[^\s\"'=<>`]+))?)*\s*/?>|</[A-Za-z][A-Za-z0-9-]*\s*>)[ \t]*$")
# Inline: a code span that opens first is code. A backslash before a backtick or `<` makes it a literal
# character, opening nothing. Comments and code spans within a paragraph are read by `_inline_spans`.
_SPAN = r"(?<![`\\])(`+)(?!`).+?(?<!`)\1(?!`)"
# An inline HTML tag other than a line break: its attributes can hide the text it wraps.
_INLINE_TAG = re.compile(_SPAN + r"|(?<!\\)<(?!br\s*/?>)/?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>",
                         re.DOTALL | re.IGNORECASE)
# An inline link's or image's target, after the bracket closing its text.
_TARGET = r"\(\s*(<[^<>\n]*>|(?:[^()\s]|\([^()\s]*\))*)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?\s*\)"
# Code spans and autolinks render as themselves; an inline link's target renders as nothing. A reference
# link `[text][label]` never resolves, since every definition is refused, so it renders as written, label
# included (group 4); the claims check's spaced reading also drops the label, as the link would render if
# a definition were added, so a phrase is found either way.
_PIECE = re.compile(
    _SPAN + rf"|(?<!\\)(<{_URI}>)"
    r"|\]" + _TARGET +
    r"|(?<!\\)\]\[([^\]]*)\]",
    re.DOTALL)
# From a backtick: the code span its run opens, or the run alone when no run of its length closes it.
_BACKTICKS = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)|`+", re.DOTALL)
# An email autolink, as CommonMark defines one.
_EMAIL_AUTOLINK = re.compile(r"<[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
                             r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*>")
# An inline target's parts as CommonMark reads them: its `(` and a destination in <>, else the destination's
# escapes, runs, and parentheses, then its optional title and `)`.
_TARGET_OPEN = re.compile(r"\(\s*(<(?:\\.|[^\\<>\n])*>)?")
_DESTINATION_PIECE = re.compile(r"\\[!-/:-@\[-`{-~]|\\|[^\\()\s]+|[()]")
_TITLE_END = re.compile(r"""\s*\)|\s+(?:"(?:\\.|[^\\"])*"|'(?:\\.|[^\\'])*'|\((?:\\.|[^\\()])*\))\s*\)""", re.DOTALL)
_COMMENT_SPAN = re.compile(r"<!--(?:-?>|.*?-->)", re.DOTALL)
# Where an escape, a code span, an autolink, a link's text or target, or a comment may start.
_INLINE_TOKEN = re.compile(r"[\\`<\[\]]")
# What an image shows in place of its text when image_text is off: one character no question holds.
_PICTURE = "\ufffc"
_BREAK_TAG = re.compile(r"(?<!\\)<br\s*/?>", re.IGNORECASE)
_TAG = re.compile(r"(?<!\\)</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
# Emphasis and strikethrough: every `*` and `~` first, then each `_` run not inside a word, as in
# CommonMark, so `r_009` and orders_**view** keep their underscore while `_leads_` renders as leads. An
# escaped marker goes too ("\*leads\* to" shows the phrase with stars around a word, and the phrase is
# what is checked), except an escaped `_` inside a word, which renders as the underscore: orders\_view.
_STARS = re.compile(r"\\?[*~]")
_UNDERSCORES = re.compile(r"(?<![^\W_])(?<![_\\])\\?_+(?!_)|(?<![_\\])\\?_+(?!_)(?![^\W_])")
_BRACKET = re.compile(r"!?\\?\[|\\?\]")
_ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
_HARD_BREAK = re.compile(r"\\(?=\n)")
_INSIDE = "inside a list item or block quote"


def _keep_lines(pattern, text, replacement=""):
    """Replace each match, keeping its line breaks, so a rendered paragraph keeps its source lines."""
    return pattern.sub(lambda match: replacement + "\n" * match.group(0).count("\n"), text)


def _rendered(text, gap=""):
    """Inline text as it renders, each markup character removed or, with gap=" ", read as a word break."""
    text = _keep_lines(_TAG, _keep_lines(_BREAK_TAG, _HARD_BREAK.sub(" ", text), " "), gap)
    # An escaped & starts no character reference: \&#108; shows as written.
    text = _ESCAPE.sub(lambda m: "&amp;" if m[1] == "&" else m[1], _BRACKET.sub(gap, _UNDERSCORES.sub(gap, _STARS.sub(gap, _visible(text)))))
    return "\n".join(unicodedata.normalize("NFKC", _visible(html.unescape(line).replace("\r", " ").replace("\n", " ")))
                     for line in text.split("\n"))


def _visible(text):
    """Text without zero-width characters, which render as nothing, written or as character references."""
    return "".join(c for c in text if unicodedata.category(c) != "Cf")


def _inline(text):
    """Text's rendered inline content, line breaks kept: (plain, prose, spaced, [(line offset, link target)]).

    spaced is prose with each markup character read as a word break rather than as nothing. CommonMark
    leaves an unmatched marker as a visible character, so x*drives shows the word drives; the claims
    check reads both, and a phrase found in either counts.
    """
    plain, prose, spaced, links, last = [], [], [], [], 0
    for match in _PIECE.finditer(text):
        segment, piece = text[last:match.start()], match.group(0)
        plain += [_rendered(segment)]
        prose += [plain[-1]]
        spaced += [_rendered(segment, " ")]
        if match.group(1) or match.group(2):
            plain.append(piece)
            prose.append(re.sub(r"[^\n]", " ", piece))
            spaced.append(prose[-1])
        elif match.group(4) is not None:
            plain.append(" " + _rendered(match.group(4)))
            prose.append(plain[-1])
            spaced.append(" " + "\n" * piece.count("\n"))
        else:
            if match.group(3) is not None:
                links.append((text.count("\n", 0, match.start()), match.group(3).strip("<>")))
            plain.append("\n" * piece.count("\n"))
            prose.append(plain[-1])
            spaced.append(" " + plain[-1])
        last = match.end()
    plain.append(_rendered(text[last:]))
    prose.append(plain[-1])
    spaced.append(_rendered(text[last:], " "))
    return "".join(plain), "".join(prose), "".join(spaced), links


def _literal_end(text, index):
    """Where the escape, code span, or autolink starting at text[index] ends, or None. Read left to right, as
    CommonMark reads them, so the backtick after an escaped backslash or backtick may open a code span; a
    bracket or `!` inside any of them is a character, opening and closing nothing."""
    if text[index] == "\\":
        return index + 2
    if text[index] == "`":
        return _BACKTICKS.match(text, index).end()
    link = (_AUTOLINK.match(text, index) or _EMAIL_AUTOLINK.match(text, index)) if text[index] == "<" else None
    return link.end() if link else None


def _target_end(text, index):
    """The end of the inline target opening with the `(` at text[index], or None: a destination in <>, or with
    its parentheses balanced to any depth, escapes read first, then an optional title, as CommonMark reads one."""
    opened = _TARGET_OPEN.match(text, index)
    if not opened:
        return None
    at, depth = opened.end(), 0
    if opened.group(1) is None:
        while (piece := _DESTINATION_PIECE.match(text, at)) and (depth or piece[0] != ")"):
            depth += {"(": 1, ")": -1}.get(piece[0], 0)
            at = piece.end()
    end = _TITLE_END.match(text, at) if not depth else None
    return end.end() if end else None


def _inline_spans(text):
    """A paragraph's comments and code spans, each as (start, end) in its text, and where a `<!--` opens a
    comment never closed, or None.

    Read left to right across the whole paragraph, as CommonMark reads them: a `<!--` in an escape, a code span,
    an autolink, or a link's or image's target is a character, opening no comment, so it hides nothing, and a
    code span wrapped across lines pairs its own backticks only.
    """
    comments, code, openers, index = [], [], 0, 0
    while found := _INLINE_TOKEN.search(text, index):
        index = found.start()
        if text[index] == "`":
            run = _BACKTICKS.match(text, index)
            if run.group(1):
                code.append(run.span())
            index = run.end()
        elif (end := _literal_end(text, index)) is not None:
            index = end
        elif text[index] == "[":
            openers, index = openers + 1, index + 1
        elif text[index] == "]" and openers:  # a target follows only a ] that closes a [
            openers, index = openers - 1, _target_end(text, index + 1) or index + 1
        elif text.startswith("<!--", index):
            if not (comment := _COMMENT_SPAN.match(text, index)):
                return comments, code, index
            comments.append(comment.span())
            index = comment.end()
        else:
            index += 1
    return comments, code, None


def _code_spans(text):
    """The code spans in text as (start, end), read as `_literal_end` reads them, so an escaped backtick opens
    and closes none."""
    spans, index = [], 0
    while found := _INLINE_TOKEN.search(text, index):
        index = found.start()
        if text[index] == "`":
            run = _BACKTICKS.match(text, index)
            if run.group(1):
                spans.append(run.span())
            index = run.end()
        else:
            end = _literal_end(text, index)
            index = end if end is not None else index + 1
    return spans


def _pictured(text):
    """Inline text with each image's text read as the picture it shows, `_PICTURE`, line breaks kept. Its `![`
    and target stay, for `_inline` to drop as it drops a link's. Image text shows only when the image fails
    to load, or to a screen reader.

    One pass pairs each `]` with the `[` it closes, as nesting does; an image is a `[` right after an
    unescaped `!` whose `]` an inline target follows, and an image inside it goes with it."""
    images, openers, bang, index = {}, [], None, 0
    while index < len(text):
        if (end := _literal_end(text, index)) is not None:
            index = end
            continue
        if text[index] == "[":
            openers.append((index, bang == index - 1))
        elif text[index] == "]" and openers:
            opened, image = openers.pop()
            if end := _target_end(text, index + 1):
                if image:
                    images[opened] = index
                index = end
                continue
        elif text[index] == "!":
            bang = index
        index += 1
    pieces, last = [], 0
    for opened, closed in sorted(images.items()):
        if opened > last:
            pieces.append(text[last:opened + 1] + _PICTURE + "\n" * text.count("\n", opened + 1, closed))
            last = closed
    return "".join(pieces) + text[last:]


def _shown(plain):
    """plain text as it shows: a code span's content without its backticks, an autolink without its brackets."""
    return _AUTOLINK.sub(r"\1", _CODE_SPAN.sub(lambda match: match[2], plain))


def _collapse(text):
    return " ".join(text.split())


def _indent(text):
    return len(text) - len(text.lstrip(" "))


def _source_column(line, column):
    """The index in `line` of the character at `column` of line.expandtabs(4), or len(line) past its end."""
    width = 0
    for index, char in enumerate(line):
        width += 4 - width % 4 if char == "\t" else 1
        if width > column:
            return index
    return len(line)


def _opens_fence(text):
    marker = _FENCE.match(text)
    return marker if marker and not (marker[2][0] == "`" and "`" in text[marker.end():]) else None


def _item_width(text, interrupting):
    """The content indent of a list item `text` opens, or None. Interrupting a paragraph, a bullet needs
    content and a numbered item must be 1, as in CommonMark."""
    item = _ITEM.match(text)
    if not item or _RULE.match(text) or interrupting and (not item[5] or item[3] and int(item[3]) != 1):
        return None
    marker = len(item[1]) + len(item[2])
    return marker + 1 if not item[5] or len(item[4]) > 4 else marker + len(item[4])


def _interrupts(text, paragraph=True):
    """Whether `text` starts a block that ends an open paragraph. A paragraph left in a container the line
    does not continue (paragraph=False) is ended by any list item, as a sibling item ends the one before."""
    return bool(_ATX.match(text) or _COMMENT_OPEN.match(text) or _HTML_BLOCK.match(text) or _QUOTE.match(text)
                or _RULE.match(text) or _opens_fence(text) or _item_width(text, paragraph) is not None)


def _view(text, *, image_text=True):
    """Markdown as it renders: one _Line per source line, the refused forms as (line, problem), the comments it
    drops, and its code spans, each as (start, end) offsets in text, in order.

    image_text=False reads each image as the picture it shows (`_pictured`), never its text.
    """
    rows, forms, refused, comments, code = [], [], set(), [], []
    stack = []          # open containers, outermost first: None for a block quote, else [content indent, empty]
    fence = comment = None  # comment: (line number, offset in text) of an open comment block
    para = False        # the previous line is paragraph text, which the next may continue
    group = 0
    sources, starts = text.splitlines(), [0]
    for source in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(source))

    def position(number, column):
        """The offset in text of a column of line `number` as its tabs expand."""
        return starts[number - 1] + _source_column(sources[number - 1], column)

    def place(joined, indexes, at):
        """The offset in text of offset `at` in a paragraph's leaves, `joined` by line breaks from rows `indexes`."""
        entry = rows[indexes[joined.count("\n", 0, at)]]
        return position(entry["number"], entry["at"] + at - joined.rfind("\n", 0, at) - 1)

    def refuse(number, what, how):
        if number not in refused:
            refused.add(number)
            forms.append((number, f"unsupported Markdown: {what} at line {number}; rewrite as {how}"))

    # at: the column of the expanded line where leaf starts. A leaf is the end of its line but for a heading's,
    # which passes its own.
    def row(number, kind, leaf="", **fields):
        rows.append({"number": number, "kind": kind, "leaf": leaf, "level": 0, "title": None, "group": None,
                     "start": False, "inside": False, "indent": 0, "item": 0, "listed": 0,
                     "at": len(line) - len(leaf), **fields})

    for number, source in enumerate(sources, start=1):
        line = source.expandtabs(4)
        if comment is not None:
            end = line.find("-->")
            if end < 0:
                row(number, "hidden")
                continue
            comments.append((comment[1], position(number, end + 3)))
            comment, group = None, group + 1
            row(number, "html", line[end + 3:], group=group, start=True)
            para = False
            continue
        if fence is not None:
            marker = _FENCE.match(line)
            if (marker and marker[2][0] == fence[0][0] and len(marker[2]) >= len(fence[0])
                    and not line[marker.end():].strip()):
                fence = None
            row(number, "code")
            continue

        rest, matched = line, 0
        for container in stack:
            if container is None:
                quote = _QUOTE.match(rest)
                if not quote:
                    break
                rest = rest[quote.end():]
            elif not rest.strip():
                if container[1]:  # an item opened empty ends at a blank line, as in CommonMark
                    break
                rest = ""
            elif _indent(rest) >= container[0]:
                rest, container[1] = rest[container[0]:], False
            else:
                break
            matched += 1
        lazy = matched < len(stack) and para and bool(rest.strip()) and not _interrupts(rest, False)
        if matched < len(stack) and not lazy:
            del stack[matched:]
            para = False
        item = 0
        while not lazy:
            if quote := _QUOTE.match(rest):
                stack.append(None)
                rest = rest[quote.end():]
            elif (width := _item_width(rest, para)) is not None:
                stack.append([width, not rest[width:].strip()])
                rest = rest[width:]
                item = item or sum(container is not None for container in stack)
            else:
                break
            para = False
        inside, indent = bool(stack), _indent(rest)
        listed = sum(container is not None for container in stack)

        if not rest.strip():
            row(number, "text")
            para = False
        elif para and not lazy and _UNDERLINE.match(rest):
            refuse(number, "text underlined with = or -, which renders as a heading",
                   "a # heading, or leave a blank line before a rule")
            row(number, "text", rest, group=group, inside=inside)
            para = False
        elif lazy or para and not _interrupts(rest):
            row(number, "text", rest, group=group, inside=inside)
        elif indent >= 4 and not para:
            refuse(number, "text indented four or more spaces, which renders as code",
                   "a fenced code block starting at the beginning of its line, or remove the indent")
            group += 1
            row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            para = True
        elif marker := _opens_fence(rest):
            if inside or indent:
                refuse(number, f"a code fence {_INSIDE if inside else 'indented from the start of its line'}",
                       "a fence at the start of its line, outside lists and quotes")
                group += 1
                row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            else:
                fence = (marker[2], number)
                row(number, "fence", line)
            para = False
        elif _COMMENT_OPEN.match(rest):
            group += 1
            if inside or indent:
                refuse(number, f"a comment {_INSIDE if inside else 'indented from the start of its line'}",
                       "a comment at the start of its line, outside lists and quotes")
                row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            elif (end := rest.find("-->", 2)) < 0:
                comment = (number, position(number, len(line) - len(rest)))
                row(number, "hidden")
            else:
                comments.append((position(number, len(line) - len(rest)),
                                 position(number, len(line) - len(rest) + end + 3)))
                row(number, "html", rest[end + 3:], group=group, start=True)
            para = False
        elif _HTML_BLOCK.match(rest) or _HTML_LINE.match(rest):
            refuse(number, "an HTML block", "Markdown text")
            group += 1
            row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            para = True
        elif not para and _DEFINITION.match(rest):
            refuse(number, "a link reference or footnote definition", "an inline link, or text where it is cited")
            group += 1
            row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            para = True
        elif heading := _ATX.match(rest):
            group += 1
            if inside:
                refuse(number, f"a heading {_INSIDE}", "a heading at the start of its own line, outside lists and quotes")
                row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            else:
                row(number, "heading", re.sub(r"(?:^|[ \t])#+[ \t]*$", "", heading[2]), group=group,
                    level=len(heading[1]), at=len(line) - len(rest) + heading.start(2))
            para = False
        elif _RULE.match(rest):
            row(number, "text")
            para = False
        else:
            group += 1
            row(number, "text", rest, group=group, start=True, inside=inside, indent=indent)
            para = True
        rows[-1].update(item=item, listed=listed)
    if fence is not None:
        refuse(fence[1], "a code fence never closed", "a fence closed by a matching fence line")
    if comment is not None:
        refuse(comment[0], "a comment never closed", "a comment closed with -->, or delete it")
        comments.append((comment[1], len(text)))  # hides every line after it

    paragraphs = {}
    for index, entry in enumerate(rows):
        entry.update(plain=entry["leaf"] if entry["kind"] == "fence" else "", prose="", spaced="", links=[])
        if entry["group"] is not None:
            paragraphs.setdefault(entry["group"], []).append(index)
    for indexes in paragraphs.values():
        joined = "\n".join(rows[i]["leaf"] for i in indexes)
        spans, code_spans, unclosed = _inline_spans(joined)
        if unclosed is not None:
            refuse(rows[indexes[joined.count("\n", 0, unclosed)]]["number"], "a comment never closed",
                   "a comment closed with --> in the same paragraph, or delete it")
        comments += [(place(joined, indexes, start), place(joined, indexes, end)) for start, end in spans]
        code += [(place(joined, indexes, start), place(joined, indexes, end)) for start, end in code_spans]
        for start, end in reversed(spans):
            joined = joined[:start] + "\n" * joined.count("\n", start, end) + joined[end:]
        found = next((m for m in _INLINE_TAG.finditer(joined) if not m.group(1)), None)
        if found:
            refuse(rows[indexes[joined.count("\n", 0, found.start())]]["number"], "an inline HTML tag",
                   "Markdown emphasis or plain text")
        plain, prose, spaced, links = _inline(joined if image_text else _pictured(joined))
        for offset, (i, *texts) in enumerate(zip(indexes, *(text.split("\n") for text in (plain, prose, spaced)))):
            rows[i].update(zip(("plain", "prose", "spaced"), texts), links=[t for o, t in links if o == offset])

    view = []
    for entry in rows:
        declares = entry["start"] and not entry["inside"] and not entry["indent"] and entry["kind"] == "text"
        if entry["kind"] in ("text", "html") and entry["plain"].lstrip().startswith("Claim strength:") and not declares:
            where = (_INSIDE if entry["inside"] else "indented from the start of its line" if entry["indent"]
                     else "after a comment on its line" if entry["kind"] == "html" else "inside a paragraph")
            refuse(entry["number"], f"a **Claim strength:** line {where}",
                   "a line opening a top-level paragraph at the start of its line, outside lists and quotes")
        view.append(_Line(entry["number"], entry["kind"], entry["level"],
                          _collapse(_shown(entry["plain"])) if entry["kind"] == "heading" else None, entry["plain"],
                          entry["prose"], entry["spaced"], entry["links"], entry["group"], entry["start"], declares,
                          entry["item"], entry["listed"]))
    return view, sorted(forms), sorted(comments), sorted(code)


# ---------------------------------------------------------------- internal names in findings.md

# Wrapping punctuation and Markdown emphasis around a token; leading dots stay so `./x` is a path.
# Underscores are stripped only in matching pairs (`_word_`), so `__init__.py` keeps its own.
_LEADING = "([{<\"'*~!“‘"
_TRAILING = ")]}>\"'*~.,;:!?”’"
_POSSESSIVE = re.compile(r"['’]s$")

# A leading slash alone is no path signal: "/ " and "/month" are prose; /usr/local has two slashes.
_PATH_PREFIX = re.compile(r"^(?:\.{1,2}/|[A-Za-z][A-Za-z0-9+.-]*://)")
_PATH_ROOTS = {"data", "foundation", "investigations", "deliveries", "src", "views",
               "queries", "results", "evidence", "exploration", "scans"}
_FRACTION = re.compile(r"[\d.,]+(?:/[\d.,]+)+")  # 3/4, 6/30/2026: numbers, not paths
_FILE_NAME = re.compile(
    r"\.(?:md|py|csv|parquet|json|sql|png|svg|duckdb|db|xlsx|yaml|yml|toml|txt|ipynb)$",
    re.IGNORECASE,
)
_SNAKE = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+")
# Segments of two or more characters, so abbreviations such as e.g. and U.S. stay clean.
_DOTTED = re.compile(r"(?<![\w.])[A-Za-z_]\w+(?:\.[A-Za-z_]\w+)+")
_HEX = re.compile(r"[0-9a-fA-F]{7,40}")


def _blank(text, start, end):
    return text[:start] + " " * (end - start) + text[end:]


def _unwrap(token):
    token = _POSSESSIVE.sub("", token.lstrip(_LEADING).rstrip(_TRAILING)).rstrip(_TRAILING)
    pairs = min(len(token) - len(token.lstrip("_")), len(token) - len(token.rstrip("_")))
    if pairs:
        token = _unwrap(token[pairs:-pairs]) if 2 * pairs < len(token) else ""
    return token


def _token_kind(token, roots):
    if "/" in token and re.search(r"\w", token):
        segments = token.split("/")
        if _PATH_PREFIX.match(token) or not _FRACTION.fullmatch(token) and (
                len(segments) >= 3 or segments[0] in _PATH_ROOTS
                or any(_FILE_NAME.search(segment) or "_" in segment or segment in roots for segment in segments)):
            return "path"
    if _FILE_NAME.search(token):
        return "file"
    if _SNAKE.search(token) or _DOTTED.search(token):
        return "identifier"
    if _HEX.fullmatch(token) and re.search(r"\d", token) and re.search(r"[a-fA-F]", token):
        return "sha"
    return None


def _name_pattern(names):
    names = sorted({name for name in names if name}, key=len, reverse=True)
    if not names:
        return None
    # Whole token: not glued to word characters, hyphens, slashes, or a dotted continuation.
    return re.compile(
        r"(?<![\w./-])(?:" + "|".join(map(re.escape, names)) + r")(?![\w/-]|\.\w)"
    )


def _scan_paragraph(lines, roots, pattern):
    """Scan one paragraph's lines. A code span is found in the joined paragraph, since it can cross a line
    break, and reported at its opening line with each line break read as a space, as it renders."""
    joined = "\n".join(line.plain for line in lines)
    spans = []
    for match in _CODE_SPAN.finditer(joined):
        start = joined.rfind("\n", 0, match.start()) + 1
        spans.append((joined.count("\n", 0, match.start()), match.start() - start, match.group(0).replace("\n", " ")))
    joined = _keep_lines(_CODE_SPAN, joined, " ")
    rows = []
    for offset, (line, text) in enumerate(zip(lines, joined.split("\n"))):
        code = [(column, "code", span) for at, column, span in spans if at == offset]
        rows.extend(_scan_line(line.number, text, roots, pattern, code))
    return rows


def _scan_line(number, line, roots, pattern, found):
    """Scan one line whose code spans are already blanked and listed in `found` as (column, "code", text)."""
    found = list(found)
    taken = []
    if pattern is not None:
        for match in pattern.finditer(line):
            found.append((match.start(), "name", match.group(0)))
            taken.append((match.start(), match.end()))

    for match in _TOKEN.finditer(line):
        token = _unwrap(match.group(0))
        start = match.start() + match.group(0).find(token)
        end = start + len(token)
        if not token or any(start < stop and begin < end for begin, stop in taken):
            continue
        kind = _token_kind(token, roots)
        if kind:
            found.append((start, kind, token))

    return [{"line": number, "kind": kind, "text": text} for _, kind, text in sorted(found)]


# The line breaks str.splitlines() sees.
_LINE_BREAK = re.compile("\r\n|[\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]")
_NOT_LINE_BREAK = re.compile("[^\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]")


def _unfenced(path):
    """Yield (line number, line, opens a fence) for each source line outside fenced code, comments blanked."""
    for number, line, opens, _ in _source_lines(path):
        yield number, line, opens


def _source_lines(path):
    """Yield (line number, line, opens a fence, bare) for each source line outside fenced code, comments blanked;
    bare is the line with its code spans blanked too, keeping its length, so the two share every column.

    The numbers check reads source lines, not the rendered view, but drops only the fenced code and comments
    `_view` drops, so a `<!--` in a code span, fenced code, or a link's target, or escaped, opens no comment here
    either. It decides line wraps and list markers and matches allowed texts on the line, which keeps its code
    spans as written, and reads numbers from bare: code spans are `_view`'s, paired across the whole paragraph,
    so a backtick a span on an earlier line closed is never paired again within a line and the lines around it.
    """
    text = Path(path).read_text(encoding="utf-8")
    view, _, comments, code = _view(text)
    # A blanked comment is one space and a newline for each line break it held, so line numbers match `_view`'s;
    # a comment ending the file can leave its last line empty, which str.splitlines() then leaves out. A blanked
    # code span keeps its line breaks and its length.
    kept, bare, last = [], [], 0
    for start, end, comment in sorted([(*span, True) for span in comments] + [(*span, False) for span in code]):
        blank = " " + "\n" * len(_LINE_BREAK.findall(text, start, end)) if comment else None
        kept += [text[last:start], blank or text[start:end]]
        bare += [text[last:start], blank or _NOT_LINE_BREAK.sub(" ", text[start:end])]
        last = end
    kept, bare = ("".join(pieces + [text[last:]]).splitlines() for pieces in (kept, bare))
    kept += [""] * (len(view) - len(kept))
    bare += [""] * (len(view) - len(bare))
    for line, source, blanked in zip(view, kept, bare):
        if line.kind != "code":
            yield line.number, source, line.kind == "fence", blanked


def check_findings(path: str | os.PathLike, *, names=(), roots=()) -> list[dict]:
    """List code, paths, file names, identifiers, SHAs, and given names, by line then column.

    A slash token with any of `names` or `roots` as a segment is a path; `roots` may be plain words,
    which never match alone.
    """
    pattern = _name_pattern(names)
    roots = set(names) | set(roots)
    rows, paragraphs = [], {}
    for line in _read_view(path)[0]:
        if line.kind == "fence":
            rows.append({"line": line.number, "kind": "code", "text": line.plain.strip()})
        elif line.group is not None:
            paragraphs.setdefault(line.group, []).append(line)
    for lines in paragraphs.values():
        rows.extend(_scan_paragraph(lines, roots, pattern))
    return sorted(rows, key=lambda row: row["line"])


# ---------------------------------------------------------------- the names set

def _sql_names(text):
    text = _SQL_NOISE.sub("''", text)
    ctes = {_unquote(name) for name in _CTE.findall(text)}
    names = set()
    for name in _CREATE.findall(text) + [
            source for source in _SOURCE.findall(text)
            if _unquote(source) not in ctes and _unquote(source).lower() not in _NOT_TABLES]:
        name = _unquote(name)
        names.update({name, name.rsplit(".", 1)[-1]})
    return names


def _unquote(name):
    return ".".join(part.strip().strip('"') for part in name.split("."))


def _keys(value, prefix=""):
    names = set()
    if isinstance(value, dict) and not _is_unknown(value):
        for key, item in value.items():
            # A nested key alone is often a plain word ("start"); only its dotted path is a name.
            dotted = f"{prefix}.{key}" if prefix else str(key)
            names.update({dotted}, _keys(item, dotted))
    elif isinstance(value, list):
        for item in value:
            names.update(_keys(item, prefix))
    return names


def _toml_keys(text):
    try:
        return _keys(_toml().loads(text))
    except ImportError:  # Python 3.10 without tomli: table headers and key lines are enough for names.
        names = set()
        for header in re.findall(r"^\s*\[\[?\s*([^\]]+?)\s*\]\]?", text, re.MULTILINE):
            parts = [part.strip().strip("\"'") for part in header.split(".")]
            names.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
        for key in re.findall(r"^\s*([A-Za-z0-9_\-\"'.]+)\s*=", text, re.MULTILINE):
            names.add(".".join(part.strip("\"'") for part in key.split(".")))
        return names


def project_names(root, investigation, package):
    """Return the findings-check names the project records, and problems that leave it incomplete."""
    names, problems = _recorded_names(root, investigation, package)
    return sorted(name for name in names if not _PLAIN_WORD.fullmatch(name)), problems


def _recorded_names(root, investigation, package):
    """Every recorded name, plain words included, and the problems that leave the set incomplete."""
    root = Path(root)
    names, problems = {investigation, package}, []
    view_files = set((root / "foundation/views").rglob("*.sql")) if (root / "foundation/views").is_dir() else set()
    settings_files = {root / "investigations" / investigation / "settings.toml"}
    settings_found = False

    for path, evidence, problem in _evidence_files(root, investigation):
        if problem:
            problems.append(problem)
            continue
        names.update({path.stem, str(evidence.get("result_id") or path.stem)})
        views = evidence.get("views")
        for entry in views if isinstance(views, list) else []:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                view_files.add(root / entry["path"])
        settings = evidence.get("settings")
        if isinstance(settings, dict) and not _is_unknown(settings):
            if isinstance(settings.get("path"), str):
                settings_files.add(root / settings["path"])
            if isinstance(settings.get("content"), dict) and not _is_unknown(settings["content"]):
                names.update(_keys(settings["content"]))
                settings_found = True

    for record in ("brief.md", "state.md", "history.md"):
        try:
            names.update(_EVIDENCE_LINK.findall(
                (root / "investigations" / investigation / record).read_text(encoding="utf-8")))
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError) as error:
            problems.append(f"investigations/{investigation}/{record}: unreadable ({error})")

    for path in sorted(view_files):
        try:
            names.update(_sql_names(path.read_text(encoding="utf-8")))
        except FileNotFoundError:
            pass  # A view cited by old evidence and since removed has nothing left to read.
        except (OSError, UnicodeError) as error:
            problems.append(f"{_rel(root, path)}: unreadable ({error})")

    for path in sorted(settings_files):
        if not path.is_file():
            continue
        settings_found = True
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".toml":
                names.update(_toml_keys(text))
            elif path.suffix == ".json":
                names.update(_keys(json.loads(text)))
            else:
                problems.append(f"{_rel(root, path)}: only TOML and JSON settings are read; "
                                "add its keys by hand")
        except (OSError, UnicodeError, ValueError) as error:
            problems.append(f"{_rel(root, path)}: unparsed ({error})")
    if not settings_found:
        problems.append(f"no settings found: investigations/{investigation}/settings.toml is absent "
                        "and no evidence records a settings file")
    return {name for name in names if name}, problems


# ---------------------------------------------------------------- flags and headings

def _cells(line):
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", text)]


def _section_table(text, title):
    """Return (header, rows) of the table under `## <title>`, or None when there is none."""
    match = re.search(rf"^## {re.escape(title)}\s*$", text, re.MULTILINE)
    if not match:
        return None
    body = re.split(r"^##? ", text[match.end():], maxsplit=1, flags=re.MULTILINE)[0]
    lines = [line for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return None
    header = _cells(lines[0])
    return header, [dict(zip(header, _cells(line))) for line in lines[2:]]


def state_flags(root, investigation) -> list[dict]:
    """Return each finding state.md flags as {finding, reason}; raise ValueError when unreadable."""
    path = Path(root) / "investigations" / investigation / "state.md"
    try:
        table = _section_table(path.read_text(encoding="utf-8"), "Current findings")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"investigations/{investigation}/state.md: unreadable ({error})") from error
    if table is None or not {"Finding", "Status", _REASON} <= set(table[0]):
        raise ValueError(f"investigations/{investigation}/state.md has no Current findings table with "
                         f"Finding, Status, and {_REASON} columns; flags cannot be compared")
    # The status collector's rule: a flagged finding's Status begins with revalidation-needed.
    return [{"finding": row.get("Finding", ""), "reason": row.get(_REASON, "")}
            for row in table[1] if row.get("Status", "").startswith("revalidation-needed")]


def unmatched_flags(record: dict, flags: list[dict]) -> list[dict]:
    """List each current flag whose exact finding and reason no revalidation_flags entry records."""
    recorded = record.get("revalidation_flags")
    recorded = {_flag_key(f) for f in recorded} if isinstance(recorded, list) else set()
    return [flag for flag in flags if (flag["finding"], flag["reason"]) not in recorded]


def _flag_key(entry):
    """An entry's (finding, reason), or None when either is not text, so a malformed entry matches nothing."""
    if isinstance(entry, dict) and isinstance(entry.get("finding"), str) and isinstance(entry.get("reason"), str):
        return entry["finding"], entry["reason"]
    return None


def sync_flags(recorded, flags: list[dict]):
    """Return revalidation_flags for the current flags: an exact-match entry kept, others fresh, none when empty."""
    prior = recorded if isinstance(recorded, list) else []
    kept = {_flag_key(e): e for e in prior if _flag_key(e)}
    # A fresh entry copies state.md verbatim; the agent fills represented_in and the user's disposition.
    entries = [kept.get((flag["finding"], flag["reason"]))
               or {"finding": flag["finding"], "reason": flag["reason"], "represented_in": [], "disposition": "none"}
               for flag in flags]
    return entries or "none"


def pending_flags(recorded) -> list[dict]:
    """List each entry still needing its places ([]) or, once represented, the user's disposition."""
    pending = []
    for entry in recorded if isinstance(recorded, list) else []:
        if not isinstance(entry, dict):
            continue
        places = entry.get("represented_in")
        if places == []:
            pending.append({"finding": entry.get("finding"), "needs": "represented_in"})
        elif isinstance(places, list) and entry.get("disposition") in (None, "none"):
            pending.append({"finding": entry.get("finding"), "needs": "disposition"})
    return pending


def flag_entry_problems(record: dict) -> list[dict]:
    """List each malformed revalidation_flags value or entry; dispositions are judged at release."""
    if "revalidation_flags" not in record:
        return [{"finding": None, "problem": "revalidation_flags is missing; rerun export"}]
    flags = record["revalidation_flags"]
    if flags == "none":
        return []
    if not isinstance(flags, list):
        return [{"finding": None, "problem": "revalidation_flags is not none or a list; rerun export"}]
    problems = []
    for entry in flags:
        if not (isinstance(entry, dict) and isinstance(entry.get("finding"), str)
                and isinstance(entry.get("reason"), str)):
            finding = entry.get("finding") if isinstance(entry, dict) else None
            problems.append({"finding": finding if isinstance(finding, str) else None,
                             "problem": "entry is not an object with a text finding and reason; rerun export"})
            continue
        places, disposition = entry.get("represented_in"), entry.get("disposition")
        if places == "none":
            continue
        if not isinstance(places, list) or not places or not all(
                isinstance(place, str) and place.strip() for place in places):
            problems.append({"finding": entry["finding"],
                             "problem": "represented_in is not none or a list of places; list them or record none"})
        elif disposition not in ("none", "revalidate", *_DISPOSITIONS):
            problems.append({"finding": entry["finding"],
                             "problem": f"unknown disposition {disposition!r}; record none, revalidate, omit, "
                                        "or release_with_caveat"})
    return problems


def _read_view(path, **options):
    return _view(Path(path).read_text(encoding="utf-8"), **options)


def _regions(view):
    """Split a view into [level, title, first line number, lines] at level 1 to 3 headings.

    Level 0 is the text before the first heading; every other region's lines open with its heading
    line, so a slide's headline is read with its body.
    """
    regions = [[0, None, 1, []]]
    for line in view:
        if 1 <= line.level <= 3:
            regions.append([line.level, line.title, line.number, []])
        regions[-1][3].append(line)
    return regions


def question_problems(draft, record: dict) -> list[dict]:
    """List each manifest `results` entry whose question methodology.md does not repeat verbatim.

    methodology.md is read as it renders (`_view`): each paragraph or heading's text as it shows, code spans
    unwrapped and whitespace collapsed, so a wrapped or formatted question matches and one in a comment or
    fenced code does not. An image shows a picture, not its text, so a question only in an image's text does
    not match either, though the other checks read that text. The question matches as written or rendered the
    same way, and must fall within one block: as written, so a code span showing it exactly counts though it
    holds a markup character.
    """
    blocks = {}
    for line in _read_view(Path(draft) / "methodology.md", image_text=False)[0]:
        if line.group is not None:
            blocks.setdefault(line.group, []).append(line.plain)
    shown = [_collapse(_shown("\n".join(lines))) for lines in blocks.values()]
    entries = record.get("results")
    if not isinstance(entries, list):
        return [{"result_id": None, "problem": "the manifest records no results list; run export"}]
    problems = []
    for entry in entries:
        result_id = entry.get("result_id") if isinstance(entry, dict) else None
        question = entry.get("question") if isinstance(entry, dict) else None
        if not isinstance(question, str) or not question.strip():
            problems.append({"result_id": result_id, "problem": "the manifest records no question for this "
                             "result; run export, or copy its question from settings into a hand-added entry"})
            continue
        # As written, or rendered as methodology.md is, so a question in a code span keeps its markup characters.
        forms = [form for form in (_collapse(question), _collapse(_shown(_inline(question)[0]))) if form]
        if not any(form in block for block in shown for form in forms):
            problems.append({"result_id": result_id, "question": question,
                             "problem": "methodology.md does not repeat this question verbatim in text that "
                                        "renders, within one paragraph or heading"})
    return problems


def _named(level, heading, section):
    """Whether a findings.md region is a slide the template names, such as How we know: a ## slide, or a
    ### one under ## Appendix headed with a template slide's name. Any other ### region is a finding."""
    return level == 2 or (level == 3 and section == _APPENDIX_SECTION and heading in _SECTIONS)


def _finding_headings(view):
    section, headings = None, []
    for line in view:
        if line.level == 2:
            section = line.title
        elif line.level == 3 and not _named(3, line.title, section):
            headings.append(line.title)
    return headings


def heading_problems(draft) -> list[dict]:
    """List each `###` finding heading in findings.md that not exactly one methodology.md section repeats,
    or that findings.md repeats. A template slide under ## Appendix, such as ### How we know, is no finding."""
    draft = Path(draft)
    findings = Counter(_finding_headings(_read_view(draft / "findings.md")[0]))
    methodology = Counter(line.title for line in _read_view(draft / "methodology.md")[0] if line.level == 3)
    rows = []
    for heading, count in findings.items():
        if count > 1:
            rows.append({"heading": heading, "problem": f"findings.md has {count} ### slides with this heading; "
                                                        "give each finding its own"})
        if heading not in methodology:
            rows.append({"heading": heading, "problem": "methodology.md has no ### section with this exact heading"})
        elif methodology[heading] > 1:
            rows.append({"heading": heading, "problem": f"methodology.md has {methodology[heading]} ### sections "
                                                        "with this exact heading; merge them into one"})
    return rows


def _narratives(draft):
    """The narrative files the checks read: findings.md, methodology.md, and the note when the draft holds it.

    Only an absent note is left out: a directory or a dangling link at its path is read, and fails as
    unreadable, rather than being skipped."""
    note = Path(draft) / METHODOLOGY_NOTE
    return NARRATIVES + ((METHODOLOGY_NOTE,) if note.exists() or note.is_symlink() else ())


def markdown_problems(draft) -> list[dict]:
    """List each block form in a narrative (`_narratives`) outside the Markdown subset the checks read."""
    draft = Path(draft)
    return [{"file": name, "line": number, "problem": problem}
            for name in _narratives(draft) for number, problem in _read_view(draft / name)[1]]


# ---------------------------------------------------------------- claim strength

# Claim strengths, weakest first, as state.md's Claim column renders them; the project's provenance
# helper owns the values. Only causal wording is checked: it exceeds descriptive and association.
_CLAIMS = ("descriptive", "association", "causal")
_CLAIM_CELL = re.compile(r"(descriptive|association)|(causal) \((?:experiment|natural experiment): \S.*\)")
# Read from rendered text, so emphasis is gone, on a line that opens a top-level paragraph at column 0.
_CLAIM_LINE = re.compile(r"Claim strength:(.*)")
# Causal wording as whole words, so "data-driven" or "causality" is not one. Bare "because" and
# "cause" are left out: they also give reasons for analytical choices and state disclaimers. So are
# "result(s) in" and "affect": "Results in the North", "the result in June", and "affected stores"
# are not claims.
_CAUSAL = re.compile(r"(?<![\w-])(?:" + "|".join([
    r"driv(?:e|es|en|ing)", r"drove", r"drivers?\s+of",
    r"caus(?:es|ed|ing)", r"because\s+of", r"due\s+to",
    r"lead(?:s|ing)?\s+to", r"led\s+to", r"result(?:ed|ing)\s+in", r"as\s+a\s+result\s+of",
    r"impact(?:s|ed|ing)?", r"effects?\s+(?:of|on)", r"attributable\s+to", r"contribut(?:e|es|ed|ing)\s+to",
]) + r")(?![\w-])", re.IGNORECASE)
# Slides that describe method, data, and caveats rather than state findings.
_UNCHECKED = {"How we know", "Limitations and open caveats", "Open questions", "What changed since the last version",
              "Supporting datasets"}


def _level(cell):
    match = _CLAIM_CELL.fullmatch(cell) if isinstance(cell, str) else None
    return (match[1] or match[2]) if match else None


def _claim_text(value):
    """A rendered Claim value for comparison: whitespace collapsed, a code span around it all unwrapped."""
    value = _collapse(value)
    span = _CODE_SPAN.fullmatch(value)
    return _collapse(span[2]) if span else value


def state_claims(root, investigation) -> dict:
    """Map each result state.md's findings table links to its Claim cell, or None when unrecognized."""
    path = Path(root) / "investigations" / investigation / "state.md"
    try:
        table = _section_table(path.read_text(encoding="utf-8"), "Current findings")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"investigations/{investigation}/state.md: unreadable ({error})") from error
    if table is None or not {"Evidence", "Claim"} <= set(table[0]):
        raise ValueError(f"investigations/{investigation}/state.md has no Current findings table with "
                         "Evidence and Claim columns")
    claims = {}
    for row in table[1]:
        cell = row.get("Claim", "")
        for result_id in _EVIDENCE_LINK.findall(row.get("Evidence", "")):
            claims[result_id] = cell if _level(cell) else None
    return claims


def _cited(text, represented):
    """The represented results a methodology section names by ID or evidence link."""
    pattern = _name_pattern(represented)
    found = set(_EVIDENCE_LINK.findall(text)) | set(pattern.findall(text) if pattern else ())
    return [r for r in represented if r in found]


def _weakest(results, levels):
    known = [levels[r] for r in results if levels.get(r)]
    return min(known, key=_CLAIMS.index) if known else _CLAIMS[0]


def _declaration_problem(section, cited, ceiling, claims):
    """Why a finding's methodology section does not state its claim as state.md records it, or None."""
    if section is None:
        return "methodology.md has no ### section with this heading, so no **Claim strength:** line"
    declared = section["declared"]
    if not declared:
        return "methodology.md's section has no **Claim strength:** line opening a top-level paragraph"
    if len(declared) > 1:
        return f"methodology.md's section has {len(declared)} **Claim strength:** lines"
    level = _level(declared[0])
    if not level:
        return ("methodology.md's **Claim strength:** line is not descriptive, association, or causal with its "
                "design basis")
    if level != ceiling:
        return f"methodology.md states {level} on its **Claim strength:** line"
    if level == "causal":
        records = {}
        for result in cited:
            if _level(claims.get(result)) == "causal":
                records.setdefault(_claim_text(_inline(claims[result])[0]), []).append(result)
        recorded = "; ".join(f"{cell} for {', '.join(results)}" for cell, results in records.items())
        if len(records) > 1:
            return (f"the results it cites record different causal designs ({recorded}); give each design its "
                    "own finding")
        if declared[0] not in records:
            return f"methodology.md states {declared[0]} on its **Claim strength:** line; state.md records {recorded}"
    return None


def _phrases(lines, field, level):
    """Each causal phrase in a region's `field` text: (line offset, phrase, whether in a ### headline)."""
    body = "\n".join(getattr(line, field) for line in lines)
    return [(body.count("\n", 0, match.start()), " ".join(match.group(0).split()),
             level == 3 and match.start() < len(getattr(lines[0], field))) for match in _CAUSAL.finditer(body)]


def claim_problems(draft, represented: list[str], claims: dict) -> list[dict]:
    """List causal wording in findings.md above its claim strength, and claim records that are missing.

    `claims` maps result IDs to state.md Claim cells, as `state_claims` returns them. A `###` finding
    slide is held to the weakest claim among the results its methodology.md namesake cites, or among
    all represented results when it cites none; the title, Answer, Implications, and any other slide
    that states conclusions, to the strongest represented claim. A slide the template names keeps its rule
    under ## Appendix, and an appendix finding slide is held like any other. Each finding's methodology
    section states its strength on one `**Claim strength:**` line, a causal one as its results' Claim cell.
    methodology-note.md, when the draft holds it, is read whole at the strongest represented claim, its
    rows carrying `file`. Every file is read as it renders (`_view`).
    """
    return _claim_review(draft, represented, claims)[0]


def _claim_review(draft, represented, claims):
    """claim_problems' rows, and the methodology.md line numbers of the **Claim strength:** lines it accepts."""
    draft = Path(draft)
    levels = {result: _level(cell) for result, cell in claims.items()}
    rows = [{"result": r, "problem": "state.md has no findings row with a claim strength for this result"
             if r not in claims else "state.md's Claim cell is not descriptive, association, or causal "
             "with its design basis"} for r in represented if not levels.get(r)]
    # Sections sharing a heading pool their citations and declarations, so none is dropped.
    sections = {}
    for level, heading, _, lines in _regions(_read_view(draft / "methodology.md")[0]):
        if level == 3:
            section = sections.setdefault(heading, {"text": [], "declared": [], "lines": []})
            section["text"] += [" ".join([line.plain, *line.links]) for line in lines]
            for line in lines:
                if line.declares and (match := _CLAIM_LINE.match(line.plain)):
                    section["declared"].append(_claim_text(match[1]))
                    section["lines"].append(line.number)
    known = [levels[r] for r in represented if levels.get(r)]
    deck = max(known, key=_CLAIMS.index) if known else _CLAIMS[0]
    declared, part, accepted = set(), None, set()
    for level, heading, first, lines in _regions(_read_view(draft / "findings.md")[0]):
        if level == 2:
            part = heading
        named = _named(level, heading, part)
        if named and heading in _UNCHECKED:
            continue
        if level == 3 and not named:
            section = sections.get(heading)
            cited = _cited("\n".join(section["text"]) if section else "", represented) or list(represented)
            ceiling = _weakest(cited, levels)
            problem = None if heading in declared else _declaration_problem(section, cited, ceiling, claims)
            if problem:
                rows.append({"section": heading, "problem": f"{problem}; its results support {ceiling}"})
            elif heading not in declared:
                accepted.update(section["lines"])
            declared.add(heading)
        else:
            cited, ceiling = list(represented), deck
        rows += _wording(lines, first, 0 if named else level, ceiling, cited, heading or "title")
    if METHODOLOGY_NOTE in _narratives(draft):
        for level, heading, first, lines in _regions(_read_view(draft / METHODOLOGY_NOTE)[0]):
            rows += [{"file": METHODOLOGY_NOTE, **row}
                     for row in _wording(lines, first, 0, deck, list(represented), heading)]
    return rows, accepted


def _wording(lines, first, level, ceiling, cited, section):
    """A region's causal phrases above `ceiling` as claims rows; a level-3 region's heading is a headline."""
    if ceiling == "causal":
        return []
    found = _phrases(lines, "prose", level)
    found += (Counter(_phrases(lines, "spaced", level)) - Counter(found)).elements()
    return [{"line": first + offset, "section": section, "phrase": phrase, "claim": ceiling, "results": cited,
             "problem": f"causal wording above the {ceiling} claim strength; reword it, since only an experiment "
                        "or an identified natural experiment supports a causal claim"
                        + ("; reword the methodology.md heading to match" if in_heading else "")}
            for offset, phrase, in_heading in sorted(found, key=lambda item: item[0])]


# ---------------------------------------------------------------- numbers in the narratives

NARRATIVES = ("findings.md", "methodology.md")
# Reading fails safe: a number is skipped only in one of the contexts below, each of which marks it as no
# quantity; every other number is read, so a doubtful one becomes a row the author clears by rewording or
# by allowing it. check_numbers also skips the accepted **Claim strength:** lines it is given (`claim_lines`),
# whose numbers repeat the record. references/helpers.md states the same list, those lines last.
_MONTH = (r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
          r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?")
_DAY = r"(?:3[01]|[12][0-9]|0?[1-9])"
_DAYS = rf"{_DAY}(?:\s*(?:[-–—]|to|through)\s*{_DAY})?"
_YEAR = r"(?:19|20)[0-9]{2}"
# Not glued to a word or to digits joined by a dot, comma, slash, or colon.
_ALONE = r"(?![\w%]|[.,/:][0-9])"
# Where a period or a date ends: punctuation, a dash before a space, or the end of its paragraph. A word
# after it could make its last number a count ("in 2000 orders"), so it is no period there.
_ENDS = r"(?=\s*(?:[,.;:!?()\[\]{}|*_\"'“”‘’…]|[-–—]\s|\Z))"


def _listed(item):
    """A range or a list closed by and or or, after a first item: 2023-2024, 2023 to 2025, 1, 2, and 3."""
    return rf"(?:\s*(?:[-–—]|to|through|vs\.?)\s*{item}|(?:\s*,\s*{item})*,?\s+(?:and|or)\s+{item})"


_DATE = rf"(?:{_MONTH}\s+{_DAY}|{_DAY}\s+{_MONTH})"
_DATE_ENDS = rf"(?:{_ENDS}|(?=\s+(?:to|through|until|till|and|or|[-–—])\s+{_DATE}))"
# A year after one of these words, a month name, or a quarter or half, where the period ends.
_IN = (rf"(?:(?i:\b(?:in|from|since|during|until|till|through|before|after|between|year|FY|CY|fiscal|calendar)\s+"
       rf"|\b(?:early|mid|late)[\s-]+)|{_MONTH}\s+|\b[QH][1-4]\s+)")
_NOT_QUANTITY = re.compile(
    rf"(?<![\w.])(?:{_YEAR}-(?:1[0-2]|0?[1-9])(?:-{_DAY})?(?:T[0-9:.]+(?:Z|[+-][0-9:]+)?)?{_ALONE}"
    rf"|[0-9]{{1,2}}/[0-9]{{1,2}}/{_YEAR}{_ALONE}"
    r"|[0-9]{1,2}:[0-9]{2}(?::[0-9]{2}(?:\.[0-9]+)?)?\s?(?i:[ap]\.?m\.?|UTC|GMT)(?!\w)"
    rf"|[0-9]{{1,2}}:[0-9]{{2}}:[0-9]{{2}}{_ALONE}"
    rf"|{_MONTH}\s+{_DAYS}(?:,?\s+{_YEAR}{_ALONE}{_DATE_ENDS}|{_ALONE}{_DATE_ENDS})"
    rf"|{_DAYS}\s+{_MONTH}(?:,?\s+{_YEAR}{_ALONE})?{_DATE_ENDS}"
    rf"|{_IN}{_YEAR}(?:{_listed(_YEAR)})?{_ALONE}{_ENDS}"
    rf"|[Cc]harts\s+[0-9]+{_listed('[0-9]+')}{_ALONE}{_ENDS}|[Cc]harts?\s+[0-9]+{_ALONE})"
    r"|^[ \t]*#{1,6}[ \t]+[0-9]+[.)](?=\s)|\[\^[^\]\n]*\]", re.MULTILINE)
_LIST_MARKER = re.compile(r"[ \t]*([0-9]{1,9})[.)](?=\s|$)")
_CURRENCY = re.compile(r"\b(?:USD|EUR|GBP|JPY|CHF|CAD|AUD|CNY|INR)(?=[0-9])")
# Paths and names are blanked whole, so no digit inside them is read (results/r-001-77.csv, ORD-123-45).
_PATH_CANDIDATE = re.compile(
    r"(?<![^\s(\[<\"'*_])(?:[A-Za-z_~][^\s,;|()\[\]<>\"']*|\.{1,2})[/\\][^\s,;|()\[\]<>\"']*")
_EXTENSIONS = "md|py|csv|tsv|parquet|jsonl?|sql|png|svg|jpe?g|pdf|html?|duckdb|db|xlsx?|docx|pptx|ya?ml|toml|txt|log|ipynb"
_FILE = re.compile(rf"(?<![\w.,/\\-])[\w-]*\w\.(?:{_EXTENSIONS})(?![\w/\\])")
_HYPHENATED = re.compile(r"(?<![\w.-])([A-Za-z_]\w*)(?:-\w+)+")
# A DOI: 10., a registrant code of four to nine digits with any dot-separated parts, a slash, and its suffix,
# which runs to the next whitespace or to a , or ; before a digit, after doi: or DOI, or bare when its
# suffix holds both a letter and a digit; a bare 10.2500/litre or 10.2500/1000 is a quantity, so it is read.
_DOI_SUFFIX = r"(?:[^\s,;]|[,;](?![0-9]))"
_DOI = re.compile(rf"(?i:\bdoi)(?::\s*|\s+)10\.[0-9]{{4,9}}(?:\.[0-9]+)*/{_DOI_SUFFIX}+"
                  rf"|(?<![\w.])10\.[0-9]{{4,9}}(?:\.[0-9]+)*/(?={_DOI_SUFFIX}*?[A-Za-z])(?={_DOI_SUFFIX}*?[0-9])"
                  rf"{_DOI_SUFFIX}+")


def _path(token):
    token = token.rstrip(".:!?*_~")
    segments = re.split(r"[/\\]", token)
    return (token.startswith(("./", "../", ".\\", "..\\", "~")) or len(segments) >= 3
            or segments[0] in _PATH_ROOTS or bool(_FILE.fullmatch(segments[-1])))


def _identifier(first):
    # ORD-123-45, COVID-19, Q-3, r-001, and the chart file stem chart-1; top-10 and mid-2025 stay words.
    return (len(first) == 1 or first.lower() == "chart" or bool(re.search(r"[0-9_]", first))
            or bool(re.search(r"[A-Z]", first[1:])))


def _blank_names(text):
    blanks = [match.span() for match in _PATH_CANDIDATE.finditer(text) if _path(match.group(0))]
    blanks += [match.span() for match in _FILE.finditer(text)]
    blanks += [match.span() for match in _HYPHENATED.finditer(text) if _identifier(match.group(1))]
    blanks += [match.span() for match in _DOI.finditer(text)]
    for start, end in blanks:
        text = _blank(text, start, end)
    return text


# A number not glued to a word or a path, with its unit. A word unit or % may stand after any whitespace,
# a line wrap included; a letter scale (k, M, b) or x is written against its number. Letters written against
# a number are shown with it (5GB, 30d, 95th). Digits joined by dots, commas, slashes, colons, or spaces between
# three-digit groups are read as one number: a version or address (3.12.1, 10.0.0.1) is no quantity, and any
# other join but thousands grouping or one decimal point never traces (1,2,3, 21,3, 3/4, 14:05, 1.234.567, 1 000).
_NUMBER = re.compile(
    r"(?<![^\W_])(?<![^\W_]_)(?<![0-9][.,/:])"
    r"((?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)[eE][-+]?[0-9]+|[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{3})+(?:\.[0-9]+)?"
    r"|[0-9]+(?:[.,/:][0-9]+)*|\.[0-9]+)"
    r"(\s*%|\s*(?:per\s*cent|percentage\s+points?|pp|thousand|million|billion|trillion|mn|bn|tn)(?!\w)"
    r"|(?:[kKmMbB]|[x×])(?!\w))?"
    r"((?<=[0-9])[^\W\d_]+)?"
    r"(?![^\W_]|_[^\W_]|[.,/:][0-9])")
_GROUPED = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"
                      r"|[0-9]+\.[eE][-+]?[0-9]+")
_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+){2,}")
_RANGE = re.compile(r"\s*(?:[-–—]|to|and)\s*")
_SCALES = {"k": 3, "thousand": 3, "m": 6, "mn": 6, "million": 6, "b": 9, "bn": 9, "billion": 9,
           "tn": 12, "trillion": 12}


def _quantities(line, before="", after="", *, marker=True, code=True):
    """Yield (text, body, unit, start, end) for each number a line states, after the skips check_numbers names.

    `before` and `after` are the lines of the same paragraph around `line`, read only so that a context or a
    unit a line wrap splits from its number is still seen. `marker` is false where a leading number cannot
    be a list marker. `code` is false where the code spans are already blanked across their paragraph, as
    `_unfenced` blanks them, so no backtick is paired within these lines alone. Every skip blanks with spaces, so `start` and `end` index the line as written; `end`
    passes the line's length when a unit stands after the wrap.
    """
    offset = len(before) + 1 if before else 0
    if marker and (found := _LIST_MARKER.match(line)):
        line = _blank(line, 0, found.end())
    text = (before + "\n" if before else "") + line + ("\n" + after if after else "")
    for start, end in _code_spans(text) if code else ():
        text = _blank(text, start, end)
    text = _CURRENCY.sub(lambda match: " " * len(match.group(0)), text)
    text = _NOT_QUANTITY.sub(lambda match: " " * len(match.group(0)), _blank_names(text))
    text = re.sub(r"\]\([^)\n]*\)", lambda match: "]" + " " * (len(match.group(0)) - 1), text)
    matches = list(_NUMBER.finditer(text))
    for index, match in enumerate(matches):
        if not offset <= match.start() < offset + len(line):
            continue
        body, unit, letters = match.group(1), match.group(2) or "", match.group(3) or ""
        if not unit and not letters and index + 1 < len(matches) and _RANGE.fullmatch(
                text[match.end():matches[index + 1].start()]):
            unit = matches[index + 1].group(2) or ""  # 10-15%: the lower bound takes the upper's unit
        if re.fullmatch(r"0[0-9]+", body) or _VERSION.fullmatch(body) and not re.fullmatch(
                r"[0-9]{1,3}(?:\.[0-9]{3})+", body):
            continue  # a zero-padded code such as release 002, or a version; 1.234.567 is read
        if letters and not letters.isalpha():
            body += letters  # 5½ has no one value
        yield (" ".join(match.group(0).split()), body, " ".join(unit.lower().split()), match.start() - offset,
               match.end() - offset)


# Arithmetic on written numbers never rounds: every digit a narrative or a record writes is kept.
_EXACT = Context(prec=MAX_PREC, Emax=MAX_EMAX, Emin=MIN_EMIN)


def _value(body):
    """Return a number's value and half a unit of its last written place, both exact.

    Raises ValueError or ArithmeticError for an exponent too large to hold.
    """
    mantissa, _, exponent = body.replace(",", "").lower().partition("e")
    exponent = int(exponent or 0)
    with localcontext(_EXACT):
        return (Decimal(mantissa).scaleb(exponent),
                Decimal(5).scaleb(exponent - len(mantissa.partition(".")[2]) - 1))


def _magnitudes(value, into, *, text=True):
    """Add the absolute value of every finite number in a JSON or CSV value; text only when `text`.

    A string that is not a number whole is read the way check_numbers reads a narrative line, adding
    each number and, with a scale such as M, its scaled value.
    """
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float, Decimal)):
        value = str(value)  # recorded JSON is read with exact decimals, so str keeps every written digit
    elif isinstance(value, dict):
        for item in value.values():
            _magnitudes(item, into, text=text)
        return
    elif isinstance(value, list):
        for item in value:
            _magnitudes(item, into, text=text)
        return
    elif not (isinstance(value, str) and text):
        return
    try:
        number = Decimal(value.strip())
        found = [number] if number.is_finite() else []
    except InvalidOperation:
        found = []
        for line in value.splitlines():
            for _, body, unit, _, _ in _quantities(line):
                if not _GROUPED.fullmatch(body):
                    continue
                try:
                    number = _value(body)[0]
                    found.append(number)
                    if unit in _SCALES:
                        found.append(number.scaleb(_SCALES[unit], _EXACT))
                except (ValueError, ArithmeticError):
                    continue  # an exponent too large to hold records nothing
    into.update(number.copy_abs() for number in found)  # copy_abs never rounds, so 4e1234567 cannot overflow


def _evidence_numbers(record):
    """The parts of an evidence record that hold result values: check details and settings content."""
    checks, settings = record.get("checks"), record.get("settings")
    return [[check.get("detail") for check in checks if isinstance(check, dict)] if isinstance(checks, list) else [],
            settings.get("content") if isinstance(settings, dict) else None]


def _read_exact_json(path):
    """Read a JSON object with every fraction as an exact Decimal, so no recorded digit is lost."""
    record = json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal)
    if not isinstance(record, dict):
        raise ValueError(f"{Path(path).name} is not a JSON object")
    return record


def recorded_values(root, investigation, results) -> tuple[list, list[str]]:
    """Return the sorted magnitudes the manifest's represented results record, and the problems.

    Each result contributes every cell of results/<id>.csv, the numbers in results/<id>.profile.json,
    and the numbers in its evidence's check details and settings. JSON numbers are read exactly as written.
    """
    if not isinstance(results, list) or not all(
            isinstance(entry, dict) and isinstance(entry.get("result_id"), str)
            and _SIMPLE.fullmatch(entry["result_id"]) for entry in results):
        return [], [f"{MANIFEST} results is not a list of result_id entries; rerun export"]
    base = Path(root) / "investigations" / investigation
    values, problems = set(), []
    for result_id in dict.fromkeys(entry["result_id"] for entry in results):
        table = base / "results" / f"{result_id}.csv"
        try:
            with table.open(newline="", encoding="utf-8") as stream:
                cells = {cell for row in csv.reader(stream) for cell in row}
            for cell in cells:  # each distinct cell is read once
                _magnitudes(cell, values)
        except FileNotFoundError:
            problems.append(f"{_rel(root, table)} is missing; numbers from {result_id} cannot be traced")
        except (OSError, UnicodeError, csv.Error) as error:
            problems.append(f"{_rel(root, table)}: unreadable ({error})")
        # The table holds the result; a profile or evidence, when present, adds its counts and settings.
        for path in (base / "results" / f"{result_id}.profile.json", base / "evidence" / f"{result_id}.json"):
            try:
                record = _read_exact_json(path)
            except FileNotFoundError:
                continue
            except (OSError, ValueError) as error:
                problems.append(f"{_rel(root, path)}: unreadable ({error})")
                continue
            if path.parent.name == "results":
                _magnitudes(record, values, text=False)  # dtype names such as float64 are not values
            else:
                _magnitudes(_evidence_numbers(record), values)
    return sorted(values), problems


def allowed_numbers(record: dict) -> tuple[set, list[str]]:
    """Return the texts the manifest's allowed_numbers accepts untraced, and its malformed entries."""
    entries = record.get("allowed_numbers", "none")
    if entries == "none":
        return set(), []
    if not isinstance(entries, list):
        return set(), ["allowed_numbers is not none or a list of {text, reason}"]
    texts, problems = set(), []
    for index, entry in enumerate(entries, start=1):
        if isinstance(entry, dict) and all(isinstance(entry.get(key), str) and entry[key].strip()
                                           for key in ("text", "reason")):
            texts.add(entry["text"].strip())
        else:
            problems.append(f"allowed_numbers entry {index} is not {{text, reason}} with both filled in")
    return texts, problems


def _within(values, low, high):
    index = bisect.bisect_left(values, low)
    return index < len(values) and values[index] <= high


def _traces(body, unit, values):
    # Written to d places, the number stands for any value within half a unit of its last place.
    if not _GROUPED.fullmatch(body):
        return False  # 1,2,3, the decimal comma 21,3, 3/4, 14:05, and 1.234.567 have no one value
    try:
        number, half = _value(body)
        with localcontext(_EXACT):
            low, high = number - half, number + half
            windows = [(low, high)]
            if unit.startswith(("%", "per", "pp")):
                windows.append((low.scaleb(-2), high.scaleb(-2)))
            elif unit in _SCALES:
                windows.append((low.scaleb(_SCALES[unit]), high.scaleb(_SCALES[unit])))
    except (ValueError, ArithmeticError):
        return False  # an exponent too large to hold traces to nothing
    return any(_within(values, low, high) for low, high in windows)


# A line that opens a block (a heading, a bullet, a quote, a table row, or a fence) starts no wrap.
_OPENS_BLOCK = re.compile(r"\s*(?:$|#{1,6}(?:\s|$)|[-*+](?:\s|$)|>|\||`{3,}|~{3,})")
_QUOTE_MARKERS = re.compile(r"[ \t]*(?:>[ \t]?)+")


def _unquoted(line):
    """The line with its blockquote markers blanked, so a quoted paragraph reads like any other."""
    return _QUOTE_MARKERS.sub(lambda match: " " * len(match.group(0)), line, count=1) if _QUOTE_MARKERS.match(line) else line


def _continues(previous, line):
    """Whether `line` wraps the paragraph `previous` ends, so a context or a unit may span the two.

    A numbered line continues paragraph text unless it numbers 1, the only number that starts a list
    there; so "rose to\\n77. Orders" reads 77. An unindented one also starts a list after a list item or an
    indented line; an indented one only after a list item at its own indentation, so "- rose to\\n  77. Orders",
    where 77 wraps the item's text, reads 77. Two quoted lines are compared inside the quote.
    """
    if _QUOTE_MARKERS.match(previous) and _QUOTE_MARKERS.match(line):
        previous, line = _QUOTE_MARKERS.sub("", previous, count=1), _QUOTE_MARKERS.sub("", line, count=1)
    if _OPENS_BLOCK.match(previous) and not re.match(r"\s*[-*+>]\s", previous) or _OPENS_BLOCK.match(line):
        return False
    numbered = _LIST_MARKER.match(line)
    if not numbered:
        return True
    indent = line[:len(line) - len(line.lstrip(" \t"))]
    starts = r"\s|[-*+>]\s|[0-9]+[.)]\s" if not indent else re.escape(indent) + r"(?:[-*+]|[0-9]+[.)])\s"
    return int(numbered.group(1)) != 1 and not re.match(starts, previous)


def check_numbers(path: str | os.PathLike, values, *, allowed=(), claim_lines=()) -> list[dict]:
    """List each number in a narrative file that no recorded value rounds to and `allowed` does not cover.

    `values` are sorted magnitudes from recorded_values(). An `allowed` text covers a number wherever the
    text is written around it, matched on the text the number is read from, so any whitespace or a line
    wrap matches a space: a bare `40` covers every 40, and `Week 23` only that 23. A number is skipped
    only in a context references/helpers.md lists; every other number is read. `claim_lines` are the line
    numbers of the **Claim strength:** lines the claims check accepts (`_claim_review`): each repeats a
    state.md Claim cell, so its numbers trace to the record.
    """
    patterns = [re.compile(r"\s+".join(map(re.escape, text.split()))) for text in allowed if text.strip()]
    rows, lines = [], list(_source_lines(path))
    for index, (number, line, opens, bare) in enumerate(lines):
        if opens or number in claim_lines:
            continue
        previous = lines[index - 1] if index and lines[index - 1][0] == number - 1 else None
        following = lines[index + 1] if index + 1 < len(lines) and lines[index + 1][0] == number + 1 else None
        wraps = previous is not None and not previous[2] and _continues(previous[1], line)
        follows = following is not None and not following[2] and _continues(line, following[1])
        # Wraps, list markers, and allowed texts read the line with its code spans; numbers read it without them.
        before, line, after = (_unquoted(text) for text in (previous[1] if wraps else "", line,
                                                            following[1] if follows else ""))
        reads = [_unquoted(text) for text in (previous[3] if wraps else "", bare, following[3] if follows else "")]
        marker = not wraps and bool(_LIST_MARKER.match(line))
        # The text _quantities reads, so an allowed text and a row's text match across the same wrap.
        offset = len(before) + 1 if before else 0
        joined = (before + "\n" if before else "") + line + ("\n" + after if after else "")
        spans = [found.span() for pattern in patterns for found in pattern.finditer(joined)]
        for text, body, unit, start, end in _quantities(reads[1], reads[0], reads[2], marker=marker, code=False):
            covered = any(low <= offset + start and offset + end <= high for low, high in spans)
            if not covered and not _traces(body, unit, values):
                rows.append({"file": Path(path).name, "line": number, "text": text})
    return rows


# ---------------------------------------------------------------- inventory and tree comparison

_CHUNK_BYTES = 1024 * 1024  # 1 MiB reads keep memory flat on large datasets


def _scan(directory):
    root = Path(directory)
    if root.is_symlink():
        raise ValueError(f"Symlink in tree: {root}")

    def fail(error):
        raise error

    files = {}
    for current, dirnames, filenames in os.walk(root, onerror=fail):
        for name in dirnames + filenames:
            if Path(current, name).is_symlink():
                raise ValueError(f"Symlink in tree: {Path(current, name)}")
        for name in filenames:
            file = Path(current, name)
            if not file.is_file():
                continue
            digest = hashlib.sha256()
            size = 0
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(_CHUNK_BYTES), b""):
                    size += len(chunk)
                    digest.update(chunk)
            path = file.relative_to(root).as_posix()
            files[path] = {"path": path, "bytes": size, "sha256": digest.hexdigest()}
    return files


def inventory(package_dir: str | os.PathLike) -> list[dict]:
    """List files in path order, reserving a path-only row for manifest.json."""
    files = _scan(package_dir)
    files[MANIFEST] = {"path": MANIFEST}
    return [files[path] for path in sorted(files)]


def _difference(path, kind, expected, actual):
    return {"path": path, "kind": kind, "expected": expected, "actual": actual}


def _compare(expected, actual, manifest_name=None):
    differences = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in actual:
            recorded = None if path == manifest_name else expected[path]["sha256"]
            differences.append(_difference(path, "missing", recorded, None))
        elif path not in expected:
            differences.append(_difference(path, "extra", None, actual[path]["sha256"]))
        elif path != manifest_name:
            recorded, found = expected[path], actual[path]
            if recorded["bytes"] != found["bytes"]:
                differences.append(_difference(path, "size", recorded["bytes"], found["bytes"]))
            # A size change is also reported as a checksum change, so both kinds always name it.
            if recorded["bytes"] != found["bytes"] or recorded["sha256"].lower() != found["sha256"]:
                differences.append(_difference(path, "checksum", recorded["sha256"], found["sha256"]))
    return differences


def verify(package_dir: str | os.PathLike, inventory: list[dict]) -> list[dict]:
    """Compare a package with the inventory recorded in its manifest; manifest content is excluded."""
    expected = {}
    for row in inventory:
        path = row.get("path")
        if not isinstance(path, str):
            raise ValueError(f"Inventory row without a path: {row!r}")
        if path in expected:
            raise ValueError(f"Duplicate inventory path: {path}")
        expected[path] = dict(row)
        if path != MANIFEST:
            if "bytes" not in row or not isinstance(row.get("sha256"), str):
                raise ValueError(f"Incomplete inventory row: {path}")
            size = row["bytes"]
            if isinstance(size, str) and size.isascii() and size.isdigit():
                size = int(size)
            if type(size) is not int or size < 0:
                raise ValueError(f"Invalid inventory byte size: {path}")
            expected[path]["bytes"] = size
    return _compare(expected, _scan(package_dir), MANIFEST)


def compare_trees(local_dir: str | os.PathLike, copy_dir: str | os.PathLike) -> list[dict]:
    """Compare every file, including the manifest, with the local release as expected."""
    return _compare(_scan(local_dir), _scan(copy_dir))


# ---------------------------------------------------------------- the deck outline
#
# findings.md is the deck's only source: `parse_outline` derives its slide structure as the file renders
# (`_view`), and nothing writes that structure down, so the outline stays the one source of truth. The
# rules a builder follows are package-format/deck-rules.md; `outline_problems` and `check_charts` check the
# parts of them a parse can settle.

# A chart specification is a paragraph, or a list item, that renders opening with "Chart N."; its fields
# are the list items directly under it, each opening with its field name, until a blank line follows one.
# An item nested deeper than the fields, a blank line before it or not, or a later paragraph inside a field,
# is kept on the chart as "inside" and reported by `check_charts`; the fields go on after it.
_CHART_SPEC = re.compile(r"[ \t]*Chart (\d+)\.(?=\s|$)")
_CHART_FIELD = re.compile(r"(Data|Highlight|Axis|Interval|Source|Caveat|Alt text):(?=\s|$)\s*(.*)")
_HEADLINE = re.compile(r"Headline:(?=\s|$)\s*(.*)")
_NOTES = re.compile(r"Notes:(?=\s|$)\s*(.*)")
_FINDINGS_SECTION = "Findings"
# ## Appendix, like ## Findings, holds ### slides; a deck has one, which follows the main sequence and ends it.
_APPENDIX_SECTION = "Appendix"
# The template's other ## slides. Under ## Appendix a ### slide with one of these headings is that slide,
# not a finding; only _MOVABLE ones may stand there. _REQUIRED must each appear once, in this order,
# with at least one finding slide in the main sequence after Answer; How we know or Limitations and open
# caveats may move to the appendix, keeping this order when both do.
_SECTIONS = ("Answer", "Implications", "How we know", "Limitations and open caveats", "Open questions",
             "What changed since the last version", "Supporting datasets")
_MOVABLE = ("How we know", "Limitations and open caveats", "Supporting datasets")
_REQUIRED = ("Answer", "How we know", "Limitations and open caveats")
HEADLINE_WORDS = 15
SLIDE_BULLETS = 5
# Form -> (roles it needs, roles it may add, roles it may repeat); every other role is named once.
CHART_FORMS = {
    "Horizontal bar": (("category", "value"), ("series",), ("value",)),
    "Bar with intervals": (("category", "value", "lower", "upper"), (), ()),
    "Line": (("category", "value"), ("series",), ("value",)),
    "Column": (("category", "value"), ("series",), ("value",)),
    "Stacked bar": (("category", "value"), ("series",), ("value",)),
    "Scatter": (("x", "y"), ("label", "fit"), ()),
    "Table": (("column",), (), ("column",)),
}
_FORM_NAMES = {form.lower(): form for form in CHART_FORMS}
_WORD = re.compile(r"\w")


def _blocks(lines):
    """A region's rendered blocks, its heading line left out: {"kind", "line", "depth", "first", "text"}.

    kind is "paragraph", "item" (a list item, depth 1 at the top level), or "heading" (level 4 to 6). first is
    the opening line's plain text, which the chart check reads as `check_charts` always has; text is the
    whole block as it shows, whitespace collapsed. gap marks a blank line before the block. An item that
    holds later paragraphs, a block quote's included, lists their first lines in "paragraphs"; a paragraph
    records in "listed" the list depth it sits in, 0 outside every list.
    """
    blocks, gap = [], False
    for line in lines[1:] if lines and lines[0].kind == "heading" and 1 <= lines[0].level <= 3 else lines:
        if line.kind == "heading":
            blocks.append({"kind": "heading", "line": line.number, "depth": 0, "first": line.title,
                           "text": line.title, "gap": gap})
            gap = False
            continue
        if line.kind not in ("text", "html"):
            continue
        text = _collapse(_shown(line.plain))
        if line.item:
            blocks.append({"kind": "item", "line": line.number, "depth": line.item, "first": line.plain,
                           "text": text, "gap": gap})
        # A paragraph in a list item continues the block before it only when that block is an item of the same
        # depth; after a deeper item it would join the wrong one, so it stands alone and is reported.
        elif text and (not blocks or line.start and (not line.listed or _CHART_SPEC.match(line.plain)
                                                     or blocks[-1]["kind"] != "item"
                                                     or blocks[-1]["depth"] != line.listed)):
            blocks.append({"kind": "paragraph", "line": line.number, "depth": 0, "first": line.plain,
                           "text": text, "gap": gap, "listed": line.listed})
        elif text:
            if line.start:
                blocks[-1].setdefault("paragraphs", []).append(line.number)
            blocks[-1]["text"] = _collapse(f"{blocks[-1]['text']} {text}")
        else:
            gap = True
            continue
        gap = False
    return blocks


def _chart(block):
    number = int(_CHART_SPEC.match(block["first"])[1])
    written, _, comparison = re.sub(r"^Chart \d+\.", "", block["text"]).partition(":")
    written = _collapse(written)
    return {"number": number, "line": block["line"], "form": _FORM_NAMES.get(written.lower()),
            "written": written, "comparison": comparison.strip(), "fields": {}, "inside": [], "slide": None}


def _slide(heading, first, lines):
    """One region read as a slide: headline, bullets, chart specifications, notes, and anything else."""
    blocks = _blocks(lines)
    slide = {"line": first, "heading": heading, "opening": blocks[0]["line"] if blocks else None, "headlines": [],
             "bullets": [], "notes": [], "after_notes": None, "charts": [], "extra": []}
    chart = depth = None  # depth: the open chart's field depth, set by its first field
    for block in blocks:
        if slide["notes"] and slide["after_notes"] is None:
            slide["after_notes"] = block["line"]
        text = block["text"]
        # An item deeper than the fields renders inside the last one, a blank line before it or not, and so does
        # a paragraph at the fields' list depth or deeper that a nested item kept from joining its field.
        if chart is not None and depth is not None and (
                block["kind"] == "item" and block["depth"] > depth
                or block["kind"] == "paragraph" and block["listed"] >= depth and not _CHART_SPEC.match(block["first"])):
            chart["inside"].append({"line": block["line"], "field": list(chart["fields"])[-1], "kind": block["kind"]})
            continue
        if chart is not None and block["kind"] == "item" and not (block["gap"] and chart["fields"]):
            if (depth is None or block["depth"] == depth) and (field := _CHART_FIELD.match(text)) \
                    and field[1] not in chart["fields"]:
                chart["fields"][field[1]] = field[2].strip()
                chart["inside"] += [{"line": line, "field": field[1], "kind": "paragraph"}
                                    for line in block.get("paragraphs", [])]
                depth = block["depth"]
                continue
        chart = depth = None
        if block["kind"] != "heading" and _CHART_SPEC.match(block["first"]):
            chart = _chart(block)
            slide["charts"].append(chart)
        elif block["kind"] == "item":
            if block["depth"] == 1 or not slide["bullets"]:
                slide["bullets"].append({"line": block["line"], "text": text, "sub": []})
            else:
                slide["bullets"][-1]["sub"].append(text)
        elif block["kind"] == "paragraph" and (match := _HEADLINE.match(text)):
            slide["headlines"].append({"line": block["line"], "text": match[1].strip()})
        elif block["kind"] == "paragraph" and (match := _NOTES.match(text)):
            slide["notes"].append({"line": block["line"], "text": match[1].strip()})
        else:
            slide["extra"].append({"line": block["line"], "text": text})
    return slide


def parse_outline(text: str) -> dict:
    """Derive the deck from findings.md text as it renders, writing nothing.

    Returns {"title", "slides", "charts", "stray", "appendix", "counts"}. title is the `#` heading's slide or
    None: {"line", "text", "subtitle", "subtitle_line", "notes", ...}. slides are the deck's other slides in
    order, one per `##` section except Findings and Appendix and one per `###` slide under them: {"line", "section",
    "finding", "appendix", "heading", "headline", "bullets", "notes", "chart", ...}. A `###` slide is a
    finding slide, except one under ## Appendix headed with a template slide's name, such as How we know,
    which is that slide; appendix marks the slides under ## Appendix. headline is a finding's `###` heading
    or the first **Headline:** text, bullets are {"line", "text", "sub"} with nested items in sub, notes is
    the first **Notes:** text, and chart is the slide's first chart number. charts lists every chart
    specification in file order: {"number", "line", "form", "written", "comparison", "fields", "inside",
    "slide"}, form being the canonical CHART_FORMS name or None, fields each field's text by name, inside
    each nested "item" or later "paragraph" in a field as {"line", "field", "kind"}, and slide the index of
    its slide in slides, or None on the title slide or outside any slide. stray lists text outside every
    slide, and any second `#` heading, as {"where", "line", "text"}. appendix lists each ## Appendix heading
    as {"line", "slides"}, slides counting the `###` slides under it. counts is {"main", "appendix"}: the
    title slide and the slides before ## Appendix, and the slides under it, without the divider a builder
    adds. The remaining slide keys keep what the checks report: every **Headline:** and **Notes:**
    paragraph, the first block after the notes, every chart, and text that is none of these.
    """
    return _outline(_view(text)[0])


def _outline(view):
    outline = {"title": None, "slides": [], "charts": [], "stray": [], "appendix": []}
    section = None
    for level, heading, first, lines in _regions(view):
        read = _slide(heading, first, lines)
        if level == 1 and outline["title"] is None:
            # The subtitle is the paragraph the title slide opens with.
            subtitle = read["extra"].pop(0) if read["extra"] and read["extra"][0]["line"] == read["opening"] else None
            outline["title"] = {**read, "text": heading, "subtitle": subtitle and subtitle["text"],
                                "subtitle_line": subtitle and subtitle["line"],
                                "notes": read["notes"][0]["text"] if read["notes"] else None,
                                "notes_lines": [n["line"] for n in read["notes"]]}
            outline["charts"] += read["charts"]
            continue
        if level == 2:
            section = heading
            if heading == _APPENDIX_SECTION:
                outline["appendix"].append({"line": first, "slides": 0})
        if level in (0, 1) or (level == 2 and heading in (_FINDINGS_SECTION, _APPENDIX_SECTION)):
            where = ("before the deck title" if level == 0 else "under a second # heading" if level == 1
                     else "under Findings before its first finding slide" if heading == _FINDINGS_SECTION
                     else "under Appendix before its first slide")
            if level == 1:
                outline["stray"].append({"where": "a second # heading", "line": first, "text": heading})
            for block in sorted(read["headlines"] + read["notes"] + read["bullets"] + read["charts"] + read["extra"],
                                key=lambda block: block["line"]):
                outline["stray"].append({"where": where, "line": block["line"],
                                         "text": block.get("text") or f"Chart {block['number']}."})
            outline["charts"] += read["charts"]
            continue
        index = len(outline["slides"])
        for chart in read["charts"]:
            chart["slide"] = index
        outline["charts"] += read["charts"]
        appendix = level == 3 and section == _APPENDIX_SECTION
        if appendix:
            outline["appendix"][-1]["slides"] += 1
        finding = level == 3 and not (appendix and heading in _SECTIONS)
        headline = heading if finding else read["headlines"][0]["text"] if read["headlines"] else None
        outline["slides"].append({**read, "section": section, "finding": finding, "appendix": appendix,
                                  "headline": headline, "notes": read["notes"][0]["text"] if read["notes"] else None,
                                  "notes_lines": [n["line"] for n in read["notes"]],
                                  "chart": read["charts"][0]["number"] if read["charts"] else None})
    behind = sum(slide["appendix"] for slide in outline["slides"])
    outline["counts"] = {"main": (outline["title"] is not None) + len(outline["slides"]) - behind,
                         "appendix": behind}
    return outline


def read_outline(path: str | os.PathLike) -> dict:
    """`parse_outline` of the findings.md at path."""
    return parse_outline(Path(path).read_text(encoding="utf-8"))


def _words(text):
    return sum(bool(_WORD.search(token)) for token in text.split())


def outline_problems(findings_path: str | os.PathLike) -> list[dict]:
    """List each break of the slide rules in findings.md: {"slide", "line", "problem"}.

    Every slide after the title has a headline of at most HEADLINE_WORDS words (its `###` heading, or one
    **Headline:** line), at most SLIDE_BULLETS bullets (Open questions is exempt), at most one chart, and one **Notes:** paragraph that
    ends it, and holds nothing else. The title slide is the `#` heading with its subtitle line; a `###`
    finding slide sits under ## Findings or ## Appendix. The deck holds each _REQUIRED slide once: Answer
    first after the title, then at least one finding slide, with How we know and then Limitations and open
    caveats after the finding slides or under ## Appendix, How we know first when both stand in the same
    part. The deck holds one ## Appendix, which ends it and holds only _MOVABLE template slides besides
    findings.
    """
    outline = read_outline(findings_path)
    rows = []

    def row(slide, line, problem):
        rows.append({"slide": slide, "line": line, "problem": problem})

    title = outline["title"]
    if title is None:
        row("title", 1, "findings.md has no # deck title heading; open it with one and its subtitle line")
    else:
        if not title["subtitle"]:
            row("title", title["line"], "the title slide has no subtitle line under the # heading")
        for block in sorted(title["headlines"] + title["bullets"] + title["extra"] + title["charts"],
                            key=lambda block: block["line"]):
            row("title", block["line"], "the title slide holds only the # heading, its subtitle line, and notes; "
                                        "move this to a slide")
        if len(title["notes_lines"]) > 1:
            row("title", title["notes_lines"][1], f"{len(title['notes_lines'])} **Notes:** paragraphs; merge them "
                                                  "into one")
    for stray in outline["stray"]:
        row(stray["where"], stray["line"], "a second # heading; the deck has one title slide, so make this a ## "
            "slide or remove it" if stray["where"] == "a second # heading" else
            f"text {stray['where']} is on no slide; move it onto a slide")
    opens = outline["appendix"][0]["line"] if outline["appendix"] else None
    for slide in outline["slides"]:
        name, line = slide["heading"], slide["line"]
        if slide["finding"] and slide["section"] not in (_FINDINGS_SECTION, _APPENDIX_SECTION):
            row(name, line, "a ### finding slide outside the ## Findings section; move it under ## Findings")
        elif slide["finding"] and not slide["appendix"] and opens is not None and line > opens:
            row(name, line, "a ### finding slide after ## Appendix; the appendix ends the deck, so move it under "
                            "## Findings before ## Appendix, or under ## Appendix")
        elif not slide["appendix"] and opens is not None and line > opens:
            row(name, line, "a ## slide after ## Appendix; the appendix ends the deck, so move this slide before it")
        if slide["appendix"] and not slide["finding"] and name not in _MOVABLE:
            row(name, line, f"{name} stays in the main sequence; make it a ## slide before ## Appendix")
        if slide["finding"] and slide["headlines"]:
            row(name, slide["headlines"][0]["line"], "a finding slide's ### heading is its headline; remove the "
                                                     "**Headline:** line")
        elif not slide["finding"] and not slide["headlines"]:
            row(name, line, "no **Headline:** line; open the slide with one")
        elif not slide["finding"] and len(slide["headlines"]) > 1:
            row(name, slide["headlines"][1]["line"], f"{len(slide['headlines'])} **Headline:** lines; keep one")
        if slide["headline"] is not None:
            words = _words(slide["headline"])
            if not words:
                row(name, line, "the headline is empty; state the slide's point with its key number")
            elif words > HEADLINE_WORDS:
                row(name, line, f"the headline has {words} words; keep it to {HEADLINE_WORDS}")
        if len(slide["bullets"]) > SLIDE_BULLETS and (slide["finding"] or name != "Open questions"):
            row(name, slide["bullets"][SLIDE_BULLETS]["line"],
                f"{len(slide['bullets'])} bullets; keep it to {SLIDE_BULLETS} and move the rest to another slide "
                "or into the notes")
        if len(slide["charts"]) > 1:
            row(name, slide["charts"][1]["line"], f"{len(slide['charts'])} charts; a slide carries at most one")
        for extra in slide["extra"]:
            row(name, extra["line"], "text outside the headline, bullets, chart, and notes; make it a bullet or "
                                     "move it into the notes")
        if not slide["notes_lines"]:
            row(name, line, "no **Notes:** paragraph; end the slide with one")
        elif len(slide["notes_lines"]) > 1:
            row(name, slide["notes_lines"][1], f"{len(slide['notes_lines'])} **Notes:** paragraphs; merge them "
                                               "into one")
        elif slide["after_notes"] is not None and slide["after_notes"] not in {e["line"] for e in slide["extra"]}:
            row(name, slide["after_notes"], "text after the **Notes:** paragraph; the notes end the slide")

    # The required slides: Answer opens the main sequence, which holds at least one finding slide; How we
    # know and then Limitations follow the finding slides there, or stand under ## Appendix, How we know
    # first when both stand in the same part. Positions are in deck order; a finding slide after ## Appendix
    # has its own row above, so it moves no required slide.
    slides = outline["slides"]
    main = [slide for slide in slides if not slide["appendix"]]
    findings = [index for index, slide in enumerate(slides) if slide["finding"] and not slide["appendix"]
                and (opens is None or slide["line"] < opens)]
    placed = {}
    for name in _REQUIRED:
        given = [slide for slide in outline["slides"] if not slide["finding"] and slide["heading"] == name
                 and not (name == "Answer" and slide["appendix"])]
        if len(given) > 1:
            row(name, given[1]["line"], f"{len(given)} {name} slides; keep one")
        if name == "Answer":
            if not given:
                row(name, None, "no ## Answer slide; open the deck with it, right after the title slide")
            elif main[0] is not given[0]:
                row(name, given[0]["line"], "the Answer slide comes first after the title slide; move it there")
            if not findings:
                row(_FINDINGS_SECTION, None, "no ### finding slide in the main sequence; keep at least one under "
                                             "## Findings")
            continue
        if not given:
            row(name, None, f"no {name} slide; add it after the finding slides, or under ## Appendix")
            continue
        placed[name] = position = next(i for i, slide in enumerate(slides) if slide is given[0])
        appendix = given[0]["appendix"]
        known = placed.get("How we know")
        if name == "How we know":
            if not appendix and findings and position < findings[-1]:
                row(name, given[0]["line"], "How we know comes after the finding slides; move it below them")
        elif not appendix and (findings and position < findings[-1]
                               or known is not None and not slides[known]["appendix"] and position < known):
            row(name, given[0]["line"], f"{name} comes after the finding slides and How we know; move it below them")
        elif appendix and known is not None and slides[known]["appendix"] and position < known:
            row(name, given[0]["line"], f"{name} comes after How we know under ## Appendix; move it below How we know")
    for index, entry in enumerate(outline["appendix"]):
        if index:
            row(_APPENDIX_SECTION, entry["line"], "a second ## Appendix; the deck has one appendix, so merge them")
        if not entry["slides"]:
            row(_APPENDIX_SECTION, entry["line"], "## Appendix holds no slide; add ### slides under it or remove it")
    return rows


def chart_data(chart: dict) -> tuple[list, list[str]]:
    """A chart specification's **Data:** line as [(role, column header)] in order, and its problems."""
    form = chart["form"]
    if "Data" not in chart["fields"]:
        return [], ["no **Data:** line under the specification"]
    pairs, problems = [], []
    for entry in (part.strip() for part in chart["fields"]["Data"].split(";")):
        role, colon, header = entry.partition(":")
        role, header = role.strip().lower(), header.strip()
        if not entry:
            continue
        if not colon or not header or not role.isalpha():
            problems.append(f"**Data:** entry {entry!r} is not role: column header")
        else:
            pairs.append((role, header))
    if form is None:
        return pairs, problems
    needed, optional, repeated = CHART_FORMS[form]
    allowed = needed + optional
    roles = Counter(role for role, _ in pairs)
    for role in roles:
        if role not in allowed:
            problems.append(f"**Data:** role {role} is not one a {form} takes ({', '.join(allowed)})"
                            + (_intervals_note(form) if role in ("lower", "upper") else ""))
        elif roles[role] > 1 and role not in repeated:
            problems.append(f"**Data:** names more than one {role} column")
    for role in needed:
        if not roles[role]:
            problems.append(f"**Data:** names no {role} column, which a {form} needs")
    if roles["series"] and roles["value"] > 1:
        problems.append("**Data:** names a series column and more than one value column; name one value with "
                        "a series, or drop the series")
    return pairs, problems


# ---------------------------------------------------------------- chart files

# A package's charts/ holds one CSV per **Chart N.** specification in findings.md, named chart-N.csv
# in specification order: a header row of display names and the plotted values, nothing else.
_CHART_FILE = re.compile(r"chart-([1-9]\d*)\.csv")
# An underscore or a dot between letters marks a column name or code, not a display name.
_IDENTIFIER = re.compile(r"[A-Za-z0-9]_[A-Za-z0-9]|[A-Za-z]\.[A-Za-z]")


def _check_chart(number, headers, rows):
    if not rows:
        raise ValueError(f"Chart {number} has no rows")
    if not all(isinstance(header, str) and header.strip() for header in headers):
        raise ValueError(f"Chart {number} has a blank or non-text header")
    if len(set(headers)) != len(headers):
        raise ValueError(f"Chart {number} repeats a header")
    for header in headers:
        if _IDENTIFIER.search(header):
            raise ValueError(f"Chart {number} header is not a display name: {header}")


def write_charts(charts_dir: str | os.PathLike, charts: list) -> list[Path]:
    """Replace the chart files with chart-1.csv, ... from (headers, rows) pairs; none removes them."""
    for number, (headers, rows) in enumerate(charts, start=1):
        _check_chart(number, headers, rows)
    directory = Path(charts_dir)
    if directory.is_dir():
        for stale in directory.iterdir():
            if _CHART_FILE.fullmatch(stale.name):
                stale.unlink()
    if not charts:
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()  # A package without charts has no charts directory.
        return []
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for number, (headers, rows) in enumerate(charts, start=1):
        path = directory / f"chart-{number}.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows(rows)
        paths.append(path)
    return paths


def check_charts(findings_path: str | os.PathLike, charts_dir: str | os.PathLike) -> list[dict]:
    """Match the chart specifications in findings.md with the chart files, and each specification with its
    form and file: one of CHART_FORMS, a **Data:** line naming that form's roles, each named column in the
    file's header, and each column of the header named."""
    view = _read_view(findings_path)[0]
    charts = _outline(view)["charts"]
    numbers = [chart["number"] for chart in charts]
    # A spec line that continues the paragraph or bullet above it renders inside that block, so it is no spec.
    continued = {int(match[1]) for line in view if line.kind == "text" and not line.start
                 and (match := _CHART_SPEC.match(line.plain))}
    rows = []
    for position, number in enumerate(numbers, start=1):
        if number != position:
            rows.append({"chart": f"Chart {number}",
                         "problem": f"specification {position} is numbered {number}"})
    directory = Path(charts_dir)
    files = {}
    if directory.is_dir():
        for path in directory.iterdir():
            match = _CHART_FILE.fullmatch(path.name)
            if match:
                files[int(match.group(1))] = path
            else:
                rows.append({"chart": path.name, "problem": "not a chart file"})
    specified = set(numbers)
    for number in sorted(specified - files.keys()):
        rows.append({"chart": f"Chart {number}", "problem": "no chart file for this specification"})
    for number in sorted(files.keys() - specified):
        rows.append({"chart": f"Chart {number}", "problem": (
            f"Chart {number}'s specification continues the paragraph or bullet above it; leave a blank line before "
            "it" if number in continued else "chart file has no specification in findings")})
    headers = {}
    for number in sorted(specified & files.keys()):
        with files[number].open(encoding="utf-8", newline="") as stream:
            lines = list(csv.reader(line for line, _ in zip(stream, range(2)) if line.strip()))
        if len(lines) < 2:
            rows.append({"chart": f"Chart {number}", "problem": "chart file has no data rows"})
        headers[number] = lines[0] if lines else []
    for chart in charts:
        label = f"Chart {chart['number']}"
        if chart["form"] is None:
            rows.append({"chart": label, "problem": f"names no chart form ({chart['written'] or 'none written'}); "
                                                    f"open the specification with one of: {', '.join(CHART_FORMS)}"})
        pairs, problems = chart_data(chart)
        rows += [{"chart": label, "problem": problem} for problem in problems]
        if chart["number"] in headers:
            named = dict.fromkeys(header for _, header in pairs)
            for header in named:
                if header not in headers[chart["number"]]:
                    rows.append({"chart": label, "problem": f"chart-{chart['number']}.csv has no column "
                                                            f"{header!r}, which **Data:** names"})
            # A column no role names would be drawn by one builder and dropped by another.
            for header in headers[chart["number"]] if pairs else []:
                if header not in named:
                    rows.append({"chart": label, "problem": f"chart-{chart['number']}.csv column {header!r} is "
                                 f"named by no **Data:** role; name it{_by_role(chart['form'])}, or export the "
                                 "chart without it" + _intervals_note(chart["form"], column=True)})
        # Text nested in a field renders inside it, where a builder reads it as the field's or drops it.
        for inside in chart["inside"]:
            what = (f"an item at line {inside['line']} is nested under" if inside["kind"] == "item"
                    else f"a paragraph at line {inside['line']} continues")
            rows.append({"chart": label, "problem": f"{what} the **{inside['field']}:** field; a field is one "
                                                    "paragraph, so join it to the field or move it below the "
                                                    "specification as a slide bullet, after a blank line"})
    return rows


def _by_role(form):
    if form is None:
        return ""
    needed, optional, _ = CHART_FORMS[form]
    return f" by a role a {form} takes ({', '.join(needed + optional)})"


def _intervals_note(form, column=False):
    """The fix for interval columns on a form that plots values without them; an unnamed column may hold none."""
    needed = CHART_FORMS[form][0] if form else ()
    if "value" not in needed or "lower" in needed:
        return ""
    return (f"; if it holds interval bounds, a {form} draws none, so use a Bar with intervals" if column
            else f"; a {form} draws no intervals, so interval columns need a Bar with intervals")


def _chart_entry(entry):
    """Whether a manifest charts entry records the shaping export applied, in the form export writes it."""
    columns, headers, selection = entry.get("columns"), entry.get("headers"), entry.get("selection")
    where = selection.get("where") if isinstance(selection, dict) and set(selection) == {"where"} else None
    return (isinstance(entry.get("result_id"), str) and bool(_SIMPLE.fullmatch(entry["result_id"]))
            and isinstance(columns, list) and bool(columns) and all(isinstance(c, str) for c in columns)
            and isinstance(headers, list) and len(headers) == len(columns) and all(isinstance(h, str) for h in headers)
            and (selection == "all"
                 or isinstance(selection, dict) and set(selection) == {"first"} and type(selection["first"]) is int
                 and selection["first"] >= 1
                 or isinstance(where, dict) and isinstance(where.get("column"), str)
                 and isinstance(where.get("values"), list) and all(isinstance(v, str) for v in where["values"]))
            and isinstance(entry.get("values"), dict)
            and all(isinstance(codes, dict) and all(isinstance(label, str) for label in codes.values())
                    for codes in entry["values"].values())
            and isinstance(entry.get("percent"), list) and all(isinstance(c, str) for c in entry["percent"])
            and isinstance(entry.get("round"), dict)
            and all(type(p) is int and 0 <= p <= _ROUND_LIMIT for p in entry["round"].values()))


def _chart_difference(actual, expected):
    """Where a chart file's rows first differ from the rows its entry gives, or None when they agree."""
    if actual[:1] != expected[:1]:
        return "its header"
    if len(actual) != len(expected):
        return f"{len(actual) - 1} rows where the selection gives {len(expected) - 1}"
    return next((f"row {index}" for index, (have, want) in enumerate(zip(actual, expected)) if have != want), None)


def _display_difference(entry, saved, display):
    """Which of an entry's headers, value labels, or percent columns differ from what display.toml now gives
    for its result and selected rows, or None. Its places can come from --round, so they are not compared."""
    names, values, _ = _labels(display, entry["result_id"])
    own_percent = display["results"].get(entry["result_id"], {}).get("percent")
    percent = display["percent"] if own_percent is None else own_percent
    selected = _select(saved, entry["selection"])
    labels = {}
    for column in entry["columns"]:
        codes = values.get(column, {})
        if used := {row[column]: codes[row[column]] for row in selected if row[column] in codes}:
            labels[column] = used
    if entry["headers"] != [names.get(column) for column in entry["columns"]]:
        return "headers"
    if entry["values"] != labels:
        return "value labels"
    if entry["percent"] != [column for column in entry["columns"] if column in percent]:
        return "percent columns"
    return None


def chart_file_problems(root, investigation, draft, record) -> list[dict]:
    """Match each chart file with the manifest's charts entry export recorded for it, the entry's headers,
    value labels, and percent columns with what foundation/display.toml gives, and the file with its result's
    saved table under that entry's selection, value labels, percent columns, and rounding: {"chart",
    "problem"}. The numbers check is separate: every plotted value is still a recorded value."""
    charts = record.get("charts")
    entries = [] if charts is None or charts == "none" else charts
    if not isinstance(entries, list) or not all(isinstance(e, dict) and isinstance(e.get("path"), str)
                                                for e in entries):
        return [{"chart": None, "problem": "the manifest's charts is not none or a list of the entries export "
                                           "writes; rerun export"}]
    directory = Path(draft) / "charts"
    files = sorted((int(match[1]), path) for path in (directory.iterdir() if directory.is_dir() else ())
                   if (match := _CHART_FILE.fullmatch(path.name)))
    recorded = {}
    for entry in entries:
        recorded.setdefault(entry["path"], entry)
    rows = [{"chart": f"Chart {number}", "problem": f"{path.name} is not in the manifest's charts; export writes "
                                                   "every chart file, so rerun export with its --chart"}
            for number, path in files if f"charts/{path.name}" not in recorded]
    present = {f"charts/{path.name}": path for _, path in files}
    display = None
    for name, entry in recorded.items():
        match = re.fullmatch(r"charts/" + _CHART_FILE.pattern, name)
        label = f"Chart {match[1]}" if match else name
        if name not in present:
            rows.append({"chart": label, "problem": f"the manifest's charts lists {name}, which the draft lacks; "
                                                    "rerun export"})
            continue
        file = present[name].name
        if not _chart_entry(entry):
            rows.append({"chart": label, "problem": f"the manifest's charts entry for {file} records no selection, "
                                                    "columns, headers, value labels, percent, or rounding; rerun "
                                                    "export with every --chart to record them (a --result-only "
                                                    "export keeps this entry)"})
            continue
        table = Path(root) / "investigations" / investigation / "results" / f"{entry['result_id']}.csv"
        try:
            available, saved = _read_table(table)
            with present[name].open(newline="", encoding="utf-8") as stream:
                actual = list(csv.reader(stream))
        except (OSError, UnicodeError, csv.Error) as error:
            rows.append({"chart": label, "problem": f"{file} cannot be checked against {_rel(root, table)}: {error}"})
            continue
        lacking = [column for column in entry["columns"] if column not in available]
        if not lacking:
            if display is None:
                try:
                    display = display_names(root)
                except (ValueError, ImportError) as error:
                    return rows + [{"chart": None, "problem": f"chart files cannot be checked: {error}"}]
            if part := _display_difference(entry, saved, display):
                rows.append({"chart": label, "problem": f"the manifest's charts entry for {file} records {part} "
                                                        f"other than {_DISPLAY} gives; rerun export, which "
                                                        "records them"})
                continue
        detail = (f"its saved table has no column {lacking[0]!r}" if lacking
                  else _chart_difference(actual, [entry["headers"]] + _apply(saved, entry)))
        if detail:
            rows.append({"chart": label, "problem": f"{file} differs from {entry['result_id']} under its recorded "
                                                    f"selection, rounding, and labels ({detail}); rerun export, and "
                                                    "select rows with --chart rather than editing the file"})
    return rows


# ---------------------------------------------------------------- check-draft

def storyline_problems(root, investigation, draft, represented, provenance, order="none"):
    """Accepted input: the outline reader's Markdown subset (references/helpers.md), with ### finding headlines matched
    exactly to ### methodology headings. The matching section names represented results using
    the existing _cited grammar (bounded result IDs or evidence/<ID>.json links, outside
    comments). Only those results' recorded settings `answers` supply ledger question IDs.

    Missing citations or empty answers are reported in unlinked_findings and sort last; no
    fallback infers answers from prose or from other represented results. A result without
    evidence has no declared linkage and is reported as unlinked, preserving the package's
    existing handling of provenance gaps. Malformed settings
    or ledgers raise an error. Known limits: a literal result ID mentioned in methodology counts
    as a citation; the reader cannot judge whether that evidence supports the audience's claim.
    Ties keep the author's slide order. Existing markdown/headings checks refuse unsupported
    Markdown and missing/repeated methodology headings.

    A row names each slide outside the longest run of finding slides already in order, so moving
    one slide reports that slide alone rather than every slide it shifted. The main sequence's finding
    slides and the appendix's each follow the ledger order, the appendix numbering on from the main.

    `order` is the manifest's presentation_order. When it is a list it decides the order instead: each
    entry is a finding slide's heading, read as inline Markdown as the heading is, and the list holds
    every finding slide, main and appendix, exactly once, in deck order. A list entry that is not
    non-blank text makes the whole field malformed, as does any other value, JSON null included; absent
    and "none" leave the ledger order in force.
    """
    tree = provenance.question_tree(root, investigation)
    ranks = {q["id"]: (("must", "should", "could").index(q["priority"]), position)
             for position, q in enumerate(tree)}
    sections = {}
    for level, heading, _, lines in _regions(_read_view(draft / "methodology.md")[0]):
        if level == 3:
            sections.setdefault(heading, []).extend(" ".join([line.plain, *line.links]) for line in lines)
    slides = [s for s in read_outline(draft / "findings.md")["slides"] if s["finding"]]
    ranked, unlinked, answers = [], [], {}
    for slide in slides:
        cited = _cited("\n".join(sections.get(slide["heading"], [])), represented)
        questions = set()
        for result in cited:
            if result not in answers:
                answers[result] = provenance.result_answers(root, investigation, result)
            questions.update(answers[result])
        question = min(questions, key=ranks.__getitem__) if questions else None
        if question is None:
            unlinked.append(slide["heading"])
        ranked.append((ranks[question] if question else (3, 0), slide, question))
    if order != "none":
        return _order_problems(order, [slide for _, slide, _ in ranked]), unlinked
    main = [entry for entry in ranked if not entry[1]["appendix"]]
    behind = [entry for entry in ranked if entry[1]["appendix"]]
    rows = []
    for part, offset in ((main, 0), (behind, len(main))):
        rows += [{**row, "question": part[index][2],
                  "problem": f"finding slide is out of place; move it to finding position {row['expected_position']}"}
                 for index, row in _misplaced([rank for rank, _, _ in part], [s for _, s, _ in part], offset)]
    return rows, unlinked


def _misplaced(ranks, slides, offset=0):
    """(index, row) for each slide outside the longest run already in rank order, positions counted from offset."""
    ordered = sorted(range(len(ranks)), key=ranks.__getitem__)
    positions = {index: position for position, index in enumerate(ordered, offset + 1)}
    in_order = _longest_ordered_run(ranks)
    return [(index, {"slide": slide["heading"], "line": slide["line"], "position": offset + index + 1,
                     "expected_position": positions[index]})
            for index, slide in enumerate(slides) if index not in in_order]


def _order_problems(order, slides):
    """Rows for a presentation_order that is malformed, misses or repeats a finding slide, names a heading no
    finding slide has, or that the finding slides, in deck order, do not follow."""
    if not isinstance(order, list) or not all(isinstance(entry, str) and entry.strip() for entry in order):
        return [{"slide": None, "line": None, "problem": "presentation_order is not none or a list of finding "
                                                         "headings; record the approved order, or none"}]
    listed = Counter(_collapse(_shown(_inline(entry)[0])) for entry in order)
    headings = {slide["heading"] for slide in slides}
    rows = []
    for heading, count in listed.items():
        if count > 1:
            rows.append({"slide": heading, "line": None,
                         "problem": f"presentation_order lists this heading {count} times; keep it once"})
        if heading not in headings:
            rows.append({"slide": heading, "line": None, "problem": "presentation_order names no finding slide with "
                                                                    "this heading; give the slide's current heading "
                                                                    "or remove it"})
    rows += [{"slide": slide["heading"], "line": slide["line"], "problem": "presentation_order does not list this "
              "finding slide; add its heading where the user placed it"}
             for slide in slides if slide["heading"] not in listed]
    rank = {heading: index for index, heading in enumerate(listed)}
    placed = [slide for slide in slides if slide["heading"] in rank]
    return rows + [{**row, "problem": "finding slide is out of place in presentation_order; move it to finding "
                                      f"position {row['expected_position']}"}
                   for _, row in _misplaced([rank[slide["heading"]] for slide in placed], placed)]


def _longest_ordered_run(ranks):
    """Indices of a longest non-decreasing subsequence of ranks: the slides that can stay where they are."""
    tails, previous = [], [None] * len(ranks)  # tails[k]: index ending the best run of length k + 1
    for i, rank in enumerate(ranks):
        k = bisect.bisect_right([ranks[t] for t in tails], rank)
        previous[i] = tails[k - 1] if k else None
        tails[k:k + 1] = [i]
    kept, i = set(), tails[-1] if tails else None
    while i is not None:
        kept.add(i)
        i = previous[i]
    return kept


def open_question_problems(root, investigation, draft, provenance, *, names, roots):
    """Accepted input: exactly one ## Open questions slide iff required questions exist,
    immediately after ## Limitations and open caveats (or, with that slide under ## Appendix, after the
    last main finding, Implications, or How we know slide) and before ## What changed since the
    last version when present. Its body is top-level Markdown list items (bullet or numbered,
    inline markup and wrapped continuations as the existing outline reader accepts), exactly
    each required question's audience wording when set, otherwise its text, rendered by
    _inline/_shown with whitespace collapsed, once each.

    Required means priority must and status open, parked, or answered (awaiting recheck).
    Declined and superseded questions are set aside. Nested bullets, charts, missing/repeated
    questions and any other bullet text are reported; outline/markdown checks report other
    structural forms. Known limits: this compares rendered text, not paraphrases or audience
    suitability. Question IDs and added owner commentary do not match; audience wording (or
    text when unset) must be single-line inline text. When unset text fails the names check,
    a row directs the caller to questions edit --audience; that scan skips any part of the text the
    outline reader refuses, which the slide's own names check still covers. Block markup/comments in that wording
    are not an alternate matching form. Notes remain presenter context and do not satisfy a question.
    """
    questions = [q for q in provenance.question_tree(root, investigation) if q["priority"] == "must"
                 and q["display_status"] in ("open", "parked", provenance.AWAITING_RECHECK)]
    expected = Counter(_collapse(_shown(_inline(q["audience"] or q["text"])[0])) for q in questions)
    slides = read_outline(draft / "findings.md")["slides"]
    opened = [(i, slide) for i, slide in enumerate(slides) if not slide["finding"] and slide["heading"] == "Open questions"]
    rows = []

    def row(problem, line=None, **details):
        rows.append({"slide": "Open questions", "line": line, "problem": problem, **details})

    pattern = _name_pattern(names)
    for question in questions:
        if not question["audience"] and _scan_paragraph(_view(question["text"])[0], set(roots) | set(names), pattern):
            row(f'use audience wording: questions edit {question["id"]} --audience "<wording>"',
                question=question["text"])

    if not expected:
        if opened:
            row("no unanswered must questions; omit the Open questions slide", opened[0][1]["line"])
        return rows, len(questions)
    if not opened:
        row("missing Open questions slide; list every unanswered must question")
        return rows, len(questions)
    if len(opened) != 1:
        row("keep exactly one Open questions slide", opened[1][1]["line"])
    # With Limitations under ## Appendix, Open questions stands where it would have: after the last main
    # finding, Implications, or How we know slide.
    limitations = "Limitations and open caveats"
    if any(not s["appendix"] and s["heading"] == limitations for s in slides):
        anchors = [i for i, s in enumerate(slides) if s["heading"] == limitations]
    else:
        anchors = [i for i, s in enumerate(slides) if not s["appendix"]
                   and (s["finding"] or s["heading"] in ("Implications", "How we know"))][-1:]
    for position, slide in opened:
        if position - 1 not in anchors:
            row("place Open questions immediately after Limitations and open caveats, or, with that slide in the "
                "appendix, immediately after the last finding, Implications, or How we know slide", slide["line"])
        if any(s["heading"] == "What changed since the last version" for s in slides[:position]):
            row("place Open questions before What changed since the last version", slide["line"])
        actual = Counter(b["text"] for b in slide["bullets"])
        for text, count in expected.items():
            if actual[text] < count:
                row("missing question", slide["line"], question=text)
        for text, count in actual.items():
            if not expected[text]:
                row("unexpected question or commentary; use the exact rendered ledger text", slide["line"], question=text)
            elif count > expected[text]:
                row("repeated question; list each required question once", slide["line"], question=text)
        for bullet in slide["bullets"]:
            if bullet["sub"]:
                row("nested bullets are not accepted; list questions as top-level bullets", bullet["line"])
        if slide["charts"]:
            row("Open questions takes no chart; list questions as top-level bullets", slide["charts"][0]["line"])
    return rows, len(questions)


# A deck naming itself unfinished: the word draft, or the phrase working copy or not a numbered release, in any
# case and as whole words, so drafted, redraft, and working copies are not markers.
_DRAFT_MARKER = re.compile(r"(?<!\w)(?:draft|working\s+copy|not\s+a\s+numbered\s+release)(?!\w)", re.IGNORECASE)


def draft_markers(findings_path: str | os.PathLike) -> list[dict]:
    """Each draft marker in the places a deck names its own status, as they render: the title, the subtitle,
    each slide's heading and **Headline:** text, and the title slide's notes, as {"where", "line", "marker",
    "text"}. Bullets, charts, and other slides' notes are not read. The rows are informational: a release
    copies the draft byte for byte, so awb-release shows them and the user confirms or revises the wording."""
    outline = read_outline(findings_path)
    title, places = outline["title"], []
    if title is not None:
        places.append(("title", title["line"], title["text"]))
        if title["subtitle"]:
            places.append(("subtitle", title["subtitle_line"], title["subtitle"]))
        if title["notes"]:
            places.append(("title notes", title["notes_lines"][0], title["notes"]))
    for slide in outline["slides"]:
        places.append(("heading", slide["line"], slide["heading"]))
        places += [("headline", headline["line"], headline["text"]) for headline in slide["headlines"]]
    return [{"where": where, "line": line, "marker": match[0], "text": text}
            for where, line, text in places for match in _DRAFT_MARKER.finditer(text or "")]


# The note check-draft writes at the top of the draft, so whoever holds the package or a release knows which
# files go to the audience, which build the deck, and which stay internal. check-draft, not export, writes it:
# export runs before the narratives and any methodology note are final, and check-draft runs last.
START_HERE = "START-HERE.md"
# The one-line prompt assembly/m365.md gives the requester; the two stay word for word the same.
M365_PROMPT = "Build a PowerPoint deck from findings.md and the chart files, following deck-rules.md and m365.md."


def start_here(draft, investigation, package) -> str:
    """START-HERE.md's plain text for a draft as it now stands: send these to your audience (the deck once
    built, methodology-note.md when present, each file under datasets/); to build the deck (the attach list
    and prompt assembly/m365.md gives, each chart file named); internal (methodology.md, manifest.json,
    deck-rules.md)."""
    draft = Path(draft)
    charts = sorted((int(match[1]), path.name) for path in
                    ((draft / "charts").iterdir() if (draft / "charts").is_dir() else ())
                    if (match := _CHART_FILE.fullmatch(path.name)))
    # Every dataset file but a hidden one, such as a file manager's .DS_Store, goes to the audience.
    datasets = sorted(path.relative_to(draft).as_posix() for path in
                      ((draft / "datasets").rglob("*") if (draft / "datasets").is_dir() else ())
                      if path.is_file() and not path.name.startswith("."))
    audience = ["the deck, once you build it as part 2 says"]
    if (draft / METHODOLOGY_NOTE).is_file():
        audience.append(f"{METHODOLOGY_NOTE}, a plain account of how the analysis was done")
    attach = ["findings.md", *(f"charts/{name}" for _, name in charts), "methodology.md", "deck-rules.md",
              "assembly/m365.md"]
    # Plain text, a blank line after each list, so a viewer that renders Markdown joins no line to a list item.
    lines = ["Start here", "",
             f"This folder is the {package} package of the {investigation} investigation. Its files fall into "
             "three parts.", "",
             "1. Send these to your audience", "", *(f"- {item}" for item in audience + datasets), "",
             "2. To build the deck", "",
             "In a Microsoft 365 Copilot app chat, add the PowerPoint agent and attach these files:", "",
             *(f"- {path}" for path in attach), "", "Then send this prompt:", "", M365_PROMPT, "",
             "3. Internal: keep these, and do not send them", "",
             "- methodology.md, the full account of the analysis",
             "- manifest.json, the record of what this package holds and what produced it",
             "- deck-rules.md, the rules the deck is built by", "",
             "The other files in part 2 are the deck's source; your audience gets the deck instead."]
    return "\n".join(lines) + "\n"


def _write_start_here(draft, investigation, package):
    path, text = Path(draft) / START_HERE, start_here(draft, investigation, package)
    try:
        current = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        current = None
    if current != text:
        _write_text(path, text)


# The brief's Audience line that records a methods note length, in its one written form, and any line that
# starts like it, so a length recorded in another form is reported rather than read as none.
_NOTE_LENGTH = re.compile(r"(?:[-*+]\s+)?Methods note length: about ([0-9]+) words\.?")
_NOTE_LENGTH_LIKE = re.compile(r"\s*(?:[-*+]\s+)?\**methods\s+note\s+length", re.IGNORECASE)
# How far the note may run over the recorded length before the row: 10%, as integer tenths.
_NOTE_SLACK_TENTHS = 11


def note_length_problems(root, investigation, draft) -> list[dict]:
    """A row when methodology-note.md runs more than 10% over the length the investigation's brief.md
    records on a `Methods note length: about <n> words` line, or when a line that starts like one is not in
    that form or two such lines disagree; no row without a note or a recorded length. Words are counted as
    the note renders: headings, text, and list items, not comments or fenced code. Informational, like
    slides: it never fails the check."""
    note = Path(draft) / METHODOLOGY_NOTE
    if METHODOLOGY_NOTE not in _narratives(draft):
        return []
    try:
        lines = _read_lines(Path(root) / "investigations" / investigation / "brief.md")
    except FileNotFoundError:
        return []
    brief = f"investigations/{investigation}/brief.md"
    rows, lengths = [], {}
    for number, line in enumerate(lines, 1):
        if not _NOTE_LENGTH_LIKE.match(line):
            continue
        match = _NOTE_LENGTH.fullmatch(line.strip())
        if match:
            lengths.setdefault(int(match[1]), number)
        else:
            rows.append({"file": brief, "line": number, "problem": "the methods note length is not written as "
                                                                  "`Methods note length: about <n> words`"})
    if len(lengths) > 1:
        rows.append({"file": brief, "line": sorted(lengths.values())[1],
                     "problem": f"the brief records more than one methods note length: {sorted(lengths)}"})
    if len(lengths) == 1:
        (recorded, number), = lengths.items()
        words = sum(_words(line.plain) for line in _read_view(note)[0])
        if words * 10 > recorded * _NOTE_SLACK_TENTHS:
            rows.append({"file": METHODOLOGY_NOTE, "words": words, "recorded": recorded,
                         "problem": f"the note runs {words} words, more than 10% over the about {recorded} words "
                                    f"{brief}:{number} records; shorten it, or report the length to the user"})
    return rows


def _structure_passed(report):
    return (not report["names_problems"] and not report["errors"] and report["findings"] == []
            and report["outline"] == [] and report["charts"] == [] and report["headings"] == [] and report["markdown"] == []
            and report["claims"] == [] and report["questions"] == []
            and report["storyline"] == [] and report["open_questions"] == []
            and report["verify"] == [] and report["flag_entries"] == [] and report["numbers"] == []
            and not report["numbers_problems"])


def check_draft(root, investigation, package, *, verify_only=False) -> dict:
    """Run every mechanical draft check; unless verify_only, write START-HERE.md and rewrite the manifest's
    inventory."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"draft": _rel(root, draft), "names": 0, "names_problems": [], "findings": None,
              "outline": None, "slides": None, "charts": None, "headings": None, "markdown": None, "claims": None, "questions": None,
              "storyline": None, "unlinked_findings": None, "open_questions": None, "open_questions_count": None,
              "numbers": None, "numbers_problems": [], "inventory": None, "verify": None,
              "flag_entries": None, "unmatched_flags": None, "draft_markers": None, "note_length": None,
              "start_here": None, "review": None, "errors": [], "passed": False}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {report['draft']}; create it with awb-package")
        return report

    recorded, report["names_problems"] = _recorded_names(root, investigation, package)
    names = sorted(name for name in recorded if not _PLAIN_WORD.fullmatch(name))
    report["names"] = len(names)
    findings_path = draft / "findings.md"
    try:
        report["findings"] = check_findings(findings_path, names=names, roots=recorded)
        if METHODOLOGY_NOTE in _narratives(draft):
            report["findings"] += [{"file": METHODOLOGY_NOTE, **row} for row in
                                   check_findings(draft / METHODOLOGY_NOTE, names=names, roots=recorded)]
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"findings check: {error}")
    try:
        report["outline"] = outline_problems(findings_path)
        report["slides"] = read_outline(findings_path)["counts"]
        report["draft_markers"] = draft_markers(findings_path)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"outline check: {error}")
    try:
        report["charts"] = check_charts(findings_path, draft / "charts")
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"charts check: {error}")
    try:
        report["note_length"] = note_length_problems(root, investigation, draft)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"note length check: {error}")
    try:
        report["headings"] = heading_problems(draft)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"headings check: {error}")
    try:
        report["markdown"] = markdown_problems(draft)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"markdown check: {error}")
    # Without findings.json the table renders empty, so any row is drift.
    provenance = None  # loaded once; the ledger checks below reuse it
    try:
        provenance = _load_provenance(root)
        if not hasattr(provenance, "findings_drift"):
            raise ValueError("src/provenance.py predates findings.json; run awb-init repair: "
                             "install_helpers.py --upgrade")
        drift = provenance.findings_drift(root, investigation)
        if drift:
            report["errors"].append(f"findings drift: {drift}; restore with python3 src/awb.py state render "
                                    f"--investigation {investigation}")
    except (OSError, ValueError) as error:
        report["errors"].append(f"findings drift: {error}")
    if provenance is not None:
        try:
            report["open_questions"], report["open_questions_count"] = open_question_problems(
                root, investigation, draft, provenance, names=names, roots=recorded)
        except (OSError, ValueError, AttributeError) as error:
            report["errors"].append(f"open questions check: {error}")
    try:
        flags = state_flags(root, investigation)
    except ValueError as error:
        flags = None
        report["errors"].append(f"flags: {error}")
    try:
        claims = state_claims(root, investigation)
    except ValueError as error:
        claims = None
        report["errors"].append(f"claims: {error}")

    record, claim_lines = None, set()
    try:
        path = draft / MANIFEST
        if not path.is_file():
            raise ValueError(f"no manifest at {_rel(root, path)}; run export first")
        record = _read_json(path)
        report["flag_entries"] = flag_entry_problems(record)
        if report["charts"] is not None:
            try:
                report["charts"] += chart_file_problems(root, investigation, draft, record)
            except OSError as error:
                report["errors"].append(f"charts check: {error}")
        try:
            report["questions"] = question_problems(draft, record)
        except (OSError, UnicodeError) as error:
            report["errors"].append(f"questions check: {error}")
        represented = record.get("results")
        if not isinstance(represented, list) or not all(
                isinstance(r, dict) and isinstance(r.get("result_id"), str) for r in represented):
            raise ValueError(f"{MANIFEST} records no results list; rerun export")
        if claims is not None:
            try:
                report["claims"], claim_lines = _claim_review(draft, [r["result_id"] for r in represented], claims)
            except (OSError, UnicodeError) as error:
                report["errors"].append(f"claims check: {error}")
        if provenance is not None:
            try:
                report["storyline"], report["unlinked_findings"] = storyline_problems(
                    root, investigation, draft, [r["result_id"] for r in represented], provenance,
                    record.get("presentation_order", "none"))
            except (OSError, ValueError, AttributeError) as error:
                report["errors"].append(f"storyline check: {error}")
        if not verify_only:
            _write_start_here(draft, investigation, package)  # before the inventory, which then lists it
            rows = inventory(draft)
            if rows != record.get("inventory"):
                record.update(inventory=rows, revised_at=_now())
                _write_json(path, record)
        elif not isinstance(record.get("inventory"), list):
            raise ValueError(f"{MANIFEST} records no inventory list; run check-draft without --verify-only")
        elif not (draft / START_HERE).is_file():
            # Every release includes it; an inventory recorded before it was written would not miss it.
            report["errors"].append(f"{START_HERE}: the draft lacks it; run check-draft without --verify-only, "
                                    "which writes it and records it in the inventory")
        report["inventory"] = {"rows": len(record["inventory"]),
                               "source": "recorded" if verify_only else "rewritten"}
        report["verify"] = verify(draft, record["inventory"])
        if flags is not None:
            report["unmatched_flags"] = unmatched_flags(record, flags)
    except (OSError, ValueError) as error:
        report["errors"].append(f"manifest: {error}")
    if (draft / START_HERE).is_file():
        report["start_here"] = _rel(root, draft / START_HERE)

    # Every number in any narrative traces to a represented result or is allowed with a reason; a Claim
    # strength line the claims check accepts repeats state.md and is skipped.
    if record is not None:
        allowed, problems = allowed_numbers(record)
        values, more = recorded_values(root, investigation, record.get("results"))
        report["numbers_problems"], report["numbers"] = problems + more, []
        for name in _narratives(draft):
            try:
                report["numbers"] += check_numbers(draft / name, values, allowed=allowed,
                                                   claim_lines=claim_lines if name == "methodology.md" else ())
            except (OSError, UnicodeError) as error:
                report["errors"].append(f"numbers check: {error}")

    # Informational: the last review against these files, read after any write above, as release reads it.
    review = review_receipt(root, investigation, package)
    report["review"] = {"status": review["status"], "changed": review["changed"]}
    report["passed"] = _structure_passed(report) and report["unmatched_flags"] == []
    return report


def _package_arguments(parser, *, package=True):
    parser.add_argument("investigation", help="investigation name under investigations/")
    if package:
        parser.add_argument("package", help="package name under deliveries/<investigation>/")


def cli_check_draft(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py check-draft", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run every mechanical draft check (internal names in findings.md and any methodology-note.md, "
                    "the slide rules and required slides, the finding order and Open questions, chart specifications "
                    "and files, "
                    "matching finding headings, the Markdown subset, causal wording against claim strength, "
                    "each represented result's question in methodology.md, numbers in the narratives, the "
                    "manifest inventory, and state.md's current flags), write START-HERE.md, and rewrite the "
                    "manifest inventory, stamping revised_at when it changes; --verify-only checks a release "
                    "candidate and writes nothing.",
        epilog="Prints one JSON line.\nmethodology-note.md, when the draft holds it, is read by the findings, "
               "claims, markdown, and numbers checks too; its rows carry file.\n"
               "outline lists, as slide, line, and problem, each break of the slide "
               "rules: a missing # title or subtitle, text outside every slide, a ### finding outside ## Findings "
               "and ## Appendix, "
               "a missing, repeated, empty, or over-15-word headline, more than five bullets except on Open questions, more than one chart, "
               "text that is no headline, bullet, chart, or notes, and a missing, repeated, or non-final **Notes:** "
               "paragraph; a missing, repeated, or misplaced required slide (Answer first after the title, a finding "
               "slide in the main sequence, then How we know and Limitations and open caveats, either of which may "
               "stand under ## Appendix instead, How we know first when both stand in the main sequence or both "
               "under ## Appendix), its line null when missing; and a slide after ## Appendix outside it, a second "
               "## Appendix, an appendix slide that stays in the main sequence, or an empty ## Appendix. slides "
               "counts the main sequence's slides, title included, and the appendix's.\nstoryline lists the "
               "finding slides to move, those outside the longest run already in priority/tree order, the main "
               "sequence and the appendix each ranked alone, each with its expected position; when the manifest's "
               "presentation_order is a list it ranks every finding slide instead, and storyline also lists a "
               "malformed order, a heading it repeats or that no finding slide has, and a finding slide it misses. "
               "unlinked_findings names slides with no declared ledger answer, which go last without a "
               "presentation_order; it is informational.\n"
               "open_questions lists presence, placement, and exact-question-bullet problems on Open questions; "
               "open_questions_count is the required count, including parked questions and answers awaiting recheck.\n"
               "charts lists, as chart and problem, a specification numbered out of order, without "
               "a file, or without a form from deck-rules.md; a **Data:** line missing, malformed, or not naming "
               "its form's roles; a column it names that the file lacks, and a column of the file that it names by "
               "no role; an item nested under a field or a second paragraph in one; and a chart file without a "
               "specification or data rows, or a foreign file. It also lists each chart file the manifest's "
               "charts does not record, an entry whose file is missing or that records no selection, columns, "
               "headers, value labels, percent, or rounding, an entry whose headers, value labels, or percent "
               "columns differ from what foundation/display.toml gives, and a file that differs from its result's saved "
               "table under that entry's selection, labels, percent columns, and rounding (export writes every "
               "chart file; rows are selected with --chart, never by editing the file).\nclaims lists each causal phrase (line, section, phrase, claim, results) "
               "in a findings.md slide, heading included, above its claim strength: a ### finding slide is held to the weakest "
               "Claim in state.md among the results its methodology.md section cites (all represented results "
               "when it cites none), and the title and other slides that state conclusions to the strongest; "
               "How we know, Limitations and open caveats, Open questions, What changed since the last version, and Supporting "
               "datasets are not read, under ## Appendix too; methodology-note.md is held to the strongest. It also lists a represented result without a recognized Claim, and a "
               "finding whose methodology.md section is missing or whose **Claim strength:** line is missing, "
               "repeated, unrecognized, or differs from state.md, a causal design included.\nheadings lists a ### "
               "finding heading without exactly one methodology.md section or repeated in findings.md.\nmarkdown "
               "lists each form outside the Markdown subset the checks read, which could hide text or move "
               "it between slides: a heading, fence, comment, or **Claim strength:** line inside a list or quote; "
               "an indented fence or comment; a setext heading; indented code; an HTML block or inline tag; a link "
               "reference definition; an unclosed fence or comment. Every check but numbers reads the narratives "
               "as they render."
               "\nnumbers lists, as file, line, and text, each number in findings.md, methodology.md, or "
               "methodology-note.md that no represented result's table, profile, check details, or settings round "
               "to and the manifest's allowed_numbers does not cover by its text or a phrase around it, reading "
               "source lines without the comments and fenced code the rendered reading drops, so a <!-- in a code "
               "span, fenced code, or a link's target, or escaped, hides nothing, and skipping a methodology.md "
               "**Claim strength:** line the claims check accepts, whose numbers repeat state.md's Claim cell; "
               "numbers_problems names "
               "a missing table, an unreadable table, profile, or evidence file, or a malformed results or "
               "allowed_numbers.\n"
               "unmatched_flags lists each finding state.md flags whose exact finding and reason the manifest's "
               "revalidation_flags does not record.\nflag_entries lists a "
               "missing or malformed revalidation_flags, an entry without text finding and reason, represented_in "
               "that is neither none nor a list of places, and an unknown disposition.\nquestions lists each "
               "manifest results entry without a question, or whose question methodology.md does not repeat "
               "verbatim within one paragraph or heading as it renders, the question read as written or rendered the "
               "same way: a code span counts, and a question in a comment, fenced code, or an image's text does "
               "not count, nor does one running across an image.\n"
               "review is the last recorded review against these files, as review-receipt show gives its status "
               "(none, current, stale, or failed) and changed; it is informational, and release refuses unless "
               "it is current.\n"
               "draft_markers lists, as where, line, marker, and text, the word draft or the phrase working copy "
               "or not a numbered release, any case, whole words, in the title, subtitle, a slide heading or "
               "**Headline:**, or the title slide's notes; it is informational, since a release copies the draft "
               "byte for byte, so awb-release asks the user to confirm or revise each before releasing.\n"
               "note_length lists, when the investigation's brief.md records `Methods note length: about <n> "
               "words`, a methodology-note.md more than 10% longer as it renders, with words and recorded, and a "
               "brief line that starts like that one but is not in its form, or a second length; it is "
               "informational, and empty without a note or a recorded length.\n"
               "Without --verify-only it first writes START-HERE.md, plain text in three parts: what to send the "
               "audience (the deck once built, methodology-note.md, each dataset), what builds the deck (the "
               "attach list and prompt assembly/m365.md gives), and what stays internal; the inventory then lists "
               "it, and --verify-only verifies it like any other file and lists an errors row when the draft lacks "
               "it. start_here names it when present.\n"
               "Exit 0 only when names_problems, findings, outline, charts, "
               "headings, markdown, claims, "
               "questions, storyline, open_questions, numbers, numbers_problems, verify, flag_entries, unmatched_flags, and errors "
               "are all empty.")
    _package_arguments(parser)
    parser.add_argument("--verify-only", action="store_true",
                        help="verify against the recorded inventory without rewriting it (the release gate)")
    args = parser.parse_args(argv)
    report = check_draft(Path(root), _simple(args.investigation, "investigation"),
                         _simple(args.package, "package"), verify_only=args.verify_only)
    _print(report)
    return 0 if report["passed"] else 1


# ---------------------------------------------------------------- producing and packaging state

def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE).stdout.decode()


def packaging_state(root, paths=("src", "package-format")) -> tuple:
    """Return the packaging checkout's commit and its uncommitted package-source paths."""
    try:
        if _git(root, "rev-parse", "--is-inside-work-tree").strip() != "true":
            raise ValueError
    except (OSError, ValueError, subprocess.CalledProcessError):
        unknown = {"unknown": "the project is not a git repository"}
        return unknown, unknown
    try:
        commit = _git(root, "rev-parse", "--verify", "HEAD").strip()
    except subprocess.CalledProcessError:
        commit = {"unknown": "the checkout has no commit yet"}
    prefix = _git(root, "rev-parse", "--show-prefix").strip()
    changes = []
    entries = iter(_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                        "--", *paths).split("\0"))
    for entry in entries:
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            next(entries, None)
        changes.append({"path": path.removeprefix(prefix), "status": status.strip()})
    return commit, changes or "none"


def _single(values):
    """One value when every result agrees; otherwise each distinct value with its results."""
    groups = {}
    for result_id, value in values.items():
        groups.setdefault(json.dumps(value, sort_keys=True), (value, []))[1].append(result_id)
    if len(groups) == 1:
        return next(iter(groups.values()))[0]
    return [{"results": results, "value": value} for value, results in groups.values()]


def _union(values):
    """Every distinct entry across results, each naming the results that recorded it."""
    rows = {}
    for result_id, entries in values.items():
        for entry in [entries] if not isinstance(entries, list) else entries:
            key = json.dumps(entry, sort_keys=True)
            rows.setdefault(key, {**entry, "results": []} if isinstance(entry, dict)
                            else {"value": entry, "results": []})["results"].append(result_id)
    return list(rows.values())


def producing_state(evidence: dict) -> dict:
    """Map {result_id: awb-evidence record} to the manifest's producing-state fields."""
    field = lambda key: {r: e.get(key, {"unknown": f"evidence lacks {key}"}) for r, e in evidence.items()}
    commits = field("producing_commit")
    changes = {r: v for r, v in field("producing_uncommitted_changes").items() if v != []}
    return {
        "producing_commit": _single(commits),
        "producing_uncommitted_changes": _union(changes) if changes else "none",
        "inputs": {"publications": _union(field("publications")),
                   "acquisitions": _union(field("acquisitions")),
                   "views": _union(field("views"))},
        "analytical_settings": _single(field("settings")),
    }


def _load_provenance(root):
    path = Path(root) / "src/provenance.py"
    if not path.is_file():
        raise FileNotFoundError("src/provenance.py is missing; install it from the awb-init skill")
    spec = importlib.util.spec_from_file_location("awb_project_provenance", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- export

_DISPLAY = "foundation/display.toml"
_DISPLAY_KEYS = ("columns", "values", "round", "percent", "results")
# A number cell: an optional sign, digits with an optional decimal point, and an optional exponent, as a CSV
# writer writes a number. Other text, a thousands separator, NaN, and infinity included, is shown as written.
_NUMBER_CELL = re.compile(r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?")
# A number shown with more decimal places than this, trailing zeros aside, needs [round] places; see `_unrounded`.
UNROUNDED_PLACES = 4
_ROUND_LIMIT = 20
_CHART_FORM = "RESULT[:COLUMNS][@first=<n>|@where=<column>=<value>[,<value>]]"
_COLLISION = ("results answering different questions share this [columns] name; confirm it fits each, "
              "or name the column for one result under [results.\"<result>\".columns]")


def _table(value, problem):
    if not isinstance(value, dict):
        raise ValueError(f"{_DISPLAY}: {problem}")
    return dict(value)


def _labels_from(record, where):
    """A [columns] table and the [values.<column>] tables, as `where` names them in the file."""
    columns = _table(record.get("columns", {}), f"{where}columns] maps each column to its display name")
    values = _table(record.get("values", {}), f"{where}values.<column>] maps each coded value to a text label")
    for column, codes in values.items():
        if not isinstance(codes, dict) or not all(isinstance(label, str) for label in codes.values()):
            raise ValueError(f"{_DISPLAY}: {where}values.{column}] maps each coded value to a text label")
        values[column] = dict(codes)
    return columns, values


def _percent_from(value, where):
    """A [percent] table's columns list, as `where` names the table in the file."""
    if not (isinstance(value, dict) and set(value) == {"columns"} and isinstance(value["columns"], list)
            and all(isinstance(column, str) and column for column in value["columns"])):
        raise ValueError(f"{_DISPLAY}: {where}percent] holds one key, columns, a list of column names")
    return list(value["columns"])


def display_names(root) -> dict:
    """Return {columns, values, round, percent, results} from foundation/display.toml, empty when it is absent.

    The file holds only [columns] (column: display name), [values.<column>] (coded value: label), [round]
    (column: decimal places), [percent] with one key, columns = [...] (columns whose fractions show 100 times
    larger), and [results."<result>"] tables holding columns, values, and percent tables, which replace the
    global ones for that result's files, a values table for its whole column and a percent table for every
    column. A result without a percent table has None there. Anything else raises ValueError. A name or a
    number of places is checked where a column is exported.
    """
    path = Path(root) / _DISPLAY
    try:
        record = _toml().loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ImportError as error:
        raise ImportError(f"reading {path.name} needs Python 3.11 or the tomli package") from error
    for key in record:
        if key not in _DISPLAY_KEYS:
            raise ValueError(f"{_DISPLAY}: unknown key {key!r}; the file holds only [columns], [values.<column>], "
                             "[round], [percent], and [results.\"<result>\"]")
    columns, values = _labels_from(record, "[")
    percent = _percent_from(record.get("percent", {"columns": []}), "[")
    results = {}
    for result_id, entry in _table(record.get("results", {}), "[results.\"<result>\"] holds a columns table, a "
                                                               "values table, and a percent table for one "
                                                               "result").items():
        where = f'[results."{result_id}"'
        if not isinstance(entry, dict) or not set(entry) <= {"columns", "values", "percent"}:
            raise ValueError(f"{_DISPLAY}: {where}] holds only a columns table, a values table, and a percent table")
        own_columns, own_values = _labels_from(entry, where + ".")
        results[result_id] = {"columns": own_columns, "values": own_values,
                              "percent": _percent_from(entry["percent"], where + ".") if "percent" in entry else None}
    return {"columns": columns, "values": values,
            "round": _table(record.get("round", {}), "[round] maps each column to its decimal places"),
            "percent": percent, "results": results}


def parse_chart(text: str) -> tuple:
    """Parse a --chart value into (result_id, [columns] or None, selection), refusing any other text.

    The grammar is closed: RESULT[:COLUMNS][@first=<n>|@where=<column>=<value>[,<value>]]. The first '@'
    opens the row selection, so a column name holding '@' or ',' cannot be named in COLUMNS, though the
    @where column may hold either. Before it, RESULT is a simple name, and the first ':' opens COLUMNS,
    comma-separated names, each stripped of surrounding spaces and none empty. After it, first=<n>, n a
    whole number from 1 to 999999999 written without leading zeros, takes the table's first n rows;
    where=<column>=<value>[,<value>] takes, in table order, the rows
    whose column holds one of the values exactly as the saved table writes it, the column ending at the first
    '=' and stripped, so no value can hold ',' and none may be empty. selection is "all", {"first": n}, or
    {"where": {"column", "values"}}. Anything else raises ValueError naming the part that does not fit.
    """
    def refuse(reason):
        raise ValueError(f"--chart {text!r}: {reason}; write {_CHART_FORM}")

    head, at, selection = text.partition("@")
    result_id, colon, listed = head.partition(":")
    if not _SIMPLE.fullmatch(result_id):
        refuse("the result ID is not a simple name")
    columns = [column.strip() for column in listed.split(",")] if colon else None
    if columns is not None and not all(columns):
        refuse("a column name is empty")
    if not at:
        return result_id, columns, "all"
    kind, equals, rest = selection.partition("=")
    if equals and kind == "first":
        if not re.fullmatch(r"[1-9][0-9]{0,8}", rest):
            refuse("@first takes a whole number of rows from 1 to 999999999, without leading zeros")
        return result_id, columns, {"first": int(rest)}
    if equals and kind == "where":
        column, equals, values = rest.partition("=")
        values = values.split(",")
        if not equals or not column.strip() or not all(values):
            refuse("@where needs a column, =, and values separated by commas, none empty")
        return result_id, columns, {"where": {"column": column.strip(), "values": values}}
    refuse("the row selection is not @first=<n> or @where=<column>=<value>[,<value>]")


def _spec(text, what):
    """Parse a --dataset's RESULT[:COL,COL] into (result_id, [columns] or None)."""
    result_id, _, columns = text.partition(":")
    return _simple(result_id, what), [c.strip() for c in columns.split(",") if c.strip()] or None


def _number(text):
    """Whether a cell is a finite number cell, the only kind a percent or [round] changes. A cell whose
    exponent is too large for a decimal to hold, such as 1e-9999999999999999999, is none: it is written as
    saved, as an overflowing one is."""
    if not (_NUMBER_CELL.fullmatch(text) and math.isfinite(float(text))):
        return False
    try:
        Decimal(text)
    except ArithmeticError:
        return False
    return True


def _unrounded(text, percent=False) -> bool:
    """Whether a cell shows more than UNROUNDED_PLACES decimal places: a finite number cell whose saved text,
    the file's text unless rounded, has more once trailing zeros are dropped, any exponent applied, and a
    percent column's 100-fold scaling applied, so a percent column's saved fraction may carry two more. So
    366.89000039169395 and 1e-05 are unrounded, and 21.3500, which is 21.35, is not; digits beyond a float's
    precision count, since the file shows them."""
    if not _number(text):
        return False
    places = -Decimal(text).normalize(_EXACT).as_tuple().exponent
    return places - (2 if percent else 0) > UNROUNDED_PLACES


def _display_cell(text, labels, percent, places):
    """A saved cell as a file shows it: its value label; else, for a number cell, scaled exactly by 100 in a
    percent column and rounded half up to its places, as a reader would; else as written."""
    if text in labels:
        return labels[text]
    if not _number(text) or not percent and places is None:
        return text
    with localcontext(_EXACT):
        number = Decimal(text).scaleb(2) if percent else Decimal(text)
        if places is not None:
            number = number.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
        return format(number, "f")


def _select(rows, selection):
    """The rows a selection takes from a saved table, in table order."""
    if selection == "all":
        return rows
    if "first" in selection:
        return rows[:selection["first"]]
    where = selection["where"]
    return [row for row in rows if row.get(where["column"]) in where["values"]]


def _apply(rows, entry):
    """A file's data rows from a saved table's rows, as an entry export records shapes them."""
    return [[_display_cell(row[column], entry["values"].get(column, {}), column in entry["percent"],
                           entry["round"].get(column)) for column in entry["columns"]]
            for row in _select(rows, entry["selection"])]


def _read_table(path):
    """A saved result table's header and rows, a short row's missing cells read as empty."""
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = [{key: "" if value is None else value for key, value in row.items() if key is not None}
                for row in reader]
        return list(reader.fieldnames or []), rows


def _display_name(names, column):
    """A column's display name, or None when absent or blank."""
    name = names.get(column)
    return name if isinstance(name, str) and name.strip() else None


def _labels(display, result_id):
    """A result's column names and value labels: its [results."<id>"] tables over the global ones."""
    own = display["results"].get(result_id, {"columns": {}, "values": {}})
    return {**display["columns"], **own["columns"]}, {**display["values"], **own["values"]}, own["columns"]


def _toml_key(name):
    # A quoted key, so a dotted or spaced column stays one key under [columns] or [round].
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + re.sub(r"[\x00-\x1f\x7f]", lambda match: f"\\u{ord(match.group()):04X}", escaped) + '"'


def _shape(root, investigation, result_id, columns, selection, display, rounding, gaps, round_gaps):
    """Shape a saved result table for the audience: (entry, rows, sources, problems).

    entry records the shaping, which check-draft reapplies (`_apply`): the result, its columns, the row
    selection, the headers, the value labels the selected rows use, and the columns shown as percents and
    rounded. sources states it as methodology lines (`_sources`). A column without a display name is
    appended to `gaps`, and an unrounded one without places to `round_gaps`; only the cells the file holds
    count.
    """
    path = Path(root) / "investigations" / investigation / "results" / f"{result_id}.csv"
    if not path.is_file():
        return None, None, None, [f"{_rel(root, path)} is missing. Stop: saving a result table needs "
                                  "separately authorized analytical work"]
    available, table = _read_table(path)
    chosen = columns or available
    names, values, own = _labels(display, result_id)
    unknown = [f"{result_id}: no column {c!r} (has {', '.join(available)})" for c in chosen if c not in available]
    missing = [c for c in chosen if c in available and _display_name(names, c) is None]
    unnamed = [f"{result_id}: column {c!r} has {'a blank' if c in names else 'no'} display name in {_DISPLAY} "
               + (f'[results."{result_id}".columns]' if c in own else "[columns]") for c in missing]
    gaps += [c for c in missing if c not in own]
    unselected = []
    if isinstance(selection, dict) and "where" in selection:
        column, wanted = selection["where"]["column"], selection["where"]["values"]
        if column not in available:
            unselected.append(f"{result_id}: @where names no column {column!r} (has {', '.join(available)})")
        else:
            present = {row[column] for row in table}
            unselected += [f"{result_id}: no row has {column} = {value!r}; @where compares values as the saved "
                           "table writes them" for value in dict.fromkeys(wanted) if value not in present]
    elif isinstance(selection, dict) and selection["first"] > len(table):
        unselected.append(f"{result_id}: @first={selection['first']} asks for more rows than the table's "
                          f"{len(table)}")
    problems = unknown + unnamed + unselected
    if unknown or unselected:
        return None, None, None, problems  # the cells a file would hold are unknown, so rounding waits
    selected = _select(table, selection)
    # A result's own percent list replaces the global one, so a column already holding percents there is kept.
    own_percent = display["results"].get(result_id, {}).get("percent")
    percent = [c for c in chosen if c in (display["percent"] if own_percent is None else own_percent)]
    places = {}
    for column in chosen:
        if column in rounding:
            value = rounding[column]
            if type(value) is not int or not 0 <= value <= _ROUND_LIMIT:
                problems.append(f"{result_id}: column {column!r} has [round] places {value!r} in {_DISPLAY}; give "
                                f"a whole number from 0 to {_ROUND_LIMIT}")
            else:
                places[column] = value
            continue
        example = next((row[column] for row in selected if row[column] not in values.get(column, {})
                        and _unrounded(row[column], column in percent)), None)
        if example is not None:
            problems.append(f"{result_id}: column {column!r} has values with more than {UNROUNDED_PLACES} decimal "
                            f"places{' shown as a percent' if column in percent else ''}, trailing zeros aside, "
                            f"such as {example}, and no places under [round] in {_DISPLAY}")
            round_gaps.append(column)
    if problems:
        return None, None, None, problems
    used = {}
    for column in chosen:
        codes = values.get(column, {})
        labeled = {row[column]: codes[row[column]] for row in selected if row[column] in codes}
        if labeled:
            used[column] = labeled
    entry = {"result_id": result_id, "columns": chosen, "selection": selection,
             "headers": [names[c] for c in chosen], "values": used, "percent": percent, "round": places}
    return entry, _apply(table, entry), _sources(entry), []


def _sources(entry):
    """The methodology lines for one file's entry: the rows it selects, unless all, then each header's source
    column with its percent scaling and rounding, so methodology.md states the shaping the manifest records."""
    result_id, selection, lines = entry["result_id"], entry["selection"], []
    if selection != "all" and "first" in selection:
        lines.append(f"rows <- the first {selection['first']} rows of {result_id}")
    elif selection != "all":
        where, values = selection["where"], selection["where"]["values"]
        listed = values[0] if len(values) == 1 else f"{', '.join(values[:-1])} or {values[-1]}"
        lines.append(f"rows <- the rows of {result_id} whose {where['column']} is {listed}")
    for header, column in zip(entry["headers"], entry["columns"]):
        places = entry["round"].get(column)
        shaping = ([", times 100"] if column in entry["percent"] else []) + (
            [] if places is None else [", rounded to whole numbers" if places == 0
                                       else f", rounded to {places} decimal place{'s' if places != 1 else ''}"])
        lines.append(f"{header} <- {result_id}.{column}{''.join(shaping)}")
    return lines


def label_collisions(display, files, questions) -> list[dict]:
    """Each column whose global [columns] name labels files from results answering different questions, no
    such result naming the column under its own [results."<id>".columns]: {column, name, results, warning}.

    files is [(result_id, [columns])], one per exported file; questions maps each result to its question.
    """
    groups = {}
    for result_id, columns in files:
        own = display["results"].get(result_id, {}).get("columns", {})
        for column in columns:
            if column in display["columns"] and column not in own:
                groups.setdefault(column, {})[result_id] = None
    return [{"column": column, "name": display["columns"][column], "results": list(results), "warning": _COLLISION}
            for column, results in groups.items()
            if len({json.dumps(questions.get(r), sort_keys=True) for r in results}) > 1]


def export(root, investigation, package, charts=(), datasets=(), results=(), *, no_datasets=False,
           rounding=None) -> dict:
    """Serialize recorded results into the draft and record the represented results' provenance.

    charts are (result_id, columns) or (result_id, columns, selection) as `parse_chart` gives them; datasets
    are (name, (result_id, columns)). Any chart, dataset, or no_datasets makes a full export that replaces
    the chart set and the dataset selection; serialized results must pass compare_evidence. Results named
    only in `results` are represented without the check, and with no chart or dataset the exported files
    stay untouched.
    """
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    full = bool(charts or datasets or no_datasets)
    report = {"charts": [], "datasets": [], "written": False, "errors": []}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {_rel(root, draft)}; create it with awb-package")
        return report
    path = draft / MANIFEST
    try:
        report["created"] = not path.exists()
        record = {} if report["created"] else _read_json(path)
        display = display_names(root) if full else None
    except (OSError, ValueError, ImportError) as error:
        report["errors"].append(str(error))
        return report

    shaped, sources, gaps, round_gaps = [], [], [], []
    if full:
        rounding = {**display["round"], **(rounding or {})}
        for kind, label, (result_id, columns, *selection) in (
                [("chart", f"chart-{i}", spec) for i, spec in enumerate(charts, 1)]
                + [("dataset", n, spec) for n, spec in datasets]):
            entry, rows, lines, problems = _shape(root, investigation, result_id, columns,
                                                  selection[0] if selection else "all", display, rounding,
                                                  gaps, round_gaps)
            report["errors"] += problems
            if not problems:
                shaped.append((kind, label, entry, rows))
                sources += [f"{label}: {line}" for line in lines]
        # Ready to paste under [columns] once each name is filled in from the glossary. A blank name
        # already has its key, so it is fixed in place from its error and left out, keeping a paste valid.
        absent = [c for c in dict.fromkeys(gaps) if c not in display["columns"]]
        if absent:
            report["display_stub"] = "\n".join(f'{_toml_key(c)} = ""' for c in absent)
        # Likewise under [round], each filled in with the decimal places the slide's number format shows.
        if round_gaps:
            report["round_stub"] = "\n".join(f'{_toml_key(c)} = ""' for c in dict.fromkeys(round_gaps))
    else:
        recorded = record.get("charts") if isinstance(record.get("charts"), list) else []
        report["errors"] += [f"{c.get('path')} serializes {c.get('result_id')}, which this call does not name; "
                             "pass it with --result" for c in recorded
                             if isinstance(c, dict) and c.get("result_id") not in results]
    if report["errors"]:
        return report

    serialized = list(dict.fromkeys(entry["result_id"] for _, _, entry, _ in shaped))
    represented = list(dict.fromkeys(serialized + list(results)))
    evidence, evidence_paths = {}, {}
    for result_id in represented:
        evidence_path = root / "investigations" / investigation / "evidence" / f"{result_id}.json"
        evidence_paths[result_id] = _rel(root, evidence_path)
        try:
            evidence[result_id] = _read_json(evidence_path)
            if not _usable_evidence(evidence[result_id]):
                raise ValueError(_UNUSABLE)
        except (OSError, ValueError) as error:
            report["errors"].append(f"missing evidence: {evidence_paths[result_id]}: {error}")
    if report["errors"]:
        return report
    questions = {r: evidence[r].get("question", {"unknown": "evidence lacks question"}) for r in represented}
    if full:
        report["label_warnings"] = label_collisions(
            display, [(entry["result_id"], entry["columns"]) for _, _, entry, _ in shaped], questions)

    checks = {}
    if serialized:
        try:
            compare = _load_provenance(root).compare_evidence
        except (OSError, ImportError) as error:
            report["errors"].append(str(error))
            return report
        checks = {r: {"result_id": r, "evidence": evidence_paths[r], "comparisons": compare(root, evidence_paths[r])}
                  for r in serialized}
    failed = [{"result_id": c["result_id"], "name": i["name"], "detail": i["detail"]}
              for c in checks.values() for i in c["comparisons"] if i["outcome"] != "pass"]
    report["export_checks"] = {"results": len(checks), "failed": failed}
    if failed:
        report["exports_blocked"] = _BLOCKED
        return report

    # Settled before any file changes, so the manifest written below always matches the exports.
    try:
        flags = sync_flags(record.get("revalidation_flags"), state_flags(root, investigation))
    except ValueError as error:
        flags, report["flags_error"] = None, str(error)

    if full:
        frames = [(entry, rows) for kind, _, entry, rows in shaped if kind == "chart"]
        try:
            paths = write_charts(draft / "charts", [(entry["headers"], rows) for entry, rows in frames])
        except ValueError as error:
            report["errors"].append(f"charts: {error}")
            return report
        report["charts"] = [{"path": _rel(draft, p), "result_id": entry["result_id"]}
                            for p, (entry, _) in zip(paths, frames)]
        # Each entry records the shaping check-draft reapplies to verify its file.
        record["charts"] = [{"path": _rel(draft, p), **entry} for p, (entry, _) in zip(paths, frames)] or "none"
        directory = draft / "datasets"
        if directory.is_dir():
            for stale in directory.glob("*.csv"):
                stale.unlink()  # The selection is replaced whole, as write_charts replaces charts.
        selection = []
        for kind, label, entry, rows in shaped:
            if kind != "dataset":
                continue
            directory.mkdir(exist_ok=True)
            dataset = directory / f"{label}.csv"
            with dataset.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(entry["headers"])
                writer.writerows(rows)
            report["datasets"].append({"path": _rel(draft, dataset), "result_id": entry["result_id"]})
            selection.append({"path": _rel(draft, dataset), "result_id": entry["result_id"],
                              "columns": entry["columns"], "percent": entry["percent"], "round": entry["round"]})
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
        record["dataset_selection"] = selection or "none"
        report["methodology_lines"] = sources

    if report["created"]:
        record.update(investigation=investigation, package=package, status="draft")
    # A represented result not serialized keeps its entry; entries outside the represented set drop.
    previous = record.get("export_checks") if isinstance(record.get("export_checks"), list) else []
    kept = {c.get("result_id"): c for c in previous if isinstance(c, dict)}
    entries = [checks.get(r) or kept.get(r) for r in represented]
    record["export_checks"] = [e for e in entries if e] or "none"
    # Every represented result with its evidence, serialized or not, so status can see a later rerun,
    # the question it answers, which methodology.md repeats verbatim, and the runtime that evidence recorded.
    record["results"] = [{"result_id": r, "evidence": evidence_paths[r], "question": questions[r],
                          "runtime": _runtime(evidence[r])}
                         for r in represented]
    fields = producing_state(evidence)
    fields["packaging_commit"], fields["packaging_uncommitted_changes"] = packaging_state(root)
    record.update(fields)
    # revalidation_flags follows state.md on every write; an unreadable state.md leaves it as it was.
    if flags is not None:
        record["revalidation_flags"] = flags
    _write_json(path, record)
    report["written"] = True
    commits, changes = fields["producing_commit"], fields["producing_uncommitted_changes"]
    report["results"] = represented
    report["questions"] = questions
    report["producing_commit"] = "differs by result" if isinstance(commits, list) else commits
    report["producing_uncommitted_changes"] = len(changes) if isinstance(changes, list) else 0
    report["packaging_commit"] = fields["packaging_commit"]
    report["packaging_uncommitted_changes"] = fields["packaging_uncommitted_changes"]
    report["flags_pending"] = pending_flags(record.get("revalidation_flags"))
    if (draft / "findings.md").is_file():
        report["check_charts"] = check_charts(draft / "findings.md", draft / "charts")
    return report


def cli_export(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py export", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Write the draft's chart and dataset files from saved result tables, renamed, mapped, "
                    "scaled, and rounded through foundation/display.toml, a chart's rows selected as its --chart "
                    "says, once compare_evidence passes for every serialized result, and the manifest's "
                    "producing and packaging state from the evidence of every represented result. Creates the "
                    "manifest when absent.",
        epilog="Prints one JSON line.\nAny --chart, --dataset, or --no-datasets replaces the whole chart set "
               "and dataset selection: no --chart records charts none. With only --result it records "
               "provenance and leaves exported files untouched.\n"
               f"--chart takes {_CHART_FORM}, a closed grammar: the first '@' opens the row selection, so a "
               "column name holding '@' or ',' cannot be named in COLUMNS, though the @where column may hold "
               "either; before it, the first ':' opens the columns, "
               "comma-separated, none empty. @first=<n> (a whole number from 1 to 999999999, no leading zero) takes the "
               "saved table's first n rows, in its stable order; @where=<column>=<value>[,<value>] takes, in table order, the rows whose "
               "column holds one of the values exactly as the table writes it, before value labels, so no value "
               "can hold ',' or be empty. Malformed text is refused with exit 2; a selection naming no column "
               "of the table, a value no row holds, or more rows than the table has is an error, and nothing "
               "is written. A --dataset takes no row selection.\n"
               "foundation/display.toml holds [columns] (column = display name), [values.<column>] (coded "
               "value = label), [round] (column = decimal places, 0 to 20), [percent] with columns = [...] "
               "(fractions shown 100 times larger, scaled exactly before rounding), and [results.\"<result>\"] "
               "with columns, values, and percent tables that replace the global ones for that result, a values "
               "table for its whole column and a percent table for every column, so a column that already holds "
               "percents in one result is not scaled again; any other key is an error.\nEvery exported column "
               "needs a non-blank display name; gaps are listed together with display_stub, lines for absent "
               "names to fill in under [columns] (a blank name is fixed in place), and nothing is written. A "
               "number cell a file holds "
               f"is unrounded when its saved text, with trailing zeros dropped, any exponent applied, and a "
               f"percent column's 100-fold scaling applied, has more than {UNROUNDED_PLACES} decimal places, so "
               f"a percent column's saved fraction may carry {UNROUNDED_PLACES + 2} (366.89000039169395 and "
               "1e-05 are; 21.3500, which is 21.35, is not); a column holding one needs places under [round] "
               "or --round, listed with round_stub, lines to paste under [round] once each \"\" is replaced "
               "with the places the slide's number format shows, unquoted, such as \"share\" = 1.\nlabel_warnings "
               "lists each column whose [columns] name labels files from results with different questions "
               "and no [results.\"<result>\".columns] name; it is a warning, and the files are written.\n"
               "The manifest's charts entries record each chart's result, columns, selection, headers, value "
               "labels used, percent columns, and places, which check-draft reapplies to verify the file; "
               "dataset_selection entries record each dataset's result, columns, percent columns, and places.\n"
               "methodology_lines states each file's shaping for methodology.md: the rows a chart selects, then "
               "each header's source column with any percent scaling and rounding.\n"
               "Writes nothing when an evidence file is "
               "missing or any comparison fails (exports_blocked).\nEach write sets revalidation_flags from "
               "state.md's flags (none when it flags nothing), keeping an entry whose finding and reason match "
               "exactly and adding others with represented_in [] and disposition none; flags_pending lists "
               "each entry that needs represented_in or, once represented, a disposition. When state.md "
               "cannot be read, flags_error says why and revalidation_flags is left as it was.\nquestions maps "
               "each represented result to the question its evidence records, for methodology.md to repeat "
               "verbatim; the manifest's results entries record it.\nExit 0 only "
               "when written and check_charts is empty; 2 for unusable arguments.")
    _package_arguments(parser)
    parser.add_argument("--chart", action="append", default=[], metavar="RESULT[:COLUMNS][@SELECTION]",
                        help="one per chart, in the order of the Chart N specifications; columns comma-separated; "
                             "@first=<n> or @where=<column>=<value>[,<value>] selects rows")
    parser.add_argument("--dataset", action="append", default=[], metavar="NAME=RESULT[:COLUMNS]",
                        help="one per selected dataset; replaces the whole selection")
    parser.add_argument("--no-datasets", action="store_true", help="record an explicit selection of none")
    parser.add_argument("--result", action="append", default=[], metavar="RESULT",
                        help="a represented result not serialized here; its producing state is recorded "
                             "without the export check")
    parser.add_argument("--round", action="append", default=[], metavar="COLUMN=PLACES",
                        help=f"decimal places, 0 to {_ROUND_LIMIT}, for a column, over foundation/display.toml [round]")
    args = parser.parse_args(argv)
    if args.dataset and args.no_datasets:
        parser.error("--dataset and --no-datasets exclude each other")
    if args.chart and not (args.dataset or args.no_datasets):
        parser.error("--chart replaces the whole export: name every --dataset, or --no-datasets")
    if not (args.chart or args.dataset or args.no_datasets or args.result):
        parser.error("name every represented result: --chart, --dataset or --no-datasets, and --result")
    charts, datasets, refused = [], [], []
    for item in args.chart:
        try:
            charts.append(parse_chart(item))
        except ValueError as error:
            refused.append(str(error))
    for item in args.dataset:
        label, sep, spec = item.partition("=")
        if not sep:
            parser.error(f"--dataset needs NAME=RESULT: {item!r}")
        if "@" in spec:
            refused.append(f"--dataset {item!r}: a dataset takes no row selection; select rows only in a --chart")
            continue
        datasets.append((_simple(label, "dataset name"), _spec(spec, "result-id")))
    if refused:
        _print({"charts": [], "datasets": [], "written": False, "errors": refused})
        return 2
    rounding = {}
    for item in args.round:
        column, sep, places = item.partition("=")
        if not sep or not places.isascii() or not places.isdigit() or int(places) > _ROUND_LIMIT:
            parser.error(f"--round needs COLUMN=PLACES, PLACES from 0 to {_ROUND_LIMIT}: {item!r}")
        rounding[column] = int(places)
    report = export(Path(root), _simple(args.investigation, "investigation"), _simple(args.package, "package"),
                    charts, datasets, [_simple(r, "result-id") for r in args.result], no_datasets=args.no_datasets,
                    rounding=rounding)
    _print(report)
    return 0 if report["written"] and not report.get("check_charts") else 1


# ---------------------------------------------------------------- review rules

REVIEW_RULES = "foundation/review-rules.md"
_SEVERITIES = ("error", "warning")
# An area's last segment holds a letter, so R-<area>-NNN never reads as another area's ID.
_AREA_TEXT = r"(?:[a-z0-9]+-)*[a-z0-9]*[a-z][a-z0-9]*"
_AREA = re.compile(_AREA_TEXT)
# [0-9], not \d, which also takes other scripts' digits, such as Arabic-Indic ones.
_RULE_HEADING = re.compile(rf"## (R-({_AREA_TEXT})-([0-9]{{3,}}))\s*")
_RULE_FIELD = re.compile(r"- (Severity|Rule|Pattern|Scope|Package|Fix|Added): ?(.*)")
_LOOSE_FIELD = re.compile(r"\s*[-*+]?\s*(?:Severity|Rule|Pattern|Scope|Package|Fix|Added)\s*:", re.IGNORECASE)
_MARKDOWN_HEADING = re.compile(r"\s*#{1,6}(?:\s|$)")
_REQUIRED_FIELDS = ("Severity", "Rule", "Pattern", "Fix")
# What one violation of a rule covers, and so how check groups its matches: each line (the default, when a
# rule has no Scope field); each slide, read as the section a #, ##, or ### heading opens as the narrative
# renders, which in findings.md is one slide and in methodology.md and the note one section; or each file.
_SCOPES = ("line", "slide", "document")
# A rule kept for one package names it as <investigation>/<package>; check lists it for that package alone.
_RULE_PACKAGE = re.compile(rf"({_SIMPLE.pattern})/({_SIMPLE.pattern})")
# A number in a rule's text, so add can warn when it repeats one a draft states: digits with any thousands
# groups and decimal part, compared by value. Any digit run counts, a version's parts included, since a
# needless warning costs a glance and a missed one keeps one draft's figure in every later review.
_RULE_NUMBER = re.compile(r"(?<![0-9])[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?")
_BAD_HEADING = ("rule heading is not ## R-<area>-NNN with a lowercase area, its last part holding a letter, "
                "and a three-digit number")
_STRAY_HEADING = "heading after the first rule is not a ## R-<area>-NNN rule heading"
# Every line break str.splitlines() recognizes but \n; grep -n counts only \n.
_OTHER_BREAK = re.compile("[\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]")
_MATCH_CAP = 20
_RULES_HEADER = """# Review rules

Rules from the user's corrections to package drafts. The read-only package review checks every rule on \
every draft; `python3 src/awb.py review-rules check <investigation> <package>` lists each rule with the \
narrative lines its pattern matches.

Add a rule only with `python3 src/awb.py review-rules add`. A rule ID, `R-<area>-NNN`, is never \
renumbered, reused, or deleted: edit a rule's other fields in place, and retire a rule by setting its \
severity to `retired`. A pattern is a Python regular expression in backticks, matched against each line \
of the draft's `findings.md`, `methodology.md`, and `methodology-note.md` when it has one, or `none` when no \
pattern can find the problem. An optional scope, `line` (the default), `slide`, or `document`, sets what one \
violation covers: a line, a slide (in `methodology.md` and the note, a section under a `#`, `##`, or `###` \
heading), or a whole file. An optional package, `<investigation>/<package>`, keeps a rule for that package \
alone; every other rule holds for every package.
"""


def _parse_pattern(value):
    """(pattern text or None, problem or None) from a Pattern field: `regex` in backticks, or none."""
    if value == "none":
        return None, None
    if len(value) < 3 or not (value.startswith("`") and value.endswith("`")):
        return None, "Pattern is neither none nor a regular expression in backticks"
    problem = _pattern_problem(value[1:-1])
    return (None, f"Pattern {problem}") if problem else (value[1:-1], None)


def _pattern_problem(pattern):
    """Why a regular expression is unusable, or None; Python raises more than re.error on some."""
    try:
        re.compile(pattern)
    except (re.error, OverflowError, RecursionError, ValueError) as error:
        return f"does not compile: {error}"
    return None


def _read_lines(path):
    r"""A file's lines as grep -n numbers them: split on \n only, with no empty line after a final \n.

    Read as bytes: text mode would turn a lone \r into \n and shift every later line number. A \r is
    dropped only where a \n follows it, as a CRLF ending; any other \r, one at the end of the file
    included, stays in its line. A UTF-8 byte order mark is not part of line 1."""
    *ended, last = Path(path).read_bytes().decode("utf-8-sig").split("\n")
    return [line.removesuffix("\r") for line in ended] + ([last] if last else [])


def parse_review_rules(lines: list) -> tuple:
    """(rules, problems) from review-rules.md: each `## R-<area>-NNN` section and its `- Field:` lines.

    The grammar is closed. A rule section holds blank lines and `- <Field>: <value>` lines, each field at
    most once: Severity (error, warning, or retired), Rule, Pattern (`regex` in backticks, or none), and
    Fix, all required; Scope (exactly line, slide, or document; line when absent), Package
    (<investigation>/<package>; every package when absent), and Added, optional. Any other line, field, or
    value is a problem, and a rule with an unusable Pattern or Scope is unchecked; one with an unusable
    Package holds for every package, so a typo never hides it.
    Any heading ends a section, and after the first rule every heading must be a rule's. Inside a rule
    section only blank and `- Field:` lines may appear, so a wrapped line starting with `#` is reported
    too; outside one no heading may name a rule and no line may look like a field. A rule that a hand
    edit breaks or cuts short is reported instead of silently dropped or truncated, and its ID is never
    handed out again by add. Lines are numbered as _read_lines splits them, so each problem's line is the
    one grep -n shows; a line holding another line break (U+2028, form feed, a lone carriage return) is a
    problem, since an editor may show it as two lines."""
    rules, problems, current = [], [], None
    for number, line in enumerate(lines, 1):
        other = _OTHER_BREAK.search(line)
        if other:
            problems.append({"line": number, "problem": f"line holds U+{ord(other[0]):04X}, a line break other "
                                                        "than \\n; replace it with a space or a newline"})
        if line.lstrip().startswith("#"):
            heading = _RULE_HEADING.fullmatch(line)
            if heading:
                current = {"id": heading[1], "area": heading[2], "number": int(heading[3]), "line": number,
                           "fields": {}}
                rules.append(current)
                continue
            # Only a heading that starts like a rule ID is a broken rule heading; ## PR-12 notes is not.
            if re.match(r"\s*#+\s*R-", line):
                problems.append({"line": number, "problem": _BAD_HEADING})
                current = None
                continue
            if _MARKDOWN_HEADING.match(line):
                if rules:
                    problems.append({"line": number, "problem": _STRAY_HEADING})
                current = None
                continue
            # Text such as `#hashtags`, not a heading: inside a rule it is a line that is not a field.
        if current is None:
            if _LOOSE_FIELD.match(line):
                problems.append({"line": number, "problem": "rule field outside a ## R-<area>-NNN section"})
            continue
        field = _RULE_FIELD.fullmatch(line.rstrip())
        if field:
            if field[1] in current["fields"]:
                problems.append({"rule": current["id"], "line": number, "problem": f"repeated {field[1]} line"})
            current["fields"][field[1]] = field[2].strip()
        elif line.strip():
            problems.append({"rule": current["id"], "line": number,
                             "problem": "line is not a - Severity, Rule, Pattern, Scope, Package, Fix, or "
                                        "Added field"})
    seen = {}
    for rule in rules:
        fields = rule.pop("fields")
        first = seen.setdefault((rule["area"], rule["number"]), rule)
        if first is not rule:
            # R-x-007 and R-x-0007 are one number written twice, so add must not treat them as two.
            problems.append({"rule": rule["id"], "problem": "rule ID appears more than once"
                             if first["id"] == rule["id"] else f"rule ID repeats the number of {first['id']}"})
        missing = [name for name in _REQUIRED_FIELDS if not fields.get(name)]
        if missing:
            problems.append({"rule": rule["id"], "problem": f"missing {', '.join(missing)}"})
        severity = fields.get("Severity", "")
        if severity and severity not in (*_SEVERITIES, "retired"):
            problems.append({"rule": rule["id"], "problem": f"unknown severity {severity!r}; use error, "
                                                            "warning, or retired"})
        rule.update(severity=severity, rule=fields.get("Rule", ""), fix=fields.get("Fix", ""),
                    pattern=None, scope=fields.get("Scope", "line"), package=fields.get("Package"), usable=True)
        if rule["package"] is not None and not _RULE_PACKAGE.fullmatch(rule["package"]):
            problems.append({"rule": rule["id"], "problem": f"Package {rule['package']!r} is not "
                                                            "<investigation>/<package>"})
            rule["package"] = None
        if fields.get("Pattern"):
            rule["pattern"], problem = _parse_pattern(fields["Pattern"])
            if problem:
                rule["usable"] = False
                problems.append({"rule": rule["id"], "problem": problem})
        # Present but blank is malformed too: an absent Scope is the only way to mean line by default.
        if rule["scope"] not in _SCOPES:
            rule["usable"] = False
            problems.append({"rule": rule["id"], "problem": f"unknown scope {rule['scope']!r}; use line, slide, "
                                                            "or document"})
    return rules, problems


def _sections(lines):
    """The first line number of each section a #, ##, or ### heading opens, read as the text renders, with
    its heading text: [(first line, heading or None)], text before the first heading under None. Unless a
    heading opens line 1, the list starts with (1, None), blank lines alone included, so every line has one.

    The view splits on every line break str.splitlines() knows, so each other break becomes a space first
    and every section keeps the line numbers grep -n gives (_read_lines)."""
    view = _view("\n".join(_OTHER_BREAK.sub(" ", line) for line in lines))[0]
    sections = [(first, heading) for level, heading, first, rows in _regions(view) if level or rows]
    return sections if sections and sections[0][0] == 1 else [(1, None), *sections]


def _scoped_matches(scope, texts, pattern):
    """A rule's matched lines grouped into one entry per line, slide, or file (_SCOPES); lines in an entry
    are capped at _MATCH_CAP, with more_lines counting the rest."""
    entries = []
    for name, lines in texts.items():
        found = [{"line": number, "text": line.strip()[:160]}
                 for number, line in enumerate(lines, 1) if pattern.search(line)]
        if scope == "line":
            entries += [{"file": name, **match} for match in found]
            continue
        groups = {}
        if scope == "document" and found:
            groups[0] = ({"file": name}, found)
        elif scope == "slide" and found:
            sections = _sections(lines)
            starts = [first for first, _ in sections]
            for match in found:
                first, heading = sections[bisect.bisect_right(starts, match["line"]) - 1]
                groups.setdefault(first, ({"file": name, "heading": heading, "line": first}, []))[1].append(match)
        for entry, inside in groups.values():
            entry["lines"] = inside[:_MATCH_CAP]
            if len(inside) > _MATCH_CAP:
                entry["more_lines"] = len(inside) - _MATCH_CAP
            entries.append(entry)
    return entries


def _read_rules(root):
    """(rules, problems), or None when the project has no rule file.

    Only an absent path means no rules: a directory or other non-file there, or a symbolic link to
    nothing, raises OSError, so check reports an error and add refuses instead of reading no rules."""
    path = Path(root) / REVIEW_RULES
    try:
        path.stat()
    except FileNotFoundError:
        if not path.is_symlink():
            return None
        raise
    if not path.is_file():
        raise OSError("not a regular file")
    return parse_review_rules(_read_lines(path))


def _for_package(rule, investigation, package):
    """Whether a rule holds for this package: every rule without a Package field, and one naming it."""
    return rule["package"] is None or rule["package"] == f"{investigation}/{package}"


def check_review_rules(root, investigation, package) -> dict:
    """List every review rule that holds for the package with the draft narrative lines its pattern matches,
    leaving out a rule kept for another package; writes nothing."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"rules_file": REVIEW_RULES, "draft": _rel(root, draft), "rules": [], "problems": [], "errors": []}
    texts = {}
    for name in _narratives(draft):
        try:
            texts[name] = _read_lines(draft / name)
        except (OSError, UnicodeError) as error:
            report["errors"].append(f"{_rel(root, draft / name)}: {error}")
    try:
        parsed = _read_rules(root)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"{REVIEW_RULES}: {error}")
        return report
    if parsed is None:
        report["rules_file"] = "none recorded"
        return report
    rules, report["problems"] = parsed
    for rule in rules:
        if not _for_package(rule, investigation, package):
            continue
        row = {"id": rule["id"], "severity": rule["severity"]}
        if rule["scope"] in _SCOPES[1:]:
            row["scope"] = rule["scope"]
        if rule["package"] is not None:
            row["package"] = rule["package"]
        if rule["severity"] == "retired":
            row["status"] = "retired"
        elif not rule["usable"]:
            row["status"] = "unchecked"
        elif rule["pattern"] is None:
            row["status"] = "no pattern"
        else:
            matches = _scoped_matches(rule["scope"], texts, re.compile(rule["pattern"]))
            row["status"] = "matched" if matches else "no match"
            if matches:
                row["matches"] = matches[:_MATCH_CAP]
                if len(matches) > _MATCH_CAP:
                    row["more_matches"] = len(matches) - _MATCH_CAP
        report["rules"].append(row)
    return report


def _draft_numbers(root, drafts):
    """({value: (narrative path, line)} for the first place each number stands in the drafts' narratives,
    [warnings for a narrative that cannot be read])."""
    found, warnings = {}, []
    for draft in drafts:
        for name in _narratives(draft):
            try:
                lines = _read_lines(draft / name)
            except FileNotFoundError:
                continue  # a narrative not written yet states no number
            except (OSError, UnicodeError) as error:
                warnings.append(f"{_rel(root, draft / name)} not read for numbers: {error}")
                continue
            for number, line in enumerate(lines, 1):
                for match in _RULE_NUMBER.finditer(line):
                    found.setdefault(Decimal(match[0].replace(",", "")), (_rel(root, draft / name), number))
    return found, warnings


def rule_number_warnings(root, texts, package=None) -> list[str]:
    """A warning for each number in texts (the rule and its fix) that a draft's narratives also state: the
    package's draft for a package rule, else every draft under deliveries/. A rule repeating one draft's
    figure is usually that draft's correction, not a rule later drafts can follow."""
    root = Path(root)
    drafts = [_package_dir(root, *package.split("/")) / "draft"] if package else \
        sorted(path for path in (root / "deliveries").glob("*/*/draft") if path.is_dir())
    found, warnings = _draft_numbers(root, drafts)
    named = {}
    for text in texts:
        for match in _RULE_NUMBER.finditer(text):
            named.setdefault(Decimal(match[0].replace(",", "")), match[0])
    for value, written in named.items():
        if value in found:
            path, line = found[value]
            warnings.append(f"the rule names {written}, which {path}:{line} also states; a rule says what every "
                            "later draft must do, so if it holds this draft's figure, reword it in place with "
                            "the user or keep the correction as an edit")
    return warnings


def add_review_rule(root, area, severity, rule, fix, pattern=None, scope=None, package=None, *,
                    confirmed=False, today=None) -> dict:
    """Append rule R-<area>-NNN, numbered after every ID the area has used, creating the file if absent.

    Refuses unless confirmed, the user having said yes to keeping the correction as a standing rule. A
    scope is written only when given; a rule without one is checked line by line. A package,
    <investigation>/<package>, must name an existing package and keeps the rule for it alone. warnings
    lists numbers the rule shares with a draft (rule_number_warnings); they never refuse."""
    root = Path(root)
    path = root / REVIEW_RULES
    if not confirmed:
        return {"added": None, "refused": "ask the user first whether later drafts should be checked for this "
                                          "correction, and pass --confirmed once they say yes"}
    if package is not None and not _package_dir(root, *package.split("/")).is_dir():
        return {"added": None, "refused": f"no package at deliveries/{package}; --package names "
                                          "<investigation>/<package>"}
    try:
        parsed = _read_rules(root)
    except (OSError, UnicodeError) as error:
        return {"added": None, "refused": f"{REVIEW_RULES}: {error}"}
    rules, problems = parsed if parsed is not None else ([], [])
    if problems:
        return {"added": None, "refused": f"repair {REVIEW_RULES} first; numbering needs a sound file",
                "problems": problems}
    number = max((r["number"] for r in rules if r["area"] == area), default=0) + 1
    rule_id = f"R-{area}-{number:03d}"
    day = today or datetime.now().astimezone().date().isoformat()
    scoped = f"- Scope: {scope}\n" if scope else ""
    scoped += f"- Package: {package}\n" if package else ""
    entry = (f"## {rule_id}\n\n- Severity: {severity}\n- Rule: {rule}\n"
             f"- Pattern: {f'`{pattern}`' if pattern else 'none'}\n{scoped}- Fix: {fix}\n- Added: {day}\n")
    existing = path.read_text(encoding="utf-8-sig") if parsed is not None else ""
    if not existing.strip():
        existing = _RULES_HEADER
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_text(path, existing.rstrip("\n") + "\n\n" + entry)
    return {"added": rule_id, "rules_file": REVIEW_RULES, "created": parsed is None,
            "rules": len(rules) + 1, "warnings": rule_number_warnings(root, (rule, fix), package)}


def cli_review_rules(root: Path, argv: list[str]) -> int:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog="awb.py review-rules", formatter_class=raw,
        description=f"Check a draft against the review rules in {REVIEW_RULES}, or append a rule from a "
                    "user's correction.",
        epilog="Run `awb.py review-rules <subcommand> --help` for its arguments, output, and exit status.")
    actions = parser.add_subparsers(dest="action", required=True, metavar="{check,add}")
    check = actions.add_parser(
        "check", formatter_class=raw, help="list every rule with the draft lines its pattern matches",
        description="List every review rule that holds for the package, a rule kept for another package left "
                    "out, with the lines of the draft's findings.md, methodology.md, and methodology-note.md "
                    "when the draft holds it, that its pattern matches. Writes nothing.",
        epilog="Prints one JSON line.\nEach rules row has id, severity, and status: matched (with matches, "
               "at most 20, and more_matches beyond), no match, no pattern (judge the rule by reading), "
               "retired, or unchecked (its problem is listed). A row has scope when the rule's is slide or "
               "document, and package when the rule is kept for this package.\nA line rule's match is one line: file, line, and text. A slide rule's match is "
               "one slide, in methodology.md and the note one section, under a #, ##, or ### heading as the "
               "file renders: file, heading (null before the first), the heading's line, and lines, each line "
               "and text. A document rule's match is one file: file and lines. A match lists at most 20 "
               "lines, with more_lines beyond.\nA match is a candidate for the reviewer to judge, and no "
               "match does not prove the rule holds.\nrules_file is none recorded when the project has no "
               "rules.\nExit 0 when problems and errors are empty, matches or not; 1 otherwise.")
    _package_arguments(check)
    add = actions.add_parser(
        "add", formatter_class=raw, help="append the next numbered rule",
        description=f"Append a rule to {REVIEW_RULES}, creating the file when absent, as R-<area>-NNN: the "
                    "number after every one the area has used, retired rules included. Only with --confirmed: "
                    "the user said yes to keeping the correction as a standing rule.",
        epilog="Prints one JSON line: added (the new ID), rules_file, created, rules (the count), and warnings: "
               "each number the rule or fix names that a draft's narratives also state (the --package draft, "
               "else every draft), which still adds the rule.\nRefuses, writing nothing, without --confirmed, "
               "when --package names no package, or when the rule file has problems that `review-rules check` "
               "lists.\nExit 0 added; 1 refused; 2 unusable arguments.")
    add.add_argument("--area", required=True, help="what the rule governs, lowercase words joined by '-', "
                                                   "the last not all digits, such as periods or "
                                                   "metric-definitions")
    add.add_argument("--severity", required=True, choices=_SEVERITIES,
                     help="error: a violation must be repaired; warning: repaired or accepted by the user")
    add.add_argument("--rule", required=True, help="what every draft must do, in one line")
    add.add_argument("--fix", required=True, help="how to repair a violation, in one line")
    add.add_argument("--pattern", help="a Python regular expression matching a likely violation on one line "
                                       "(default: none, judged by reading)")
    add.add_argument("--scope", choices=_SCOPES,
                     help="what one violation covers, so a wording rule gives one verdict per slide or file "
                          "rather than per line: line (the default, written only when given), slide (one "
                          "slide, in methodology.md and the note one section under a #, ##, or ### heading), "
                          "or document (one file)")
    add.add_argument("--package", metavar="INVESTIGATION/PACKAGE",
                     help="keep the rule for this package alone (default: every package)")
    add.add_argument("--confirmed", action="store_true",
                     help="the user said yes to keeping the correction as a rule later drafts are checked for")
    args = parser.parse_args(argv)
    if args.action == "check":
        report = check_review_rules(Path(root), _simple(args.investigation, "investigation"),
                                    _simple(args.package, "package"))
        _print(report)
        return 1 if report["problems"] or report["errors"] else 0
    if not _AREA.fullmatch(args.area):
        add.error(f"--area must be lowercase letters and digits joined by '-', the last part holding a "
                  f"letter: {args.area!r}")
    for name in ("rule", "fix", "pattern"):
        value = getattr(args, name)
        if value is None:
            continue
        # \n and every other break the parser reports (_OTHER_BREAK), or the file add writes would fail
        # its own check and block the next add.
        if not value.strip() or value.splitlines() != [value]:
            add.error(f"--{name} must be one non-blank line")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:  # bytes that are not UTF-8 reach argv as lone surrogates
            add.error(f"--{name} is not valid UTF-8")
    if args.pattern is not None and (problem := _pattern_problem(args.pattern)):
        add.error(f"--pattern {problem}")
    if args.package is not None and not _RULE_PACKAGE.fullmatch(args.package):
        add.error(f"--package must be <investigation>/<package>, each a simple name: {args.package!r}")
    report = add_review_rule(Path(root), args.area, args.severity, args.rule.strip(), args.fix.strip(),
                             args.pattern, args.scope, args.package, confirmed=args.confirmed)
    _print(report)
    return 0 if report["added"] else 1


# ---------------------------------------------------------------- review receipt

# The record of the last review, beside draft/ so it is never inventoried or released.
REVIEW_DIR = "review"
RECEIPT = "receipt.json"
_KINDS = ("full", "scoped")
# What a review reads, in the order the fingerprint hashes it, and each one's file in the snapshot.
# The brief is keyed brief.md and read from the investigation; its questions and Audience set what a review checks.
BRIEF = "brief.md"
_REVIEW_INPUTS = {"findings.md": "findings.md", "methodology.md": "methodology.md",
                  METHODOLOGY_NOTE: METHODOLOGY_NOTE, BRIEF: BRIEF, REVIEW_RULES: "review-rules.md",
                  "revalidation_flags": "revalidation_flags.json"}
# Bounded so the diff and a prior report fit in one read tool result (16,000 characters by default).
_DIFF_LIMIT = 12000
_SUMMARY = re.compile(r"review( \(scoped\))?: (?:(clean)|([0-9]+) violations? \(([0-9]+) errors?\), "
                      r"([0-9]+) narrative problems?, ([0-9]+) command problems?)\.?")
_VIOLATION_ROW = re.compile(r"(?:[-*+]\s+)?R-\S+ violation (error|warning)(?=\s)")
_NARRATIVE_ROW = re.compile(r"(?:[-*+]\s+)?narrative\s")
_SUMMARY_FORM = ("`review: clean`, or `review: <v> violations (<e> error), <n> narrative problems, <c> command "
                 "problems`, opening `review (scoped):` for a scoped review")
NO_REVIEW = "no passed review of this draft: run the review in awb-package's references/review.md"


def _reviewed_flags(path):
    """The manifest's revalidation_flags reduced to what makes a review stale: each entry's finding, reason,
    represented_in, and whether its disposition is omit. Anything else, such as release_with_caveat recorded
    at release, leaves a review current; an entry that is not an object, or a value that is not a list, is
    kept whole, so any change to it counts."""
    try:
        record = _read_json(path)
    except FileNotFoundError:
        return {"manifest": "absent"}
    except (OSError, ValueError):
        return {"manifest": "unreadable"}
    flags = record.get("revalidation_flags")
    if not isinstance(flags, list):
        return flags
    return [{"finding": flag.get("finding"), "reason": flag.get("reason"),
             "represented_in": flag.get("represented_in"), "omit": flag.get("disposition") == "omit"}
            if isinstance(flag, dict) else flag for flag in flags]


def _package_rules(data, investigation, package):
    """The rule file's bytes without the sections of rules kept for another package, so adding or changing
    one leaves this package's review current. A file that does not decode or parse cleanly is kept whole,
    so any change to it still counts."""
    try:
        rules, problems = parse_review_rules([line.removesuffix("\r")
                                              for line in data.decode("utf-8-sig").split("\n")])
    except UnicodeError:
        return data
    if problems:
        return data
    lines = data.split(b"\n")
    # A sound file holds only rule headings after its first rule, so a section runs to the next one; the
    # last runs to the end of the file, its final newline included, so a rule appended for another package
    # leaves these bytes exactly as they were.
    ends = [rule["line"] - 1 for rule in rules[1:]] + [len(lines)]
    foreign = [(rule["line"] - 1, end) for rule, end in zip(rules, ends)
               if not _for_package(rule, investigation, package)]
    if not foreign:
        return data
    kept, last = [], 0
    for start, end in foreign:
        kept += lines[last:start]
        last = end
    kept += lines[last:]
    return b"\n".join(kept) + (b"\n" if last == len(lines) and kept and kept[-1] != b"" else b"")


def review_inputs(root, investigation, package) -> dict:
    """{input: bytes, or None when absent} for exactly what a review reads: the three narratives, the
    investigation's brief.md, the rule file without rules kept for another package (_package_rules), and the
    reduced revalidation_flags as
    indented JSON. Raises OSError on a path that cannot be read, a directory included."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    paths = {name: draft / name for name in NARRATIVES + (METHODOLOGY_NOTE,)}
    paths[BRIEF] = root / "investigations" / investigation / BRIEF
    paths[REVIEW_RULES] = root / REVIEW_RULES
    inputs = {}
    for name, path in paths.items():
        try:
            inputs[name] = path.read_bytes()
        except FileNotFoundError:
            inputs[name] = None
    if inputs[REVIEW_RULES] is not None:
        inputs[REVIEW_RULES] = _package_rules(inputs[REVIEW_RULES], investigation, package)
    flags = _reviewed_flags(draft / MANIFEST)
    inputs["revalidation_flags"] = (json.dumps(flags, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return inputs


def _digests(inputs):
    return {name: hashlib.sha256(inputs[name]).hexdigest() if inputs[name] is not None else "absent"
            for name in _REVIEW_INPUTS}


def _fingerprint(digests):
    return hashlib.sha256("".join(f"{name}\0{digests[name]}\n" for name in _REVIEW_INPUTS).encode()).hexdigest()


def review_summary(text, kind, accepted) -> tuple:
    """(passed, refusal) from a review report: its last non-blank line, as review.md's Brief step 4 writes it.

    passed is True when the line is clean, or when it counts no error violation and no command problem and
    accepted holds one entry for each warning violation and narrative problem it counts. A refusal names a
    report no record may rest on: a last line that does not parse, a kind it does not open with, more error
    than violations, a clean line given acceptances, or a body listing more violation or narrative rows of a
    kind than the last line counts, so a report that undercounts its own rows never passes."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None, "the report is empty"
    last = lines[-1].strip("`").strip()
    match = _SUMMARY.fullmatch(last)
    if not match:
        return None, f"the report's last line is not {_SUMMARY_FORM}: {last[:200]!r}"
    if bool(match[1]) != (kind == "scoped"):
        opens = "review (scoped):" if match[1] else "review:"
        return None, f"--kind {kind} does not match the report's last line, which opens {opens}"
    violations, errors, narrative, command = (0, 0, 0, 0) if match[2] else map(int, match.group(3, 4, 5, 6))
    if errors > violations:
        return None, "the report's last line counts more error violations than violations"
    if match[2] and accepted:
        return None, "a clean review has nothing to accept; record it without --accept"
    rows = Counter(row[1] for row in map(_VIOLATION_ROW.match, lines[:-1]) if row)
    narrative_rows = sum(1 for line in lines[:-1] if _NARRATIVE_ROW.match(line))
    if rows["error"] > errors or rows["warning"] > violations - errors or narrative_rows > narrative:
        return None, (f"the report lists {rows['error']} error and {rows['warning']} warning violations and "
                      f"{narrative_rows} narrative problems, more than its last line counts")
    return errors == 0 and command == 0 and len(accepted) == violations - errors + narrative, None


def record_review(root, investigation, package, kind, text, accepted=(), *, now=None) -> dict:
    """Record a review: snapshot what it read under deliveries/<investigation>/<package>/review/ and write
    receipt.json, replacing the previous record. A report that does not pass is recorded too, so the next
    review can be scoped against it; a refused report writes nothing."""
    root = Path(root)
    package_dir = _package_dir(root, investigation, package)
    if not (package_dir / "draft").is_dir():
        return {"recorded": False, "refused": f"no draft at {_rel(root, package_dir / 'draft')}; create it "
                                              "with awb-package"}
    accepted = list(accepted)
    passed, refusal = review_summary(text, kind, accepted)
    if refusal:
        return {"recorded": False, "refused": refusal}
    try:
        inputs = review_inputs(root, investigation, package)
    except OSError as error:
        return {"recorded": False, "refused": f"the draft cannot be read: {error}"}
    digests = _digests(inputs)
    directory = package_dir / REVIEW_DIR
    snapshot = directory / "snapshot"
    try:
        # The old receipt goes first, so an interrupted record leaves none, and the next review is full.
        (directory / RECEIPT).unlink(missing_ok=True)
        if snapshot.exists():
            shutil.rmtree(snapshot)
        snapshot.mkdir(parents=True)
        for name, stored in _REVIEW_INPUTS.items():
            if inputs[name] is not None:
                (snapshot / stored).write_bytes(inputs[name])
        receipt = {"recorded_at": now or _now(), "kind": kind, "fingerprint": _fingerprint(digests),
                   "inputs": digests, "report": text, "passed": passed, "accepted": accepted}
        _write_json(directory / RECEIPT, receipt)
    except OSError as error:
        return {"recorded": False, "refused": f"{_rel(root, directory)}: {error}"}
    return {"recorded": True, "receipt": _rel(root, directory / RECEIPT), "kind": kind, "passed": passed,
            "accepted": accepted}


def _diff_text(data):
    """Lines split at \\n alone, so hunk line numbers are the ones grep -n gives."""
    if data is None:
        return []
    text = data.decode("utf-8", "replace").removeprefix("﻿")
    parts = text.split("\n")
    return [part + "\n" for part in parts[:-1]] + ([parts[-1] + "\n"] if parts[-1] else [])


def review_receipt(root, investigation, package) -> dict:
    """The last review's record against the draft now; writes nothing.

    status is none (no receipt), current (it passed and nothing it read has changed), stale (something it
    read has changed), or failed (nothing changed, but it did not pass). changed names each input whose
    content differs, and diff is a unified diff of each from what the review read to the current file, cut
    at _DIFF_LIMIT characters with diff_cut counting the rest."""
    root = Path(root)
    directory = _package_dir(root, investigation, package) / REVIEW_DIR
    report = {"status": "none", "kind": None, "recorded_at": None, "accepted": [], "report": None,
              "changed": [], "diff": "", "diff_cut": 0, "errors": []}
    try:
        receipt = _read_json(directory / RECEIPT)
    except FileNotFoundError:
        return report
    except (OSError, ValueError) as error:
        report["errors"].append(f"{_rel(root, directory / RECEIPT)}: {error}")
        return report
    inputs_seen = receipt.get("inputs")
    if receipt.get("kind") not in _KINDS or not isinstance(receipt.get("passed"), bool) \
            or not isinstance(inputs_seen, dict) or not isinstance(receipt.get("accepted"), list):
        report["errors"].append(f"{_rel(root, directory / RECEIPT)}: not a review receipt; record the review again")
        return report
    report.update(kind=receipt["kind"], recorded_at=receipt.get("recorded_at"), accepted=receipt["accepted"],
                  report=receipt.get("report"))
    try:
        current = review_inputs(root, investigation, package)
    except OSError as error:
        report["status"] = "stale"
        report["errors"].append(f"the draft cannot be read: {error}")
        return report
    digests = _digests(current)
    report["changed"] = [name for name in _REVIEW_INPUTS if digests[name] != inputs_seen.get(name)]
    if report["changed"] or _fingerprint(digests) != receipt.get("fingerprint"):
        report["status"] = "stale"
    else:
        report["status"] = "current" if receipt["passed"] else "failed"
    draft = _rel(root, _package_dir(root, investigation, package) / "draft")
    pieces = []
    for name in report["changed"]:
        try:
            before = (directory / "snapshot" / _REVIEW_INPUTS[name]).read_bytes()
        except OSError:
            before = None
        label = REVIEW_RULES if name == REVIEW_RULES else f"investigations/{investigation}/{BRIEF}" \
            if name == BRIEF else f"{draft}/{MANIFEST} revalidation_flags" if name == "revalidation_flags" \
            else f"{draft}/{name}"
        pieces += difflib.unified_diff(_diff_text(before), _diff_text(current[name]),
                                       f"reviewed {label}", label)
    diff = "".join(pieces)
    if len(diff) > _DIFF_LIMIT:
        cut = diff.rfind("\n", 0, _DIFF_LIMIT) + 1 or _DIFF_LIMIT
        report["diff_cut"] = len(diff) - cut
        diff = diff[:cut] + (f"[... {report['diff_cut']} characters cut; read each changed file in full ...]\n")
    report["diff"] = diff
    return report


def cli_review_receipt(root: Path, argv: list[str]) -> int:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog="awb.py review-receipt", formatter_class=raw,
        description="Record a draft review, with a snapshot of what it read, or show the last one against the "
                    "draft now.",
        epilog="The record is deliveries/<investigation>/<package>/review/, beside draft/, so it is never "
               "inventoried or released.\nRun `awb.py review-receipt <subcommand> --help` for its arguments, "
               "output, and exit status.")
    actions = parser.add_subparsers(dest="action", required=True, metavar="{record,show}")
    record = actions.add_parser(
        "record", formatter_class=raw, help="record a review's report and what it read",
        description="Record a review's report: snapshot the draft's findings.md, methodology.md, "
                    "methodology-note.md when present, the investigation's brief.md when present, "
                    "foundation/review-rules.md when present without rules kept for another package, and the "
                    "manifest's revalidation_flags (finding, reason, represented_in, and whether the "
                    "disposition is omit), and write receipt.json with a SHA-256 fingerprint of them, the report "
                    "verbatim, passed, and accepted. Each record replaces the previous one.",
        epilog=f"The report's last line is {_SUMMARY_FORM}. passed is true when it is clean, or when it counts no "
               "error violation and no command problem and --accept is given once for each warning violation "
               "and narrative problem it counts. A report that does not pass is recorded with passed false.\n"
               "Prints one JSON line: recorded, receipt, kind, passed, and accepted.\nRefuses, writing nothing, "
               "when the last line does not parse, --kind disagrees with its opening, it counts more errors than "
               "violations, a clean report is given --accept, or the report lists more violation or narrative "
               "rows than its last line counts.\nExit 0 recorded; 1 refused; 2 unusable arguments.")
    _package_arguments(record)
    record.add_argument("--kind", required=True, choices=_KINDS, help="full, or scoped against the last record")
    record.add_argument("--report", required=True,
                        help="the reviewer's report file, project-relative or absolute, or - for standard input")
    record.add_argument("--accept", action="append", default=[], metavar="TEXT",
                        help='a problem the user accepted, as "<file>:<line> <quote>: <the user\'s reason>"; '
                             "once per accepted warning violation or narrative problem")
    show = actions.add_parser(
        "show", formatter_class=raw, help="compare the last record with the draft now, writing nothing",
        description="Compare the last recorded review with the draft now. Writes nothing.",
        epilog="Prints one JSON line: status (none: no record; current: it passed and nothing it read has "
               "changed; stale: something it read has changed; failed: nothing has changed, but it did not "
               "pass), kind, recorded_at, accepted, report (the prior report), changed (each input whose content "
               f"differs), diff (a unified diff of each from the reviewed copy to the current file, its + line "
               f"numbers the current file's, at most {_DIFF_LIMIT} characters, with diff_cut counting what was "
               "cut), and errors.\nExit 0 unless errors is not empty.")
    _package_arguments(show)
    args = parser.parse_args(argv)
    investigation, package = _simple(args.investigation, "investigation"), _simple(args.package, "package")
    if args.action == "show":
        report = review_receipt(Path(root), investigation, package)
        _print(report)
        return 1 if report["errors"] else 0
    for text in args.accept:
        if not text.strip() or text.splitlines() != [text]:
            record.error("--accept must be one non-blank line")
    try:
        if args.report == "-":
            text = sys.stdin.read()
        else:
            path = Path(args.report).expanduser()
            text = (path if path.is_absolute() else Path(root) / path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        record.error(f"--report: {error}")
    report = record_review(Path(root), investigation, package, args.kind, text, [a.strip() for a in args.accept])
    _print(report)
    return 0 if report["recorded"] else 1


# ---------------------------------------------------------------- release

def disposition_problems(record: dict) -> list[dict]:
    """List each represented flagged finding whose disposition does not allow release."""
    flags = record.get("revalidation_flags")
    if flags == "none" or flags == []:
        return []
    if not isinstance(flags, list):
        return [{"finding": None, "problem": "revalidation_flags is missing; record none or each flag"}]
    problems = []
    for flag in flags:
        flag = flag if isinstance(flag, dict) else {}
        places, disposition = flag.get("represented_in"), flag.get("disposition")
        if places == "none":
            continue  # A flagged finding the draft does not represent needs no disposition.
        if not isinstance(places, list) or not places or not all(
                isinstance(place, str) and place.strip() for place in places):
            problem = "represented_in is not a list of places; list them or record none"
        elif disposition in _DISPOSITIONS:
            continue
        else:
            problem = {None: "no disposition", "none": "no disposition",
                       "revalidate": "revalidation pending"}.get(disposition, f"unknown disposition {disposition!r}")
        problems.append({"finding": flag.get("finding"), "problem": problem})
    return problems


def release_dispositions(record: dict, prior) -> list[dict]:
    """Each represented flag's disposition, `new` unless the prior release recorded the same one.

    `prior` is the prior release's manifest, None when there is none, or False when it is unreadable
    (then `new` is None: unknown).
    """
    def key(flag):
        return flag.get("finding"), flag.get("reason"), flag.get("disposition")

    before = prior.get("revalidation_flags") if isinstance(prior, dict) else None
    before = {key(f) for f in before if isinstance(f, dict)} if isinstance(before, list) else set()
    rows = []
    for flag in record.get("revalidation_flags") if isinstance(record.get("revalidation_flags"), list) else []:
        if not isinstance(flag, dict) or not isinstance(flag.get("represented_in"), list):
            continue
        rows.append({"finding": flag.get("finding"), "reason": flag.get("reason"),
                     "represented_in": flag["represented_in"], "disposition": flag.get("disposition"),
                     "new": None if prior is False else key(flag) not in before})
    return rows


# The deck's slides that state what stays open, wherever they stand, the appendix included.
_OPEN_SLIDES = ("Limitations and open caveats", "Open questions")


def open_caveats(directory, record: dict) -> list[dict]:
    """The open caveats a release carries, new or carried forward, so its report never calls it clean while one
    remains: the headline and then each top-level bullet of the deck's Limitations and open caveats and Open
    questions slides in the findings.md under directory, as it renders and in deck order, as {"slide",
    "line", "text", "sub"}, nested items in sub and a headline's sub empty; then each represented flag
    released with its caveat, as {"finding", "reason", "represented_in"}. An omitted flag carries no caveat."""
    rows = [{"slide": slide["heading"], "line": block["line"], "text": block["text"], "sub": block.get("sub", [])}
            for slide in read_outline(Path(directory) / "findings.md")["slides"]
            if not slide["finding"] and slide["heading"] in _OPEN_SLIDES
            for block in slide["headlines"][:1] + slide["bullets"]]
    flags = record.get("revalidation_flags")
    return rows + [{"finding": flag.get("finding"), "reason": flag.get("reason"),
                    "represented_in": flag["represented_in"]}
                   for flag in (flags if isinstance(flags, list) else [])
                   if isinstance(flag, dict) and isinstance(flag.get("represented_in"), list)
                   and flag.get("disposition") == "release_with_caveat"]


def _runtime(evidence):
    """The evidence's runtime block, or unknown when it records none; stale tests the same shape."""
    runtime = evidence.get("runtime")
    if isinstance(runtime, dict) and isinstance(runtime.get("packages"), dict):
        return runtime
    return {"unknown": "evidence lacks runtime"}


def provenance_gaps(record: dict) -> list[dict]:
    """Each manifest value recorded as unknown, an {"unknown": reason} object, by its dotted field path,
    with the reason, and each requirements line a result's runtime could not read, whose packages'
    versions went unrecorded. A string is never a gap, so a settings value or a column name such as
    unknown_pickup is not one."""
    gaps = []

    def walk(value, path):
        if _is_unknown(value):
            gaps.append({"field": path, "reason": value["unknown"]})
        elif isinstance(value, dict):
            for key, item in value.items():
                if key == "unread_requirements" and isinstance(item, list):
                    # The reason's prefix is UNREAD in awb_provenance.py, which stale reports; keep the two equal.
                    gaps.extend({"field": f"{path}.{key}[{index}]",
                                 "reason": f"requirements not read, packages unrecorded: {entry}"}
                                for index, entry in enumerate(item))
                else:
                    walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    for key, value in record.items():
        if key not in {"inventory", "export_checks", "revalidation_flags", "allowed_numbers", "presentation_order"}:
            walk(value, key)
    return gaps


def checkout_only_acquisitions(root, record: dict) -> list[dict]:
    """Each cited acquisition whose Acquisitions row in foundation/sources.md shows no retained copy."""
    inputs = record.get("inputs")
    entries = inputs.get("acquisitions") if isinstance(inputs, dict) else None
    paths = sorted({e["path"] for e in entries if isinstance(e, dict) and isinstance(e.get("path"), str)}
                   if isinstance(entries, list) else set())
    if not paths:
        return []
    try:
        table = _section_table((Path(root) / "foundation/sources.md").read_text(encoding="utf-8"), "Acquisitions")
    except (OSError, UnicodeError):
        table = None
    retained = {}
    for row in table[1] if table else []:
        key = (row.get("Source ID", "").strip("`").strip(), row.get("Acquisition ID", "").strip("`").strip())
        retained[key] = row.get("Retained copy", "").strip("`").strip()
    found = []
    for path in paths:
        parts = Path(path).parts
        cell = retained.get(tuple(parts[-2:])) if len(parts) >= 2 else None
        if cell is None or cell.lower() in {"", "this checkout only"}:
            found.append({"acquisition": path, "retained_copy": cell if cell is not None else "no Acquisitions row"})
    return found


def storage_location(root) -> tuple:
    """Return (kind, location) from the README: path, unreachable, none-chosen, or unrecorded."""
    try:
        lines = (Path(root) / "README.md").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        lines = []
    values = [line[len(_STORAGE_LINE):].strip().strip("`").strip()
              for line in lines if line.startswith(_STORAGE_LINE)]
    value = values[0] if len(values) == 1 else ""
    if not value or value.lower() in {"not yet recorded", "unknown"}:
        return "unrecorded", None
    if value.lower() in {"none", "none chosen"}:
        return "none-chosen", value
    # A URL or prose needs the user's own copy, never a speculative network call.
    if "://" in value or not value.startswith(("/", "~", "./", "../")):
        return "unreachable", value
    return "path", value


def _copy_to_storage(root, local, investigation, package, number):
    """Copy one release to <location>/<investigation>/<package>/<n>/. The checkout's released/ folder is not
    repeated there, so a location the user calls releases holds no releases/.../released/ path."""
    kind, location = storage_location(root)
    if kind == "none-chosen":
        return {"status": "none chosen",
                "warning": f"no release storage was chosen; {_rel(root, local)} in this checkout is the only copy"}
    destination = f"{location}/{investigation}/{package}/{number}/" if location else None
    instruction = (f"copy {_rel(root, local)}/ to {destination}" if destination else
                   f"record where released packages are kept, then copy {_rel(root, local)}/ there "
                   f"as <location>/{investigation}/{package}/{number}/")
    if kind != "path":
        return {"status": kind, "location": location, "instruction": instruction}
    base = Path(location).expanduser()
    base = base if base.is_absolute() else Path(root) / base
    if not base.is_dir():
        return {"status": "unreachable", "location": location, "instruction": instruction}
    target = base / investigation / package / number
    try:
        if target.exists():
            # An identical earlier copy is already in place; anything else is left for the user.
            differences = compare_trees(local, target)
            if not differences:
                return {"status": "already copied", "copy": str(target), "compare_trees": []}
            return {"status": "conflict", "copy": str(target), "compare_trees": differences,
                    "problem": "destination already exists and differs; nothing was overwritten"}
        shutil.copytree(local, target)
        differences = compare_trees(local, target)
    except (OSError, ValueError, shutil.Error) as error:
        return {"status": "copy failed", "copy": str(target), "problem": str(error),
                "instruction": instruction}
    return {"status": "copied" if not differences else "mismatch", "copy": str(target),
            "compare_trees": differences}


_STORAGE_FAILURES = {"conflict", "copy failed", "mismatch"}


def release(root, investigation, package) -> dict:
    """Verify the draft and its review receipt, copy it to the next numbered release, stamp it with the
    review it passed, and copy it to storage."""
    root = Path(root)
    package_dir = _package_dir(root, investigation, package)
    check_report = check_draft(root, investigation, package, verify_only=True)
    report = {"released": False, "check": {"passed": check_report["passed"]}}
    if not _structure_passed(check_report):
        report["refused"] = "check-draft --verify-only does not pass"
        report["check"] = check_report
        return report
    record = _read_json(package_dir / "draft" / MANIFEST)
    problems = disposition_problems(record)
    if check_report["unmatched_flags"] or problems:
        report["refused"] = "flagged findings without a release disposition"
        report["unmatched_flags"] = check_report["unmatched_flags"]
        report["dispositions"] = problems
        return report
    review = review_receipt(root, investigation, package)
    if review["status"] != "current":
        report["refused"] = NO_REVIEW
        report["review"] = {"status": review["status"], "changed": review["changed"]}
        return report

    released = package_dir / "released"
    existing = [p for p in released.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()] \
        if released.is_dir() else []
    prior = max(existing, key=lambda p: int(p.name), default=None)
    number = f"{int(prior.name) + 1 if prior else 1:03d}"  # Gaps stay unfilled.
    try:
        prior_record = _read_json(prior / MANIFEST) if prior else None
    except (OSError, ValueError):
        prior_record = False
    target = released / number
    staging = released / f".{number}.{os.getpid()}.tmp"
    released.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(package_dir / "draft", staging)
        record.update({"status": "release", "release_number": number, "released_at": _now(),
                       "prior_release": f"released/{prior.name}" if prior else "none",
                       "review": {key: review[key] for key in ("kind", "recorded_at", "accepted")}})
        _write_json(staging / MANIFEST, record)
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    report.update(released=True, release=_rel(root, target), release_number=number,
                  released_at=record["released_at"], prior_release=record["prior_release"], review=record["review"],
                  verify=verify(target, record["inventory"]),
                  datasets=record.get("dataset_selection", {"unknown": "dataset_selection is not recorded"}),
                  dispositions=release_dispositions(record, prior_record),
                  open_caveats=open_caveats(target, record),
                  provenance_gaps=provenance_gaps(record),
                  checkout_only_acquisitions=checkout_only_acquisitions(root, record),
                  storage=_copy_to_storage(root, target, investigation, package, number))
    return report


def cli_release(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py release", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy a draft that passes check-draft --verify-only, with every flagged finding "
                    "recorded and disposed, to the next numbered release and to release storage.",
        epilog="Prints one JSON line.\nRefuses, creating nothing, unless check-draft --verify-only passes, "
               "every represented revalidation_flags entry is omit or release_with_caveat, and review-receipt "
               "show reports current; a flag refusal lists unmatched_flags and dispositions, and a review "
               "refusal the review's status and changed. Its draft_markers rows do not refuse: run check-draft "
               "--verify-only first to show them.\nOn success it prints the report fields: datasets, "
               "review (the passed review's kind, recorded_at, and accepted problems, which the released manifest records too), dispositions (new: absent from the prior release's manifest), open_caveats, provenance_gaps, "
               "checkout_only_acquisitions, verify (the local copy), and storage.\nopen_caveats lists the open "
               "caveats the release carries, new or carried forward: the headline and then each bullet of the deck's "
               "Limitations and open caveats and Open questions slides, wherever they stand, as slide, line, "
               "text, and sub (nested items, empty for a headline), then each represented flag released with "
               "its caveat, as finding, reason, and "
               "represented_in; while one remains, the release is not clean.\nThe release is "
               "deliveries/<investigation>/<package>/released/<n>/; storage holds its copy at "
               "<location>/<investigation>/<package>/<n>/.\nstorage.status is copied or "
               "already copied (empty compare_trees), mismatch or conflict (compare_trees rows), copy failed "
               "(problem), unreachable or unrecorded (instruction), or none chosen (warning).\nExit 1 on "
               "refusal, a verify row, or storage status mismatch, conflict, or copy failed.")
    _package_arguments(parser)
    args = parser.parse_args(argv)
    report = release(Path(root), _simple(args.investigation, "investigation"), _simple(args.package, "package"))
    _print(report)
    if not report["released"]:
        return 1
    # A failed local verify or storage copy needs attention; the release itself stands.
    return 1 if report["verify"] or report["storage"]["status"] in _STORAGE_FAILURES else 0


# ---------------------------------------------------------------- copy-releases

def copy_releases(root, investigation, package=None) -> dict:
    """Copy every numbered release to the recorded release storage and compare each copy."""
    root = Path(root)
    kind, location = storage_location(root)
    report = {"location": location, "releases": [], "errors": []}
    base = root / "deliveries" / investigation
    if package is not None and not (base / package).is_dir():
        report["errors"].append(f"no package at {_rel(root, base / package)}")
        return report
    packages = [base / package] if package else sorted(p for p in base.iterdir() if p.is_dir()) \
        if base.is_dir() else []
    for directory in packages:
        released = directory / "released"
        numbers = sorted((p for p in released.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()),
                         key=lambda p: int(p.name)) if released.is_dir() else []
        report["releases"] += [{"release": _rel(root, p),
                                "storage": _copy_to_storage(root, p, investigation, directory.name, p.name)}
                               for p in numbers]
    if not report["releases"]:
        report["errors"].append(f"no numbered releases under {_rel(root, base)}")
    return report


def cli_copy_releases(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py copy-releases", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy every existing numbered release of an investigation (or one package) to the "
                    "README's recorded release storage and compare each copy with compare_trees.",
        epilog="Prints one JSON line with one storage row per release, statuses as release reports them; each "
               "release copies to <location>/<investigation>/<package>/<n>/, and an identical existing copy is "
               "already copied, a differing one a conflict, never overwritten.\n"
               "Exit 1 when no release exists or any storage status is mismatch, conflict, or copy failed.")
    _package_arguments(parser, package=False)
    parser.add_argument("package", nargs="?", help="package name under deliveries/<investigation>/ "
                                                   "(default: every package)")
    args = parser.parse_args(argv)
    report = copy_releases(Path(root), _simple(args.investigation, "investigation"),
                           _simple(args.package, "package") if args.package else None)
    _print(report)
    failed = report["errors"] or any(r["storage"]["status"] in _STORAGE_FAILURES for r in report["releases"])
    return 1 if failed else 0
