"""Find internal names left in an audience-facing Markdown file such as `findings.md`.

Copy this file to `src/packaging/findings.py`; do not import it from the skill folder.
"""

import os
import re
from pathlib import Path

_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_TOKEN = re.compile(r"\S+")

# Wrapping punctuation and Markdown emphasis around a token; leading dots stay so `./x` is a path.
# Underscores are stripped only in matching pairs (`_word_`), so `__init__.py` keeps its own.
_LEADING = "([{<\"'*~!“‘"
_TRAILING = ")]}>\"'*~.,;:!?”’"
_POSSESSIVE = re.compile(r"['’]s$")

_PATH = re.compile(r"\w/\w")
_FRACTION = re.compile(r"[\d.,]+(?:/[\d.,]+)+")  # 3/4, 6/30/2026: numbers, not paths
_FILE = re.compile(
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


def _token_kind(token):
    if token.startswith(("./", "../")) or (_PATH.search(token) and not _FRACTION.fullmatch(token)):
        return "path"
    if _FILE.search(token):
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


def _scan_line(number, line, names):
    found = []
    for match in _CODE_SPAN.finditer(line):
        found.append((match.start(), "code", match.group(0)))
        line = _blank(line, match.start(), match.end())
    for match in _LINK_TARGET.finditer(line):
        line = _blank(line, match.start() + 1, match.end())

    taken = []
    if names is not None:
        for match in names.finditer(line):
            found.append((match.start(), "name", match.group(0)))
            taken.append((match.start(), match.end()))

    for match in _TOKEN.finditer(line):
        token = _unwrap(match.group(0))
        start = match.start() + match.group(0).find(token)
        end = start + len(token)
        if not token or any(start < stop and begin < end for begin, stop in taken):
            continue
        kind = _token_kind(token)
        if kind:
            found.append((start, kind, token))

    return [{"line": number, "kind": kind, "text": text} for _, kind, text in sorted(found)]


def check(path: str | os.PathLike, *, names=()) -> list[dict]:
    """List code, paths, file names, identifiers, SHAs, and given names, by line then column."""
    text = Path(path).read_text(encoding="utf-8")
    text = _COMMENT.sub(lambda match: " " + "\n" * match.group(0).count("\n"), text)
    pattern = _name_pattern(names)

    rows = []
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        if fence is not None:
            closing = _FENCE.match(line)
            if (closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence)
                    and not line[closing.end():].strip()):
                fence = None
            continue
        opening = _FENCE.match(line)
        if opening and not (opening.group(1)[0] == "`" and "`" in line[opening.end():]):
            fence = opening.group(1)
            rows.append({"line": number, "kind": "code", "text": line.strip()})
            continue
        rows.extend(_scan_line(number, line, pattern))
    return rows
