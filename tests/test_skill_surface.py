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
    angle brackets, or parentheses, or never closed; a reference definition, a line
    starting `[label]: `; and an autolink, `<` then `http`. Known limits: code spans
    and fences are read like prose, so a `](` written in code must fit too, as
    scripts/build-dist.sh's own check reads it; labels are not checked.
    """
    if any(re.match(r'\s*\[[^\]]+\]:\s', line) for line in text.split('\n')):
        raise ValueError('reference definitions are outside the link grammar')
    if re.search(r'<https?:', text):
        raise ValueError('autolinks are outside the link grammar')
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
    ('[a](b c.md)\n', None),
    ('[a](b.md "Title")\n', None),
    ('[a](<b.md>)\n', None),
    ('[a](b(c).md)\n', None),
    ('[a]()\n', None),
    ('[a](b.md\n', None),
    ('[a]: b.md\n', None),
    ('See <https://x.y>.\n', None),
])
def test_markdown_links_accepted_and_refused_forms(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            markdown_links(text)
    else:
        assert markdown_links(text) == expected


def heading_anchors(text):
    """Accepted input: LF Markdown. Returns the anchor GitHub gives each ATX heading
    (one to six `#` at column 0, a space, text) outside ``` fences: the text stripped
    and lowercased, each character other than an ASCII letter, digit, space, hyphen,
    or underscore dropped, then each space made a hyphen. Refuse with ValueError a
    heading holding a character outside printable ASCII, since this is GitHub's rule
    for ASCII text only. Known limits: a repeated heading's `-1` suffix and Setext
    headings are not produced.
    """
    anchors, fenced = set(), False
    for line in text.split('\n'):
        if line.startswith('```'):
            fenced = not fenced
            continue
        match = None if fenced else re.match(r'#{1,6} (.+)$', line)
        if match:
            heading = match[1].strip()
            if not all(' ' <= character <= '~' for character in heading):
                raise ValueError(f'heading outside printable ASCII: {heading!r}')
            anchors.add(re.sub(r'[^a-z0-9 _-]', '', heading.lower()).replace(' ', '-'))
    return anchors


@pytest.mark.parametrize(('text', 'expected'), [
    ('# Title\n## What you get\n', {'title', 'what-you-get'}),
    ('## 3. Server configuration\n', {'3-server-configuration'}),
    ('### Project instructions in `AGENTS.md`\n', {'project-instructions-in-agentsmd'}),
    ('## Install and administer\n```sh\n# a comment\n```\n', {'install-and-administer'}),
    ('#hashtag\n####### seven\n', set()),
    ('## Café\n', None),
    ('## A — B\n', None),
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
    """Each relative link in text whose file `source` maps to nothing, or whose
    anchor names no heading there; `source` maps a link path to a file or None."""
    unresolved = []
    for target in markdown_links(text):
        if re.match(r'https?://', target):
            continue
        path, _, anchor = target.partition('#')
        file = source(path)
        if file is None or not file.is_file():
            unresolved.append(target)
        elif anchor and anchor not in heading_anchors(text if not path else file.read_text(encoding='utf-8')):
            unresolved.append(target)
    return unresolved


def test_readme_links_resolve():
    # Every relative link in the repository README names a file that exists, and every anchor a heading in it.
    text = README.read_text(encoding='utf-8')
    assert unresolved_links(text, lambda path: ROOT / path if path else README) == []


# scripts/build-dist.sh's archive holds the skill folders at its top level, beside these files.
ARCHIVE_FILES = ('CHANGELOG.md', 'LICENSE', 'README.md')


def test_archive_readme_links_only_what_the_archive_holds():
    # build-dist.sh drops the dist:exclude blocks, rewrites skill links, and refuses a docs/ link or a stray
    # marker in what is left; every link left must name a file the archive holds.
    archive = archive_readme(README.read_text(encoding='utf-8'))
    assert '](docs/' not in archive

    def source(path):
        if not path or path in ARCHIVE_FILES:
            return ROOT / (path or 'README.md')
        if (ROOT / '.agents/skills' / path.split('/')[0] / 'SKILL.md').is_file():
            return ROOT / '.agents/skills' / path
        return None

    assert unresolved_links(archive, source) == []


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
