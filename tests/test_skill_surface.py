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


def test_review_checks_reconciliation_claims_and_scopes_re_reviews():
    # The review holds a checked or reconciliation sentence to a recorded result or check, pairing with the
    # warning state finding gives, and the package contract tells the writer so; a re-review after repairs may
    # be scoped, judging rules added or changed since in full, but never the last one before the request's
    # final check-draft or the one that completes it, and release always runs the full review.
    def read(path):
        return ' '.join((ROOT / '.agents/skills' / path).read_text(encoding='utf-8').split())

    review = read('awb-package/references/review.md')
    package = read('awb-package/SKILL.md')
    release = read('awb-release/SKILL.md')
    reviewer = read('awb-package/assets/awb-package-reviewer.agent.md')
    provenance = read('awb-init/references/provenance.md')

    assert ('asserts that something was checked or verified, reconciles, sums or adds up to, or matches cites the '
            'recorded result or check that establishes it') in review
    assert 'A sentence without one is a narrative problem' in review
    assert '`awb.py state finding`' in review and 'pair' in review
    assert 'asserts a reconciliation or a completed check' in review and 'asserts a reconciliation or a completed' \
        in provenance
    assert 'Report every violation and narrative problem in this one pass, quoting each' in review
    assert 'settle everything it reports, as above, before the review runs again' in review
    assert ('Within one `awb-package` request, the review run again after repairs may be a scoped re-review: '
            'give the reviewer the prior report and a diff') in review
    assert ('a full review is still required before the request\'s final `check-draft`, and `awb-release` always '
            'runs the full review') in review
    assert '`review (scoped):`' in review
    # The draft is outside Git, so the diff is taken against a copy kept when the prior review was launched,
    # and with no copy the next review is full; a slide or document rule is judged on each slide or file a
    # changed line falls in.
    assert '`diff -u <copy> <current file>`' in review and 'Git-ignored `deliveries/` folder' in review
    # The scoped diff is made against the prior review's copy before that copy is replaced; replacing it first
    # would leave an empty diff.
    diff_at = review.index('For a scoped re-review, first make the diff against the copy the prior review left')
    copy_at = review.index('Then, for every review `awb-package` launches, full or scoped, and after any scoped '
                           'diff is made, copy those files to the scratch folder, replacing the copy an earlier '
                           'review left')
    assert diff_at < copy_at
    assert 'whenever `awb-package` launches a review, first copy' not in review
    assert 'When no copy of what the prior review read was kept, the next review is a full one' in review
    assert 'for a `slide` or `document` rule, on each slide or file that holds one' in review
    assert 'the caller settles them all before the next review' in review
    assert ('judge each rule added or changed since, as the diff of `foundation/review-rules.md` shows, against '
            'every narrative in full') in review
    assert ('Only a full review, whose last line opens `review:`, can complete a request or a release; a scoped '
            're-review, whose last line opens `review (scoped):`, never does') in review
    assert 'for a scoped re-review, the prior report and the diff' in review
    assert '`slide` rule' in review and '`document` rule' in review
    assert 'scoped re-review' in package and 'the last review before the final `check-draft` is a full one' in package
    assert 'the last review is a full review, passed and not stale' in package
    contract = read('awb-package/references/package-contract.md')
    assert ('A sentence asserting that something was checked or verified, reconciles, sums or adds up to, or matches '
            'cites the check that establishes it') in contract
    assert 'Run the full read-only review' in release and 'never a scoped re-review' in release
    assert 'one pass' in reviewer and 'scoped' in reviewer and 'the evidence a narrative cites' in reviewer
