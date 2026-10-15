"""Public skill metadata and repository content contracts."""

import json
import os
import posixpath
import subprocess
import tempfile
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


def skill_section(path, heading):
    """A SKILL.md section's text from its heading to the next heading of any level, whitespace collapsed."""
    text = (ROOT / path).read_text(encoding='utf-8')
    body = text.split(f'\n{heading}\n', 1)[1]
    return ' '.join(re.split(r'\n#{1,6} ', body, maxsplit=1)[0].split())


def test_a_folded_revision_waits_for_the_users_check_before_release():
    # A revision requested together with the release is shown to the user, and the release waits for their
    # yes, so a change they have not seen is never frozen into a numbered release.
    milestone = skill_section('.agents/skills/awb-package/SKILL.md', '## Delivery milestone')
    assert 'show the user the changed slides' in milestone
    assert 'wait for their yes before invoking `awb-release`' in milestone
    assert 'unless they said to release without seeing it' in milestone


def test_release_shows_draft_markers_and_reports_every_open_caveat():
    release = skill_section('.agents/skills/awb-release/SKILL.md', '## 3. Release')
    assert '`draft_markers`' in release and 'confirm' in release and 'revise' in release
    report = skill_section('.agents/skills/awb-release/SKILL.md', '## Report')
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
    export = skill_section('.agents/skills/awb-package/SKILL.md', '## 4. Export the files and provenance')
    assert 'pass only `--result`' in export
    assert 'A `check-draft` `charts` row that asks to rerun export needs the full export, with every `--chart`.' in export


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
    for rule in ('offer an untested explanation as a question, not an answer',
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
    # A repair reports more than setup does; step 5 says so rather than capping a repair at five items.
    assert 'A repair report adds what [references/repair.md](references/repair.md) says to report' \
           in ' '.join(report.split())


def test_only_the_users_questions_are_roots():
    # Status and the turn footer count the ledger's roots as the user's questions. A stakeholder's
    # threshold or a deferred decision left as a root was counted as one the user asked, so scoping
    # records each question the user asks as a root and puts every other question under one.
    interview = ' '.join(section((ROOT / '.agents/skills/awb-scope/SKILL.md').read_text(encoding='utf-8'),
                                 '## 2. Interview').split())
    assert 'so a root is only a question the user asked: record each one they ask' in interview
    assert ("Every other question, such as a stakeholder's threshold, a decision the user deferred, "
            "or a method choice, takes as parent the user's question it serves") in interview
    record = ' '.join(section((ROOT / '.agents/skills/awb-brainstorm/SKILL.md').read_text(encoding='utf-8'),
                              '## 3. Record the choices').split())
    assert 'empty for a root' not in record
    assert 'leave the parent empty only when the user takes the question as one of their own' in record
    # The footer names the user's questions as the roots and counts them only when they changed.
    agents = ' '.join(AGENTS.read_text(encoding='utf-8').split())
    assert ("ends with one plain line: what changed for the user's questions, the ledger's roots, "
            "if anything, and the next step") in agents
    status = ' '.join((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').split())
    assert 'lead with `roots`, the questions the user asked' in status
    assert 'Report `questions.counts`, the totals with every sub-question, only on request' in status


def test_analysis_records_its_questions_under_the_one_they_serve():
    # `questions add` defaults --parent to empty, so a question raised mid-analysis, such as whether a
    # dip is seasonal, became a root and was counted as one the user asked. The analysis guide gives
    # the analysis path the parent rule scoping, brainstorming, and exploration follow.
    add = ' '.join(section((ROOT / '.agents/skills/awb-init/assets/workbench/workbench-guides/analysis.md')
                           .read_text(encoding='utf-8'), '## Add a result').split())
    assert ("Record a question the analysis raises, such as whether a dip is seasonal, with "
            "`awb.py questions add --origin analysis` and the question it serves as `--parent`.") in add
    assert 'so only a question the user asks is a root' in add
    # Chat-driven work reads no guide, so the always-loaded rule names the parent too.
    agents = ' '.join(section(AGENTS.read_text(encoding='utf-8'), '## Record maintenance').split())
    assert ("record a question the work raises with `questions add --parent <question it serves>`"
            in agents)
    # A ledger written before roots meant the user's questions is re-parented when scoping next runs.
    sharpen = ' '.join((ROOT / '.agents/skills/awb-scope/SKILL.md').read_text(encoding='utf-8').split())
    assert ("A root the user did not ask, which an older ledger may hold, takes as parent the user's "
            "question it serves, recorded first as a root from the brief when the ledger lacks it.") in sharpen


def test_guide_commit_points_follow_the_commits_line():
    # The README promises at most one commit reminder a session under `on request`, and commits
    # as the work goes under `as I go`; the rerun and publish points keep to both.
    guides = ROOT / '.agents/skills/awb-init/assets/workbench/workbench-guides'
    analysis = ' '.join((guides / 'analysis.md').read_text(encoding='utf-8').split())
    assert ("Before rerunning a supported or flagged finding, commit its evidence when README's `Commits:` "
            "line says `as I go`; otherwise suggest committing it, unless you already suggested a commit "
            "this session.") in analysis
    data = ' '.join((guides / 'data.md').read_text(encoding='utf-8').split())
    assert ("commit these first when README's `Commits:` line says `as I go`; otherwise suggest committing "
            "them, unless you already suggested a commit this session.") in data
    assert 'Suggest committing these first' not in data
    # A kept reference document follows the same line.
    assert ("under `foundation/references/<source-id>/`; commit it when README's `Commits:` line says "
            "`as I go`, otherwise suggest committing it, unless you already suggested a commit this session.") in data
    assert 'and suggest committing it.' not in data


def test_exploration_asks_the_users_questions_in_its_report():
    report = ' '.join(section((ROOT / '.agents/skills/awb-explore/SKILL.md').read_text(encoding='utf-8'),
                              '## 6. Report').split())
    assert 'the ledger questions added, asking in the report each one the user can settle' in report


def test_brainstorm_asks_the_users_questions_in_its_report():
    # A kept question the user can settle is asked, never sent to another skill; only a
    # stakeholder's question and a scope change go through `awb-scope`.
    report = ' '.join(section((ROOT / '.agents/skills/awb-brainstorm/SKILL.md').read_text(encoding='utf-8'),
                              '## 4. Report').split())
    assert 'questions for the user or a stakeholder through `awb-scope`' not in report
    assert 'asking in the report each kept question the user can settle' in report
    assert "a stakeholder's question through `awb-scope`" in report


def test_status_reports_git_unavailable_with_its_impact():
    status = ' '.join((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').split())
    assert 'When `git.available` is false, report its `reason`. ' not in status
    assert ('When `git.available` is false, report its `reason` with what it means for the user: status '
            'cannot tell what is uncommitted or whether the state is out of date, and evidence records '
            'file checksums instead of a commit SHA; say whether they must act, such as by installing Git '
            'or putting the project in a repository.') in status


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


README = ROOT / 'README.md'


def markdown_links(text):
    """Accepted input: LF Markdown whose links are all inline, `[label](target)`: the
    target is one or more characters other than whitespace, `(`, `)`, `<`, and `>`,
    closed by `)`. Returns every target in order, anchors included. Refuse with
    ValueError a `](` whose target does not fit, such as one holding a space, a title,
    angle brackets, or parentheses, or never closed; any `]:`, which every reference
    definition holds wherever its target sits; any `][`, a full or collapsed
    reference; an autolink, `<` then a scheme and `:`; and any `href=` or `src=`, by
    which raw HTML names a target. Known limits: code spans and fences are read like
    prose, so a `](` written in code must fit too, as scripts/build-dist.sh's own
    check reads it; labels are not checked; GitHub's bare `https://` and `www.` links
    are not returned, since they never name a repository file.
    """
    if ']:' in text:
        raise ValueError('reference definitions are outside the link grammar')
    if '][' in text:
        raise ValueError('reference links are outside the link grammar')
    if re.search(r'<[A-Za-z][A-Za-z0-9+.-]+:', text):
        raise ValueError('autolinks are outside the link grammar')
    if re.search(r'\b(?:href|src)\s*=', text, re.I):
        raise ValueError('HTML links are outside the link grammar')
    targets = []
    for match in re.finditer(r'\]\(', text):
        target = re.match(r'[^\s()<>]+\)', text[match.end():])
        if not target:
            raise ValueError(f'link target outside the grammar: {text[match.start():match.start() + 40]!r}')
        targets.append(target[0][:-1])
    return targets


@pytest.mark.parametrize(('text', 'expected'), [
    ('See [a](b.md) and [`c`](https://x.y/z#q).\n', ['b.md', 'https://x.y/z#q']),
    ('[a](docs/x.md#3-y)\n[b](#what-you-get)\n', ['docs/x.md#3-y', '#what-you-get']),
    ('No links, [brackets] or (parentheses) here.\n', []),
    ('Replace `<host>` in [a](b.md): `x[1]`.\n', ['b.md']),
    ('[a](b c.md)\n', None),
    ('[a](b.md "Title")\n', None),
    ('[a](<b.md>)\n', None),
    ('[a](b(c).md)\n', None),
    ('[a]()\n', None),
    ('[a](b.md\n', None),
    ('[a]: b.md\n', None),
    ('[a]:b.md\n[x][a]\n', None),
    ('[a]:\nb.md\n', None),
    ('- [a]: b.md\n', None),
    ('See [x][a] and [y][].\n', None),
    ('See <https://x.y>.\n', None),
    ('Write to <mailto:a@b.c>.\n', None),
    ('<a href="docs/x.md">x</a>\n', None),
    ('<img src="docs/x.png">\n', None),
])
def test_markdown_links_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            markdown_links(text)
    else:
        assert markdown_links(text) == expected


def heading_anchors(text):
    """Accepted input: LF Markdown. Returns the anchor GitHub gives each ATX heading
    outside fences, a line of one to six `#` at column 0, a space, and text: the text
    without a closing run of `#` after a space, stripped and lowercased, each
    character other than an ASCII letter, digit, space, hyphen, or underscore dropped,
    then each space made a hyphen. A fence opens at a line of three or more backticks
    or tildes after zero to three spaces, and closes at the next such line of the
    same character, at least as long, after zero to three spaces, with nothing after
    it; a fence-like line indented four or more spaces inside a fence is its content.
    Refuse with ValueError, outside fences: any other line of one to six `#` then a
    space, a tab, or nothing, such as an indented heading or one with no text; a line
    starting `<` that is not a whole one-line HTML comment; a backtick fence line
    whose info text holds a backtick, which is a code span; and a fence-like line
    indented four or more spaces, which an indented code block or a nested list item
    holds. Refuse a heading holding a character outside
    printable ASCII, `*`, `[`, `<`, an entity such as `&amp;`, or a `_` not between
    two letters or digits, since the rule above is GitHub's for plain ASCII text and
    these render as other text. Known limits: a repeated heading's `-1` suffix and Setext
    headings are not produced, and a heading inside a blockquote gives no anchor, so a
    link to one fails; a fence in a list item closed by a line indented four or more
    spaces stays open and hides the headings after it, so a link to one fails.
    """
    anchors, fence = set(), None
    for line in text.split('\n'):
        fence_line = re.match(r'( *)(`{3,}|~{3,})(.*)$', line)
        if fence_line:
            indent, run, info = fence_line.groups()
        if fence:
            if (fence_line and len(indent) <= 3 and run[0] == fence[0] and len(run) >= len(fence)
                    and not info.strip()):
                fence = None
            continue
        if fence_line:
            if len(indent) > 3:
                raise ValueError(f'fence indented four or more spaces: {line!r}')
            if run[0] == '`' and '`' in info:
                raise ValueError(f'code span, not a fence: {line!r}')
            fence = run
            continue
        if re.match(r' *<', line) and not re.fullmatch(r'<!--.*-->', line):
            raise ValueError(f'raw HTML line: {line!r}')
        if not re.match(r' *#{1,6}(?:[ \t]|$)', line):
            continue
        match = re.fullmatch(r'#{1,6} (.*)', line)
        heading = re.sub(r'(?:^|[ \t])#+[ \t]*$', '', match[1]).strip() if match else ''
        if not heading:
            raise ValueError(f'heading outside the grammar: {line!r}')
        if not all(' ' <= character <= '~' for character in heading):
            raise ValueError(f'heading outside printable ASCII: {heading!r}')
        if re.search(r'[*\[<]|&#?\w+;|(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])', heading):
            raise ValueError(f'heading markup outside the grammar: {heading!r}')
        anchors.add(re.sub(r'[^a-z0-9 _-]', '', heading.lower()).replace(' ', '-'))
    return anchors


@pytest.mark.parametrize(('text', 'expected'), [
    ('# Title\n## What you get\n', {'title', 'what-you-get'}),
    ('## 3. Server configuration\n', {'3-server-configuration'}),
    ('### Project instructions in `AGENTS.md`\n', {'project-instructions-in-agentsmd'}),
    ('## Install and administer\n```sh\n# a comment\n```\n', {'install-and-administer'}),
    ('#hashtag\n####### seven\n', set()),
    ('## Title ##\n## C# and snake_case\n', {'title', 'c-and-snake_case'}),
    ('## A & B\n', {'a--b'}),
    ('~~~\n# not a heading\n~~~\n', set()),
    ('````md\n```\n# inside\n````\n## After\n', {'after'}),
    ('- item\n  ```sh\n  # comment\n  ```\n', set()),
    ('```md\n    ```\n# x\n```\n', set()),
    ('<!-- dist:exclude -->\n## A\n', {'a'}),
    ('## Café\n', None),
    ('## A — B\n', None),
    ('## **Bold** _it_\n', None),
    ('## __init__\n', None),
    ('## See [x](y.md)\n', None),
    ('## A <kbd>B</kbd>\n', None),
    ('## A &amp; B\n', None),
    ('   ## Indented\n', None),
    ('#\tTab\n', None),
    ('## ##\n', None),
    ('<details>\n# x\n</details>\n', None),
    ('<!--\n# x\n-->\n', None),
    ('```a`b\n# x\n', None),
    ('    ```\n# x\n    ```\n', None),
])
def test_heading_anchors_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            heading_anchors(text)
    else:
        assert heading_anchors(text) == expected


DIST_OPEN, DIST_CLOSE = '<!-- dist:exclude -->', '<!-- /dist:exclude -->'


def archive_readme(text):
    """Accepted input: LF Markdown in which every `dist:exclude` marker is a whole
    line, DIST_OPEN or DIST_CLOSE, alternating from DIST_OPEN and ending on
    DIST_CLOSE. Returns the README scripts/build-dist.sh writes into the archive: each
    block from DIST_OPEN through DIST_CLOSE dropped, and every `](.agents/skills/`
    made `](`. Refuse with ValueError a marker inside a line of other text, two
    DIST_OPEN or two DIST_CLOSE lines in a row, a DIST_CLOSE first, and a DIST_OPEN
    never closed, which build-dist.sh would drop to the end of the file. Known limits:
    the script's squeezing of repeated blank lines is left out, since it changes no
    link.
    """
    kept, inside = [], False
    for line in text.split('\n'):
        if line in (DIST_OPEN, DIST_CLOSE):
            if (line == DIST_OPEN) == inside:
                raise ValueError(f'unbalanced marker: {line!r}')
            inside = line == DIST_OPEN
        elif 'dist:exclude' in line:
            raise ValueError(f'marker inside a line: {line!r}')
        elif not inside:
            kept.append(line)
    if inside:
        raise ValueError('an exclude block is never closed')
    return '\n'.join(kept).replace('](.agents/skills/', '](')


@pytest.mark.parametrize(('text', 'expected'), [
    (f'a\n{DIST_OPEN}\nb\n{DIST_CLOSE}\nc\n', 'a\nc\n'),
    ('[x](.agents/skills/awb-init/SKILL.md)\n', '[x](awb-init/SKILL.md)\n'),
    (f'a\n{DIST_CLOSE}\n', None),
    (f'{DIST_OPEN}\n{DIST_OPEN}\n{DIST_CLOSE}\n', None),
    (f'{DIST_OPEN}\nb\n{DIST_CLOSE}\n{DIST_CLOSE}\n', None),
    (f'{DIST_OPEN}\nb\n', None),
    (f'text {DIST_OPEN}\n', None),
    (f' {DIST_OPEN}\nb\n{DIST_CLOSE}\n', None),
])
def test_archive_readme_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            archive_readme(text)
    else:
        assert archive_readme(text) == expected


def unresolved_links(text, source):
    """Each relative link in text whose path `source` maps to no file, or whose anchor
    names no heading there; `source` maps a link path to the linked file's text or
    None, and a bare `#anchor` is read against text itself."""
    unresolved = []
    for target in markdown_links(text):
        if re.match(r'https?://', target):
            continue
        path, _, anchor = target.partition('#')
        linked = source(path) if path else text
        if linked is None or anchor and anchor not in heading_anchors(linked):
            unresolved.append(target)
    return unresolved


def tracked_files():
    listed = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True)
    return set(listed.stdout.decode('utf-8').split('\0')) - {''}


def repository_source(tracked):
    # A link resolves on GitHub only to a tracked file inside the repository: an absolute path, a path out
    # of the repository, and an untracked local file name nothing there.
    def source(path):
        path = posixpath.normpath(path)
        return (ROOT / path).read_text(encoding='utf-8') if path in tracked else None
    return source


# scripts/build-dist.sh's archive holds the skill folders at its top level, beside these files.
ARCHIVE_FILES = ('CHANGELOG.md', 'LICENSE', 'README.md')


def archive_source(archive, tracked):
    # The archive's README.md is the archive copy, so its anchors are read there, not in the repository's.
    # The script copies only tracked files, and its allowlist names every skill folder.
    def source(path):
        if path == 'README.md':
            return archive
        if path in ARCHIVE_FILES:
            return (ROOT / path).read_text(encoding='utf-8')
        if f'.agents/skills/{path}' in tracked:
            return (ROOT / '.agents/skills' / path).read_text(encoding='utf-8')
        return None
    return source


def test_readme_links_resolve():
    # Every relative link in the repository README names a tracked file, and every anchor a heading in it.
    text = README.read_text(encoding='utf-8')
    assert unresolved_links(text, repository_source(tracked_files())) == []


def test_archive_readme_links_only_what_the_archive_holds():
    # build-dist.sh drops the dist:exclude blocks, rewrites skill links, and refuses a docs/ link or a stray
    # marker in what is left; every link left must name a file the archive holds.
    archive = archive_readme(README.read_text(encoding='utf-8'))
    assert '](docs/' not in archive
    assert unresolved_links(archive, archive_source(archive, tracked_files())) == []


def test_unresolved_links_refuse_what_github_and_the_archive_do_not_hold():
    tracked = tracked_files()
    repository = repository_source(tracked)
    outside = f'../{ROOT.name}/README.md'
    with tempfile.NamedTemporaryFile(dir=ROOT, suffix='.md') as untracked:
        name = Path(untracked.name).name
        text = f'[a](/etc/hosts)\n[b]({outside})\n[c]({name})\n[d](README.md)\n[e](./LICENSE)\n'
        assert unresolved_links(text, repository) == ['/etc/hosts', outside, name]
    readme = README.read_text(encoding='utf-8')
    archive = archive_readme(readme)
    dropped = sorted(heading_anchors(readme) - heading_anchors(archive))
    assert dropped, 'the archive copy drops no heading'
    text = archive + f'[x](README.md#{dropped[0]})\n[y](#{dropped[0]})\n[z](README.md#what-you-get)\n'
    assert unresolved_links(text, archive_source(archive, tracked)) == [f'README.md#{dropped[0]}', f'#{dropped[0]}']


def test_readme_opens_with_what_you_get_and_the_analyst_quick_start():
    # The analyst's page comes first; install and host setup sit in one section below it.
    text = README.read_text(encoding='utf-8')
    headings = re.findall(r'^## (.+)$', text, re.M)
    assert headings[:2] == ['What you get', 'Quick-start for analysts']
    assert headings.index('Install and administer') > headings.index('Quick-start for analysts')
    admin = section(text, '## Install and administer').split('\n')
    for heading in ('### Requirements', '### Install', '#### Shared skills', '#### MCP server',
                    '#### VS Code Local and package reviewer', '#### Project instructions in AGENTS.md'):
        assert heading in admin


def test_readme_says_what_the_analyst_gets_and_is_asked():
    text = README.read_text(encoding='utf-8')
    what = ' '.join(section(text, '## What you get').split())
    for name in ('findings.md', 'charts/', 'methodology-note.md', 'methodology.md', 'deck-rules.md',
                 'assembly/m365.md', 'START-HERE.md'):
        assert f'`{name}`' in what, name
    # Users expected slides: the package is the deck's sources, and Copilot is one builder of several.
    assert 'not a .pptx' in what
    assert 'by hand' in what and 'only for the Copilot route' in what
    quick = ' '.join(section(text, '## Quick-start for analysts').split())
    assert 'Python 3.10 or later' in quick
    for term in ('Canonical view', 'Question ledger', 'Receipt', 'Disposition', 'Review rule'):
        assert f'**{term}**' in quick, term
    assert 'asked for a disposition only when a finding the draft shows is flagged' in quick
    for mode in ('preview-and-wait', 'draft-then-review'):
        assert mode in quick
    # The requests come in the order an investigation usually takes them.
    requests = ['Use awb-init', 'Use awb-scope', 'Use awb-clean', 'Use awb-explore', 'Use awb-status',
                'Use awb-package', 'Use awb-release']
    positions = [quick.find(request) for request in requests]
    assert -1 not in positions and positions == sorted(positions), dict(zip(requests, positions))
    assert 'awb-brainstorm' in quick
    # The exchange count is a range from the recorded runs, not a promise.
    assert '6 to 11' in quick
    # The package check passes a number listed with its reason, so the limits say so.
    assert 'traces to a recorded result or is listed, with its reason' in quick
    # The builder gets only what START-HERE.md lists; datasets and the methods note are not attached.
    how = ' '.join(section(text, '## How it works').split())
    assert 'chosen exports' not in how and 'travel beside the deck and are not attached' in how


def test_commands_state_the_cli_fallback_scripts_by_path_and_the_interpreter():
    commands = ' '.join(section(AGENTS.read_text(encoding='utf-8'), '## Commands').split())
    # A refused or missing write tool falls back to the command line, said once; working tools stay first.
    assert ('If a write tool is refused or unavailable, run its CLI command, '
            'keep using the tools that work, and say so once.') in commands
    # The scan and record scripts live in their skill folders and are never awb.py subcommands.
    assert 'Skill scripts run by path, never as `awb.py` commands.' in commands
    # One interpreter, recorded once: the installer writes the README line the commands mean.
    assert "In every workbench command, `python3` means README's `Project interpreter`." in commands
    readme = (ROOT / '.agents/skills/awb-init/assets/workbench/README.md').read_text(encoding='utf-8')
    assert re.search(r'^Project interpreter: not yet recorded$', readme, re.M)
    for skill in ('awb-clean', 'awb-explore', 'awb-package'):
        text = ' '.join((ROOT / f'.agents/skills/{skill}/SKILL.md').read_text(encoding='utf-8').split())
        assert "README's `Project interpreter`" in text, skill


def test_no_code_history_means_no_commits_or_suggestions():
    readme = (ROOT / '.agents/skills/awb-init/assets/workbench/README.md').read_text(encoding='utf-8')
    assert re.search(r'^Code history: Git$', readme, re.M)
    agents = ' '.join(AGENTS.read_text(encoding='utf-8').split())
    assert "While README's `Code history:` line says `none`, make and suggest no commits." in agents
    analysis = ' '.join((ROOT / '.agents/skills/awb-init/assets/workbench/workbench-guides/analysis.md')
                        .read_text(encoding='utf-8').split())
    assert "While README's `Code history:` line says `none`, do neither." in analysis
    # The guide and skill that suggest a commit at a step say so too, where the step is read.
    data = ' '.join((ROOT / '.agents/skills/awb-init/assets/workbench/workbench-guides/data.md')
                    .read_text(encoding='utf-8').split())
    # Both the reference-document and the publication commit points say so where the step is read.
    assert data.count("While README's `Code history:` line says `none`, do neither.") == 2
    clean = ' '.join((ROOT / '.agents/skills/awb-clean/SKILL.md').read_text(encoding='utf-8').split())
    assert ("Commit `foundation/quality.json` together with `foundation/quality.md` when you commit as README's "
            "`Commits:` line allows, never while its `Code history:` line says `none`") in clean
    init = ' '.join(section((ROOT / '.agents/skills/awb-init/SKILL.md').read_text(encoding='utf-8'),
                            '## 1. Resolve the target').split())
    assert '`Code history: none (<reason>)`' in init
    # A project that later gains a repository goes back to Git, at a rerun or a repair.
    assert 'set the line back to `Code history: Git`' in init
    repair = ' '.join((ROOT / '.agents/skills/awb-init/references/repair.md').read_text(encoding='utf-8').split())
    assert "set it back to `Code history: Git`" in repair


def ledger_ids(text):
    """Accepted input: any text. Returns each ledger-style ID, `Q-` and one or more digits,
    in order; a `Q-` preceded by a letter, a digit, or `-` (as in `DQ-004`) is part of another
    word and refused, as is `Q-` without a digit. Known limits: a plain substring scan, so an
    ID inside a URL or code is found too."""
    return re.findall(r'(?<![A-Za-z0-9-])Q-\d+', text)


@pytest.mark.parametrize(('text', 'expected'), [
    ('Use {Q-004} or Q-12.', ['Q-004', 'Q-12']),
    ('`Q-007` beside plain text', ['Q-007']),
    ('such as DQ-004', []),
    ('x-Q-004 and AQ-1', []),
    ('Q- and Q-ID', []),
])
def test_ledger_id_scanner_accepted_and_refused_forms(text, expected):
    assert ledger_ids(text) == expected


def test_quality_ids_in_shipped_help_are_dq_never_ledger_ids():
    # Ledger questions are Q-NNN; quality IDs are DQ-NNN, so no cleaning help names a quality ID like Q-004.
    import subprocess
    import sys
    scripts = ROOT / '.agents/skills/awb-clean/scripts'
    texts = {name: subprocess.run([sys.executable, str(scripts / name), '--help'], capture_output=True,
                                  text=True, check=True).stdout
             for name in ('record_cleaning.py', 'scan_dataset.py')}
    for path in [ROOT / '.agents/skills/awb-clean/SKILL.md', *sorted((ROOT / '.agents/skills/awb-clean/references').glob('*.md')),
                 ROOT / '.agents/skills/awb-init/assets/workbench/foundation/quality.md']:
        texts[str(path.relative_to(ROOT))] = path.read_text(encoding='utf-8')
    assert {name: ledger_ids(text) for name, text in texts.items() if ledger_ids(text)} == {}
    assert 'DQ-004' in texts['record_cleaning.py'] and 'DQ-004' in texts['.agents/skills/awb-clean/SKILL.md']
    assert 'DQ-NNN' in texts['.agents/skills/awb-init/assets/workbench/foundation/quality.md']
