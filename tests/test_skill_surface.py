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


def section(path, heading):
    """A SKILL.md section's text from its heading to the next heading of any level, whitespace collapsed."""
    text = (ROOT / path).read_text(encoding='utf-8')
    body = text.split(f'\n{heading}\n', 1)[1]
    return ' '.join(re.split(r'\n#{1,6} ', body, maxsplit=1)[0].split())


def test_a_folded_revision_waits_for_the_users_check_before_release():
    # A revision requested together with the release is shown to the user, and the release waits for their
    # yes, so a change they have not seen is never frozen into a numbered release.
    milestone = section('.agents/skills/awb-package/SKILL.md', '## Delivery milestone')
    assert 'show the user the changed slides' in milestone
    assert 'wait for their yes before invoking `awb-release`' in milestone
    assert 'unless they said to release without seeing it' in milestone


def test_release_shows_draft_markers_and_reports_every_open_caveat():
    release = section('.agents/skills/awb-release/SKILL.md', '## 3. Release')
    assert '`draft_markers`' in release and 'confirm' in release and 'revise' in release
    report = section('.agents/skills/awb-release/SKILL.md', '## Report')
    # An open caveat the deck states, such as one on its limitations slide, is listed too, not only a flag.
    assert '`open_caveats`' in report and '**Limitations and open caveats**' in report
    # The limitations slide's headline states the caveat that matters most, so it is listed with the bullets.
    assert 'the headline and bullets of the deck' in report
    assert 'never call the release clean' in report and 'say nothing is outstanding' in report


def test_status_asks_to_copy_releases_when_recorded_storage_lacks_the_latest():
    # latest_release_in_storage is false only when storage is recorded and reachable, so the request copies the
    # releases there rather than asking again where releases are kept.
    rows = [line for line in (ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').splitlines()
            if line.startswith('| ')]
    copy = [row for row in rows if '`latest_release_in_storage`' in row]
    assert copy == ['| A package\'s `latest_release_in_storage` is false | "Copy the <package> releases to storage" '
                    '| `python3 src/awb.py copy-releases <investigation> <package>` | risk |']
    record = [row for row in rows if 'Record where releases are kept' in row]
    assert len(record) == 1 and 'latest_release_in_storage' not in record[0]


def test_a_caveat_only_revision_names_the_full_export_for_a_charts_row():
    # A --result-only export keeps the manifest's charts entries, so a charts row asking to rerun export
    # needs every --chart.
    export = section('.agents/skills/awb-package/SKILL.md', '## 4. Export the files and provenance')
    assert 'pass only `--result`' in export
    assert 'A `check-draft` `charts` row that asks to rerun export needs the full export, with every `--chart`.' in export
