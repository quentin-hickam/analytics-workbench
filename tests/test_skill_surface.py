"""Public skill metadata and repository content contracts."""

import json
import os
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]


def skill_metadata(text):
    """Accepted input: --- LF, name: VALUE LF, description: JSON_STRING LF,
    --- LF, then any Markdown body. Fields occur exactly once, in that order.
    Refuse every other header with ValueError. This repository convention is a
    subset of YAML, not a general YAML reader: no extra keys, multiline scalars,
    comments, single quotes or unquoted descriptions. JSON escapes are accepted.
    Name/folder and character limits are checked separately below.
    """
    header, separator, _ = text.partition('\n---\n')
    match = re.fullmatch(r'---\nname: ([^\n]+)\ndescription: ("[^\n]*")', header)
    if not separator or not match:
        raise ValueError('expected name and JSON-quoted description frontmatter')
    try:
        description = json.loads(match[2])
    except ValueError as error:
        raise ValueError('invalid JSON-quoted description') from error
    return match[1], description


@pytest.mark.parametrize(('header', 'expected'), [
    ('---\nname: sample-1\ndescription: "Look at this data."\n---\n# Body',
     ('sample-1', 'Look at this data.')),
    ('---\nname: sample\ndescription: "Say \\"hello\\" or \\u00e9."\n---\n',
     ('sample', 'Say "hello" or é.')),
    ('name: sample\ndescription: "Text"\n---\n', None),
    ('---\nname: sample\ndescription: Plain text\n---\n', None),
    ("---\nname: sample\ndescription: 'Text'\n---\n", None),
    ('---\nname: sample\ndescription: >\n  Text\n---\n', None),
    ('---\nname: sample\nname: duplicate\ndescription: "Text"\n---\n', None),
    ('---\ndescription: "Text"\nname: sample\n---\n', None),
    ('---\nname: sample\ndescription: "Text"\nextra: true\n---\n', None),
    ('---\nname: sample\ndescription: "bad\\q"\n---\n', None),
    ('---\nname: sample\ndescription: "Text"\n---', None),
])
def test_skill_metadata_accepted_and_refused_forms(header, expected):
    if expected is None:
        with pytest.raises(ValueError):
            skill_metadata(header)
    else:
        assert skill_metadata(header) == expected


def shipped_skills(root):
    """The repository's skills live only in .agents/skills/<name>/SKILL.md.
    Scope to that folder, not the whole checkout: an rglob would also collect
    stale copies in ignored nested worktrees such as .claude/worktrees/.
    """
    return sorted(root.glob('.agents/skills/*/SKILL.md'))


def test_shipped_skills_skip_nested_copies(tmp_path):
    shipped = tmp_path / '.agents/skills/good/SKILL.md'
    nested = tmp_path / '.claude/worktrees/old/.agents/skills/bad/SKILL.md'
    for path in (shipped, nested):
        path.parent.mkdir(parents=True)
        path.write_text('not frontmatter\n', encoding='utf-8')
    assert shipped_skills(tmp_path) == [shipped]


def test_repository_ships_skills():
    # Guards the parametrized test below against silently collecting nothing.
    assert shipped_skills(ROOT)


@pytest.mark.parametrize('path', shipped_skills(ROOT),
                         ids=lambda path: str(path.relative_to(ROOT)))
def test_every_skill_has_loadable_metadata(path):
    name, description = skill_metadata(path.read_text(encoding='utf-8'))
    assert name == path.parent.name
    assert re.fullmatch(r'[a-z0-9-]{1,64}', name), name
    assert 1 <= len(description) <= 1024


# Split so this file does not itself contain the retired name.
RETIRED_SKILL = b'awb-' + b'eda'


def mentions_retired_skill(data):
    """Accept any bytes; match only the exact case-sensitive ASCII substring.
    Other bytes are nonmatches, not errors. No decoding, word boundaries, case
    folding or normalization: UTF-16 and split/escaped spellings are not matches.
    """
    return RETIRED_SKILL in data


@pytest.mark.parametrize(('data', 'expected'), [
    (RETIRED_SKILL, True),
    (b'path/' + RETIRED_SKILL + b'/SKILL.md', True),
    (b'awb-explore', False),
    (b'AWB-EDA', False),
    (b'awb- eda', False),
    ('awb-'.encode('utf-16-le') + 'eda'.encode('utf-16-le'), False),
])
def test_retired_skill_exact_byte_matches(data, expected):
    assert mentions_retired_skill(data) is expected


def test_repository_has_no_retired_skill_outside_changelog():
    # Scope: tracked and nonignored untracked working-tree files, including
    # dotfiles, binary content and symlink targets. Deleted files, Git
    # history/metadata and ignored build/cache files are outside the repository
    # text contract. Only the root CHANGELOG.md is exempt. File paths are
    # checked along with contents.
    import subprocess

    result = subprocess.run(['git', 'ls-files', '--cached', '--others',
                             '--exclude-standard', '-z'], cwd=ROOT,
                            capture_output=True, check=True)
    offenders = []
    for entry in result.stdout.split(b'\0'):
        if not entry or entry == b'CHANGELOG.md':
            continue
        path = ROOT / entry.decode('utf-8')
        # Git stores a symlink's target as its content, and the target may dangle.
        if path.is_symlink():
            data = os.fsencode(os.readlink(path))
        elif path.is_file():
            data = path.read_bytes()
        else:
            continue
        if mentions_retired_skill(entry) or mentions_retired_skill(data):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], offenders


def question_add_priorities(text):
    """Accepted input: LF text with literal `python3 src/awb.py questions add `
    examples, either as a whole line (leading whitespace allowed) or inside
    single-backtick inline code. Arguments occupy that line/span, use POSIX shlex quoting, and contain
    --priority followed by must, should, could, or the placeholder <priority>.
    Each whole-word 'questions add' occurrence must belong to such an example;
    refuse other spellings/contexts, missing/invalid priorities, broken quotes,
    backtick nesting and shell continuations with ValueError. Other prose is
    ignored. Known limits: a repository example convention, not a Markdown or
    shell interpreter; argument meanings beyond priority are not validated.
    """
    import shlex

    commands = []
    for line in text.splitlines():
        mentions = re.findall(r"\bquestions add\b", line)
        if not mentions:
            continue
        spans = line.split("`")
        if len(spans) % 2 == 0 or any(not span for span in spans[1::2]):
            raise ValueError("use closed single-backtick command spans")
        candidates = spans[1::2] if len(spans) > 1 else [line.strip()]
        found = [span for span in candidates if span.startswith("python3 src/awb.py questions add ")]
        if len(found) != len(mentions):
            raise ValueError("use a literal single-line questions add command")
        for command in found:
            if "\\" in command:
                raise ValueError("shell escapes and continuations are outside the example grammar")
            args = shlex.split(command)
            priorities = [args[i + 1] if i + 1 < len(args) else None
                          for i, arg in enumerate(args) if arg == "--priority"]
            if len(priorities) != 1 or priorities[0] not in ("must", "should", "could", "<priority>"):
                raise ValueError("questions add needs one --priority must|should|could|<priority>")
            commands.append(priorities[0])
    return commands


@pytest.mark.parametrize("text, expected", [
    ('python3 src/awb.py questions add "Which region?" --priority must', ["must"]),
    ('  python3 src/awb.py questions add "Which region?" --priority should', ["should"]),
    ('Use `python3 src/awb.py questions add "Which region?" --priority could`.', ["could"]),
    ('Use `python3 src/awb.py questions add "<question>" --priority <priority>`.', ["<priority>"]),
    ('Ordinary prose; questions added.', []),
    ('python3 src/awb.py questions add "Which region?"', None),
    ('python3 src/awb.py questions add "Which region?" --priority urgent', None),
    ('python3 src/awb.py questions add "Which region?" --priority', None),
    ('python3 src/awb.py questions add "Which region?" --priority must --priority could', None),
    ('python3 src/awb.py questions add "Which region?" --priority must --priority', None),
    ('Use questions add with a priority.', None),
    ('`python3 src/awb.py questions add "Which region?" --priority must', None),
    ('``python3 src/awb.py questions add "Which region?" --priority must``', None),
    ('python3 src/awb.py questions add "Which region? --priority must', None),
    ('python3 src/awb.py questions add "Which region?" \\\n --priority must', None),
])
def test_question_add_example_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            question_add_priorities(text)
    else:
        assert question_add_priorities(text) == expected


@pytest.mark.parametrize("path", shipped_skills(ROOT), ids=lambda path: path.parent.name)
def test_every_question_add_example_carries_priority(path):
    question_add_priorities(path.read_text(encoding="utf-8"))


def test_headline_checkpoint_names_both_modes_and_never_waits_unconditionally():
    # The headline checkpoint is preview-and-wait or draft-then-review; neither the skill nor any other
    # shipped text keeps the old unconditional wait before writing the slides.
    package = (ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8')
    contract = (ROOT / '.agents/skills/awb-package/references/package-contract.md').read_text(encoding='utf-8')
    brief = (ROOT / '.agents/skills/awb-init/assets/workbench/investigation/brief.md').read_text(encoding='utf-8')
    # The current request comes before a mode the brief recorded for an earlier package.
    precedence = ("the mode the request states; **draft-then-review** when the request supplies the storyline or "
                  "asks for the full draft; the mode the brief's **Audience** section records; **preview-and-wait**")
    for text in (package, contract):
        assert '**preview-and-wait**' in text and '**draft-then-review**' in text
        assert precedence in ' '.join(text.split())
    assert 'preview-and-wait' in brief and 'draft-then-review' in brief
    retired = ('wait for their answer before expanding the slides', "and wait for the user's approval or reorder")
    offenders = [(str(path.relative_to(ROOT)), phrase) for path in sorted((ROOT / '.agents/skills').rglob('*'))
                 if path.is_file() and path.suffix in ('.md', '.py')
                 for phrase in retired if phrase in ' '.join(path.read_text(encoding='utf-8').split())]
    assert offenders == []


AGENTS = ROOT / '.agents/skills/awb-init/assets/workbench/AGENTS.md'


def section(text, heading):
    """Accepted input: LF Markdown text holding exactly one line that is `heading`
    itself, such as `## Conversation`, at column 0. Returns the lines after it up to
    the next heading of its level or above (one to as many `#` as it has, then a
    space), or to the end. Refuse a heading argument that is not `#` marks, a space,
    and text, and a heading line that is absent or repeated, with ValueError. Known
    limits: headings inside code fences are read as headings; Setext headings are
    not headings.
    """
    lines = text.split('\n')
    level = len(heading) - len(heading.lstrip('#'))
    if not 1 <= level <= 6 or heading[level:level + 1] != ' ' or not heading[level + 1:].strip():
        raise ValueError('expected an ATX heading such as "## Conversation"')
    starts = [index for index, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        raise ValueError(f'expected exactly one {heading!r} line, found {len(starts)}')
    body = []
    for line in lines[starts[0] + 1:]:
        marks = len(line) - len(line.lstrip('#'))
        if 1 <= marks <= level and line[marks:marks + 1] == ' ':
            break
        body.append(line)
    return '\n'.join(body)


@pytest.mark.parametrize(('text', 'heading', 'expected'), [
    ('# T\n## A\none\n## B\ntwo\n', '## A', 'one'),
    ('## A\none\n### Sub\nkept\n## B\n', '## A', 'one\n### Sub\nkept'),
    ('## A\none\n# Top\nlater\n', '## A', 'one'),
    ('## A\none\n#hashtag line\n', '## A', 'one\n#hashtag line\n'),
    ('## 5. Report\n- a\n', '## 5. Report', '- a\n'),
    ('## B\ntwo\n', '## A', None),
    ('## A\none\n## A\ntwo\n', '## A', None),
    (' ## A\none\n', '## A', None),
    ('## A\n', 'A', None),
    ('## A\n', '##A', None),
    ('## \n', '## ', None),
    ('####### A\n', '####### A', None),
])
def test_section_accepted_and_refused_forms(text, heading, expected):
    if expected is None:
        with pytest.raises(ValueError):
            section(text, heading)
    else:
        assert section(text, heading) == expected


FOOTER_RULE = 'A turn that changed workbench records ends with'


def footer_example(text):
    """Accepted input: LF text with exactly one line that starts with FOOTER_RULE and
    holds exactly one `For example: `; returns what follows it on that line, stripped
    and nonempty. Refuse no or several footer lines, a footer line without exactly one
    `For example: `, and an empty example with ValueError. Other lines are ignored.
    """
    rules = [line for line in text.split('\n') if line.startswith(FOOTER_RULE)]
    if len(rules) != 1:
        raise ValueError(f'expected one footer rule line, found {len(rules)}')
    parts = rules[0].split('For example: ')
    if len(parts) != 2 or not parts[1].strip():
        raise ValueError('the footer rule needs exactly one nonempty "For example: "')
    return parts[1].strip()


@pytest.mark.parametrize(('text', 'expected'), [
    (FOOTER_RULE + ' one line. For example: Your two questions: 1 answered · next: explore.\n',
     'Your two questions: 1 answered · next: explore.'),
    ('Intro.\n\n' + FOOTER_RULE + ' a line. For example: next: clean the data. \nAfter.\n',
     'next: clean the data.'),
    ('No footer here.\n', None),
    (FOOTER_RULE + ' a line.\n', None),
    (FOOTER_RULE + ' a line. For example: \n', None),
    (FOOTER_RULE + ' For example: a. For example: b.\n', None),
    (FOOTER_RULE + ' a. For example: a.\n' + FOOTER_RULE + ' b. For example: b.\n', None),
    ('  ' + FOOTER_RULE + ' a line. For example: a.\n', None),
])
def test_footer_example_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            footer_example(text)
    else:
        assert footer_example(text) == expected


def test_record_footer_example_counts_the_users_questions_not_ledger_rows():
    # The footer once taught "Questions: answered 1 · opened 2 (1 needs you)": ledger tallies that
    # counted every sub-question and announced a question needing the user without asking it.
    example = footer_example(AGENTS.read_text(encoding='utf-8'))
    for ledger_count in ('Questions:', 'opened', 'needs you'):
        assert ledger_count not in example
    assert not re.search(r'\b(answered|opened|added|open)\s+\d', example), example
    assert example.startswith('Your ') and ' questions: ' in example


def test_conversation_rules_ask_inline_state_impact_and_claim_no_attachment():
    conversation = ' '.join(section(AGENTS.read_text(encoding='utf-8'), '## Conversation').split())
    # A pause is a plain decision request, asked in the message that needs it.
    assert 'When you need the user, ask in that message for a plain decision, ' \
           'with your recommendation and the alternative' in conversation
    assert 'never send them to a skill or instruction file' in conversation
    # An environment or tool limit is reported by its impact, or not at all.
    assert 'Report an environment or tool limit only when it affects the user: ' \
           'whether they must act, and what the workbench does instead.' in conversation
    # Files are named by path; nothing is attached.
    assert 'giving file paths; never say a file was attached or sent.' in conversation


def test_first_pass_answers_keep_to_the_evidence():
    invariants = ' '.join(section(AGENTS.read_text(encoding='utf-8'), '## Analytical invariants').split())
    # A saved query's figure is exploration until run.py records it as a result.
    assert "can become a finding; present other query output, saved queries' too, as exploration" in invariants
    for rule in ('offer an untested one as a question, not an answer',
                 'Record what the user recalls as their statement, not as confirmed',
                 'name what a comparison leaves uncontrolled when a decision rests on it'):
        assert rule in invariants


def test_commit_preference_is_a_readme_line_the_rules_follow():
    readme = (ROOT / '.agents/skills/awb-init/assets/workbench/README.md').read_text(encoding='utf-8')
    assert re.search(r'^Commits: on request$', readme, re.M)
    agents = ' '.join(AGENTS.read_text(encoding='utf-8').split())
    assert "README's `Commits:` line says `as I go`" in agents


def test_scoping_asks_every_user_decision_before_writing_records():
    scope = ' '.join((ROOT / '.agents/skills/awb-scope/SKILL.md').read_text(encoding='utf-8').split())
    assert 'now or later' not in scope
    interview = ' '.join(section((ROOT / '.agents/skills/awb-scope/SKILL.md').read_text(encoding='utf-8'),
                                 '## 2. Interview').split())
    # Every decision the user can answer is asked before the records are written; one is parked only
    # when the user defers it, so a report never lists the user's own decisions unasked.
    assert 'Before writing the records, ask the user every open decision they can answer' in interview
    assert 'record one as an open user question only when the user defers it' in interview
    init = ' '.join(section((ROOT / '.agents/skills/awb-init/SKILL.md').read_text(encoding='utf-8'),
                            '## 4. Hand off the question').split())
    assert "run `awb-scope`'s first interview round before it creates the investigation, asking it in this report" in init


def list_items(text):
    """Accepted input: LF Markdown text whose list items start at column 0 with `- `.
    Returns those lines, each without its marker; a line that does not start a list
    item, such as prose or an item's wrapped continuation, is ignored. Refuse a nested
    item (whitespace, then `-`, `*`, `+`, or digits and `.` or `)`, then a space) and a
    top-level `*`, `+`, or numbered item with ValueError, so no item escapes the count.
    """
    items = []
    for line in text.split('\n'):
        if re.match(r'\s+([-*+]|\d+[.)])\s', line):
            raise ValueError(f'nested list item: {line!r}')
        if re.match(r'([*+]|\d+[.)])\s', line):
            raise ValueError(f'list items start with "- ": {line!r}')
        if line.startswith('- '):
            items.append(line[2:])
    return items


@pytest.mark.parametrize(('text', 'expected'), [
    ('Report:\n\n- one;\n- two; and\n- three.\n\nAfter.\n', ['one;', 'two; and', 'three.']),
    ('Prose with - a dash.\n', []),
    ('-not an item\n', []),
    ('- one\n  - nested\n', None),
    ('- one\n    1. nested\n', None),
    ('* starred\n', None),
    ('+ plus\n', None),
    ('1. numbered\n', None),
    ('2) numbered\n', None),
])
def test_list_items_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            list_items(text)
    else:
        assert list_items(text) == expected


def test_setup_report_has_at_most_five_items_and_keeps_the_host_instruction_file():
    report = section((ROOT / '.agents/skills/awb-init/SKILL.md').read_text(encoding='utf-8'), '## 5. Report')
    items = list_items(report)
    assert 1 <= len(items) <= 5, items
    assert sum('host instruction file' in item for item in items) == 1
    assert any('impact' in item for item in items)
