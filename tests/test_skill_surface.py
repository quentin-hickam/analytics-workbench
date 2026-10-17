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
    assert '**preview-and-wait**' in package and '**draft-then-review**' in package
    assert precedence in ' '.join(package.split())
    # The skill states the modes once; the contract points to it rather than repeating them.
    assert precedence not in ' '.join(contract.split()) and "`awb-package`'s **The headline checkpoint**" in contract
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


def test_headline_checkpoint_states_the_word_limit_and_asks_before_trimming():
    # The limit was once written only for the agent, which trimmed approved headlines and said so afterwards.
    checkpoint = skill_section('.agents/skills/awb-package/SKILL.md', '### The headline checkpoint')
    assert 'a headline holds at most 15 words' in checkpoint
    assert 'Before trimming a headline the user wrote or approved, ask' in checkpoint
    assert '`accepted_long_headlines`' in checkpoint
    # The check step is where draft-then-review meets a long headline first, before the user sees the headlines.
    check = skill_section('.agents/skills/awb-package/SKILL.md', '## 6. Check')
    assert 'a long-headline `warning` row is asked about as the headline checkpoint says, never trimmed unasked' in check


def test_package_records_and_previews_audience_number_formats_and_prose_approximations():
    brief = (ROOT / '.agents/skills/awb-init/assets/workbench/investigation/brief.md').read_text()
    assert "Once the audience is named, always record precision and clock format: the user's choices, otherwise audience defaults." in brief
    assert ('Unless the audience is recorded as technical, use whole numbers for large values, or one decimal '
            'with a scale word (8.6 billion), one decimal '
            "for shares and rates, and the audience's usual clock format.") in brief
    assert 'when the user states them' not in brief
    package = (ROOT / '.agents/skills/awb-package/SKILL.md').read_text()
    establish = skill_section('.agents/skills/awb-package/SKILL.md', '## 1. Establish')
    assert ("Record precision and clock format, using the [brief template](../awb-init/assets/workbench/investigation/"
            "brief.md)'s audience defaults when unspecified") in establish
    checkpoint = skill_section('.agents/skills/awb-package/SKILL.md', '### The headline checkpoint')
    assert "With the headlines" in checkpoint and "state the brief's precision and clock format" in checkpoint
    helpers = (ROOT / '.agents/skills/awb-package/references/helpers.md').read_text()
    for text in (package, helpers):
        assert "the places the brief's precision gives" in text
        assert "the places the slide's number format shows" not in text
        assert 'files = false' in text
    assert 'prose-only divisors as `prose_scale`' in helpers
    check = skill_section('.agents/skills/awb-package/SKILL.md', '## 6. Check')
    assert 'use a scale word: "22.5 thousand" traces to 22,523' in check
    assert 'It is computed from results that none records: only separately authorized analysis records it' in check
    template = (ROOT / '.agents/skills/awb-package/assets/package-format/findings-template.md').read_text()
    assert ("where rounded start and end values do not subtract to the shown change, the slide's **Notes:** "
            'say changes were computed before rounding') in template


def test_release_asks_the_user_to_confirm_helper_drift():
    release = skill_section('.agents/skills/awb-release/SKILL.md', '## 3. Release')
    assert '`helper_drift`' in release and 'ask the user' in release and '`helper_drift_confirmed`' in release
    # A recorded confirmation is not asked again, and a declined change is put back by the path that restores it:
    # repair skips a missing package format, and the installer refuses an unreadable receipt.
    assert 'For each row whose `confirmed` is false' in release
    assert "a `missing` package format with the installer command in awb-package's **1. Establish**" in release
    assert '`.awb-receipt.json` from Git' in release
    helpers = (ROOT / '.agents/skills/awb-package/references/helpers.md').read_text(encoding='utf-8')
    opening = ' '.join(helpers.split('\n\n', 2)[1].split())
    assert 'change one only after the user says yes to the change, asked in plain words' in opening
    manifest = (ROOT / '.agents/skills/awb-package/assets/package-format/manifest-template.md').read_text(encoding='utf-8')
    assert '`accepted_long_headlines`' in manifest and '`helper_drift_confirmed`' in manifest


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


def test_status_scopes_read_only_to_its_report():
    # "Stay read-only" with no scope deferred the edits a user sent with "where are we?".
    status = ' '.join((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').split())
    assert 'Stay *read-only*' not in status
    assert ("The status report is *read-only*: report what the records say, and turn every fix it finds into a "
            "next request. Carry out the message's other requests, such as edits, through their own skills after "
            "the report.") in status


def test_status_offers_a_headline_preview_for_provisional_findings():
    # With every finding provisional, only brainstorming and a commit applied, and the agent improvised the preview.
    rows = [line for line in (ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').splitlines()
            if line.startswith('| ')]
    preview = rows.index('| Provisional findings and no draft | "Preview the slide headlines" | `awb-package` | progress |')
    assert rows[preview + 1].startswith('| Supported findings and no draft | "Prepare a draft package"')
    # Who promotes a finding, and when, is said where its status is defined.
    template = ' '.join((ROOT / '.agents/skills/awb-init/assets/workbench/investigation/state.md')
                        .read_text(encoding='utf-8').split())
    assert ("The agent promotes a provisional finding to supported with `python3 src/awb.py state finding` once its "
            "checks are understood and recorded and the user has approved its headline or text, such as at awb-package's "
            "slide headline preview") in template
    assert "to be promoted again once the user approves its text as rerun" in template
    # The skill that shows the headlines carries the promotion, which a bounded revision may not read in the template.
    package = ' '.join((ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8').split())
    assert ("Promote each provisional finding behind an approved headline with "
            "`python3 src/awb.py state finding <result-id> --status supported --reason \"<why>\"`.") in package


def test_status_reports_findings_by_question_every_caveat_and_plain_freshness():
    status = ' '.join(section((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8'),
                              '## Report').split())
    # Findings are counted against the user's questions, by text, and a root the agent added is labelled.
    assert ('then each `questions.by_question` entry, one of the user\'s questions, by its text with its findings by '
            'status, as "Which zones grew fastest: 2 findings, 1 supported"') in status
    assert 'labelling one whose `origin` is `brainstorm`, `eda`, or `analysis`' in status
    # Every caveat, not only flagged findings', as awb-release lists open caveats.
    assert 'every flagged finding in `active.findings`' not in status
    assert 'Then every `active.caveats` entry, flagged findings first; while one remains, never say nothing is open.' in status
    # A freshness order the records cannot settle is said plainly beside the evidence check.
    assert 'indeterminate' not in status
    assert ('run `read` command `stale` for the investigation (`python3 <project-root>/src/awb.py stale '
            '--investigation <name>`) and give the status in plain words beside how many checked results it finds '
            'current, as "saved the same day as the latest change; evidence checks show 11 of 11 current"') in status


# awb-package/SKILL.md's length after #90 shortened it, rounded up to the next 100 words. Trim the file rather
# than raise this when a change pushes it over.
PACKAGE_SKILL_WORDS = 2500


def test_package_skill_stays_under_its_word_budget():
    text = (ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8')
    assert len(text.split()) <= PACKAGE_SKILL_WORDS


def test_package_steps_export_before_filling_names_and_keep_the_preview_out_of_the_package():
    package = (ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8')
    sequence = ' '.join(package[package.index('## Sequence'):package.index('## 1. Establish')].split())
    # Writing is a first pass; export comes next and creates the folder; names, then methodology lines, after it.
    assert '**Write** a first pass of `findings.md`' in sequence
    assert 'which creates the draft folder; then fill in the display names and paste the `methodology_lines`' in sequence
    export = skill_section('.agents/skills/awb-package/SKILL.md', '## 4. Export the files and provenance')
    assert export.index('`display_stub`') < export.index('`methodology_lines`')
    assert 'Before writing, give each column' not in package
    # The evidence-restoring procedure lives in the smaller reference; the step points to it.
    assert ('**Missing evidence** in [numbers and evidence](references/numbers-and-evidence.md#missing-evidence)'
            in export and 'restore them after each' not in export)
    evidence = (ROOT / '.agents/skills/awb-package/references/numbers-and-evidence.md').read_text(encoding='utf-8')
    assert '\n## Missing evidence\n' in evidence and 'restore them after each' in ' '.join(evidence.split())
    # Step 4 is numbered sub-steps, not one paragraph.
    assert re.search(r'\n1\. Run `python3 src/awb.py export', package) and '\n5. When `export` reports' in package
    checkpoint = skill_section('.agents/skills/awb-package/SKILL.md', '### The headline checkpoint')
    assert '`.preview/headlines.md` in the draft folder, which no check reads and no release copies' in checkpoint
    assert 'takes `--show`, leaving its priority' in checkpoint
    # The report repeats the package name; scoping names the folder; release gives the full storage path.
    assert 'the package name, the draft path' in skill_section('.agents/skills/awb-package/SKILL.md', '## 7. Report')
    assert '`investigations/<slug>/`' in skill_section('.agents/skills/awb-scope/SKILL.md', '## 4. Report')
    assert 'the full `path`' in skill_section('.agents/skills/awb-release/SKILL.md', '## 5. Copy to storage')


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
    assert 'Name what a comparison leaves uncontrolled when a decision rests on it' in invariants


def test_chat_claim_rules_sit_where_chat_is_written():
    # An untested explanation stated as an answer, and a share whose base changed between replies,
    # reached chat while the rule sat among the analytical invariants; it moved, not duplicated.
    text = AGENTS.read_text(encoding='utf-8')
    conversation = ' '.join(section(text, '## Conversation').split())
    assert 'Offer an untested cause, label, or recollection as a question' in conversation
    assert '("timing errors?", not "timing errors")' in conversation
    assert "record recollections as the user's" in conversation
    assert text.count('recollections') == 1 and text.count('recollection as a question') == 1
    assert 'recalls' not in text
    assert "Name codes by meaning, and every share's base and when it changes." in conversation
    assert 'untested' not in ' '.join(section(text, '## Analytical invariants').split())
    # IDs stay in the records: no allowance for one beside plain text in chat.
    assert 'Records keep precise terms and IDs; chat uses plain words' in conversation
    assert 'may sit beside plain text' not in conversation
    # The headline checkpoint repeats the explanation rule and shows the figures chat has not.
    checkpoint = ' '.join(section((ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8'),
                                  '### The headline checkpoint').split())
    assert 'Headlines claim only what results show: no untested cause or label, no exception dropped.' in checkpoint
    assert 'show them with the figures behind each headline that chat has not shown' in checkpoint
    # A duplicate row is a repeat to explain, its treatment proposed without a cause asserted.
    clean = ' '.join((ROOT / '.agents/skills/awb-clean/SKILL.md').read_text(encoding='utf-8').split())
    assert 'landed twice' not in clean
    assert 'Both duplicate issues are repeats to explain, not known copies: propose their treatment without ' \
           'asserting why they repeat.' in clean


def test_cross_part_copies_need_the_user_or_source_to_call_them_reextracts():
    clean = (ROOT / '.agents/skills/awb-clean/SKILL.md').read_text(encoding='utf-8')
    decide = ' '.join(section(clean, '## 2. Decide').split())
    assert 'such as overlapping periods' not in clean
    assert 'known to be re-extracts' not in clean
    assert "when the user or source documentation says the parts are re-extracts" in decide
    assert ("an overlap you observe, or what you already know of a dataset, is not the source saying so") in decide
    assert "When `duplicate-rows:across-parts` spans more than two parts, count each pair's shared rows" in decide
    assert "compare the counts with the issue's" not in decide
    assert 'under a recorded grain with no lineage column in it (repeats then share one grain key)' in decide
    assert "The user decides everything else" in decide
    checks = (ROOT / '.agents/skills/awb-clean/references/checks.md').read_text(encoding='utf-8')
    assert checks.count('first lineage column') == 1
    assert 'counts rows outside each repeated group\'s minimum part' in checks
    assert 'counts repeats beyond one in that part, or all repeats without lineage' in checks
    landing = (ROOT / '.agents/skills/awb-init/references/landing.md').read_text(encoding='utf-8')
    assert 'part column first, such as `sheet` and `sheet_row`' in landing
    correction = (ROOT / '.agents/skills/awb-clean/references/correction-views.md').read_text(encoding='utf-8')
    assert '**Cross-part copies (`duplicate-rows:across-parts`):**' in correction
    assert '**Exact repeats (`duplicate-rows`), without lineage:**' in correction


def test_footer_counts_a_provisional_answer_as_provisional():
    # "5 answered" while chat had shown only leaders: an answer resting on unpromoted findings is provisional.
    agents = ' '.join(AGENTS.read_text(encoding='utf-8').split())
    # A flagged answer never promoted displays answered (provisional, awaiting recheck): provisional too.
    assert 'counting any `provisional` answer as provisional' in agents
    assert '1 provisional' in footer_example(AGENTS.read_text(encoding='utf-8'))
    status = ' '.join((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').split())
    assert ('Count `answered (provisional)` and `answered (provisional, awaiting recheck)`' in status
            and 'as provisional, not answered' in status)


def test_reports_use_plain_words_not_ids():
    for path in sorted((ROOT / '.agents/skills').rglob('*.md')):
        assert 'Report the new ID' not in path.read_text(encoding='utf-8'), path
    review = ' '.join((ROOT / '.agents/skills/awb-package/references/review.md').read_text(encoding='utf-8').split())
    assert 'Say in plain words what later drafts will be checked for.' in review
    report = ' '.join(section((ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8'),
                              '## 7. Report').split())
    assert 'each chart by what it shows' in report and 'with the result it serializes' not in report
    clean = ' '.join(section((ROOT / '.agents/skills/awb-clean/SKILL.md').read_text(encoding='utf-8'),
                             '## Report').split())
    assert 'the recorded issues in plain words, their quality IDs kept in the files' in clean
    status = ' '.join(section((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8'),
                              '## Report').split())
    assert "without its keys or their question and result IDs" in status
    assert "report that question's text and status" in status and 'report the ID' not in status
    assert 'list each `provisional` question by its text' in status


COMMIT_GUARDS = ('already suggested a commit this session', 'at most once a session')


def commit_suggestions(text):
    """Accepted input: Markdown prose or table rows. Returns each sentence (split after a period
    followed by whitespace) or table row that suggests a commit: `suggest`, `suggests`, `suggested`
    or `suggesting` followed in the same sentence by `commit` (any case, `uncommitted` included),
    unless `no` directly follows the verb, or that names the request "Commit the current work".
    Errs toward listing: a guard sentence such as "unless you already suggested a commit" is listed
    too, and must then carry a guard itself. Known limit: a suggestion phrased without `suggest`
    is not found.
    """
    found = []
    for line in text.split('\n'):
        for sentence in ([line] if line.lstrip().startswith('|') else re.split(r'(?<=\.)\s+', line)):
            if re.search(r'\bsuggest(?:s|ed|ing)?\b(?! no\b)[^.]*commit', sentence, re.I) \
                    or 'Commit the current work' in sentence:
                found.append(sentence)
    return found


@pytest.mark.parametrize(('text', 'expected'), [
    ('Otherwise suggest committing it, unless you already suggested a commit this session. Next.',
     ['Otherwise suggest committing it, unless you already suggested a commit this session.']),
    ('Make and suggest no commits. Suggests no commit.', []),
    ('| `x` is above zero | "Commit the current work" | request | progress |',
     ['| `x` is above zero | "Commit the current work" | request | progress |']),
    ('Suggest one at most once a session while it is uncommitted.',
     ['Suggest one at most once a session while it is uncommitted.']),
    ('A suggestion to commit. Commit when asked.', []),
])
def test_commit_suggestions_accepted_forms(text, expected):
    assert commit_suggestions(text) == expected


def test_every_commit_suggestion_is_once_a_session():
    suggestions = [(path, sentence) for path in sorted((ROOT / '.agents/skills').rglob('*.md'))
                   for sentence in commit_suggestions(path.read_text(encoding='utf-8'))]
    names = {path.relative_to(ROOT / '.agents/skills').as_posix() for path, _ in suggestions}
    # The status request, both reports, and the repair report carry the guard the guides already had.
    assert {'awb-status/SKILL.md', 'awb-package/SKILL.md', 'awb-release/SKILL.md', 'awb-init/SKILL.md',
            'awb-init/assets/workbench/AGENTS.md', 'awb-init/assets/workbench/workbench-guides/data.md',
            'awb-init/assets/workbench/workbench-guides/analysis.md'} <= names
    for path, sentence in suggestions:
        assert any(guard in sentence for guard in COMMIT_GUARDS), (path, sentence)


def test_scoping_counts_a_decision_as_one_choice():
    interview = ' '.join(section((ROOT / '.agents/skills/awb-scope/SKILL.md').read_text(encoding='utf-8'),
                                 '## 2. Interview').split())
    assert 'at most four' in interview
    assert ('A decision is one choice: never number unrelated choices under one item; '
            'make each its own decision, and ask any beyond four in a second round.') in interview


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
    assert ("ends with one plain line: any change to the user's questions, the ledger's roots, "
            "counting any `provisional` answer as provisional, and the next step") in agents
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


def test_analysis_states_the_threshold_rule_and_the_standard_checks():
    # A threshold set after seeing which rows lead, or a minimum the user never agreed, shaped answers the
    # user then rejected; reconciliation and per-entity coverage surfaced only at packaging review.
    add = ' '.join(section((ROOT / '.agents/skills/awb-init/assets/workbench/workbench-guides/analysis.md')
                           .read_text(encoding='utf-8'), '## Add a result').split())
    assert ("A threshold, minimum, or exclusion the brief does not settle is the user's decision: propose it to "
            "the user before looking at which rows lead, and say so when you propose one after seeing results.") in add
    assert "with every filtered population reconciled by `reconcile()`" in add
    assert ("For a series summed over a period, list each in-scope entity's missing periods, inside its series too, "
            'as a caveat: "unreported in <periods>; sums cover reported periods only", never zero; '
            "filling gaps by assumption gives an illustrative scenario, never a bound.") in add
    assert 'a count below the period length' not in add
    assert "Save full precision in result queries and round only for display." in add
    assert "result sessions run DuckDB on one thread" in add
    assert "the investigation's `views/*.sql`" in add and "(`import helpers` for `helpers.py`)" in add
    assert ("A result run before the project's first commit records `uncommitted` as its producing commit until it "
            "is rerun after that commit.") in add
    # The MCP route comes first; the terminal command is the fallback.
    assert ("Run results through the `awb` MCP `run` tool with the investigation and any result IDs, or with "
            "`python3 investigations/<name>/run.py [result-id ...]` when the host offers no MCP tools.") in add
    explore = ' '.join((ROOT / '.agents/skills/awb-explore/SKILL.md').read_text(encoding='utf-8').split())
    assert ("A question-specific exclusion, threshold, or minimum the brief does not settle is the user's decision: "
            "propose it before looking at which rows lead, say so when you propose one after seeing results") in explore
    assert ("list in a follow-up the periods each entity in scope lacks, mid-series too, and record them under "
            "Unresolved issues and in any quality.md row as unreported, never zero, so the finding on that sum "
            "carries the caveat") in explore
    contract = ' '.join((ROOT / '.agents/skills/awb-package/references/package-contract.md').read_text(encoding='utf-8').split())
    assert ("A validation check recorded as not assessed stays out of `findings.md` and the methodology note unless "
            "the user should act on it.") in contract
    package = ' '.join((ROOT / '.agents/skills/awb-package/SKILL.md').read_text(encoding='utf-8').split())
    assert ("When a review or the user corrects a claim a finding's text states, also reword that finding with "
            "`python3 src/awb.py state finding <id> --text \"<corrected text>\"` in the same revision") in package
    status = ' '.join((ROOT / '.agents/skills/awb-status/SKILL.md').read_text(encoding='utf-8').split())
    assert ("When `git.uncommitted_evidence` lists results, say in one plain line that they were run before the "
            "first commit, so their evidence names no commit until they are rerun.") in status


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
    # The review holds a checked or reconciliation sentence to a recorded result or check, and the contract
    # points the writer there; every review after a draft's
    # first is scoped against the helper's receipt, judging rules added or changed since in full, and a scoped
    # review that passes completes a request or a release.
    def read(path):
        return ' '.join((ROOT / '.agents/skills' / path).read_text(encoding='utf-8').split())

    review = read('awb-package/references/review.md')
    package = read('awb-package/SKILL.md')
    release = read('awb-release/SKILL.md')
    reviewer = read('awb-package/assets/awb-package-reviewer.agent.md')
    provenance = read('awb-init/references/provenance.md')
    contract = read('awb-package/references/package-contract.md')

    assert ('Every sentence asserting that something was checked or verified, reconciles, sums or adds up to, or '
            'matches cites the recorded result or check that establishes it, covering all it asserts') in contract
    assert "the contract's [Writing rules](package-contract.md#writing-rules) hold" in review
    assert 'read the cited records to confirm each check establishes all the claim asserts' in review
    assert '`awb.py state finding`' not in review
    assert 'asserts a reconciliation or a completed' in provenance
    assert 'Report every violation and narrative problem in this one pass, quoting each' in review
    assert 'the caller settles them all before the next review' in review
    assert '`review (scoped):`' in review
    assert 'for a `slide` or `document` rule, on each slide or file that holds one' in review
    assert ('judge each rule added or changed since, as the diff of `foundation/review-rules.md` shows, against '
            'every narrative in full') in review
    assert 'the lines in the other narratives that state the same claims as a changed line' in review
    assert '`slide` rule' in review and '`document` rule' in review
    # A scoped re-review completes a request or a release; the hand-kept scratch copy is gone.
    assert 'never does' not in review and 'never complete' not in review
    assert 'A passed review completes a request or a release, full or scoped' in review
    assert 'scratch folder' not in review and '`diff -u <copy> <current file>`' not in review
    assert 'a full review is still required' not in review
    # The helper keeps the record: every review is recorded before any file changes, and later ones are scoped.
    assert ('Record every review as soon as it returns, before changing any file: run `review-receipt record '
            '<investigation> <package> --kind full|scoped --report -` through the `package` tool') in review
    assert ('The first review of a draft, or any while `show` reports `none`, is full; every later one is scoped '
            'against the receipt, unless the user asks for a full one') in review
    # The user may accept a narrative problem with a reason, as a warning; the rounds are capped.
    assert ('the user accepted, with a reason, every `warning` violation and narrative problem it reports') in review
    assert '--accept "<file>:<line> <quote>: <the user\'s reason>"' in review
    assert ('When a second review in one request still reports problems, start no third review unless the user '
            'asks') in review
    # Routine repairs are reported at the cap; decisions and rule conflicts still go to the user.
    assert '(unchanged since the prior review)' not in review and 'why the earlier pass missed it' not in review
    assert 'Take a conflict between two rules to the user rather than repairing it' in review
    assert ('At that stop, list the small repairs, those changing no number, no finding beyond narrowing to its '
            'evidence, and no user-written or approved wording, in one plain note') in review
    assert ("in one plain note saying the next request's scoped review checks them") in review
    assert 'show the user each other problem in plain words with a recommended repair' in review
    assert ("Make the small repairs now when no problem needs the user; otherwise make them with the user's answer, "
            'after recording any acceptances with `--accept`') in review
    # Package is done on a passed review of the final files, full or scoped.
    assert 'its `review` row is `current`' in package
    assert 'the last review before the final `check-draft` is a full one' not in package
    assert 'the last review is a full review' not in package
    contract = read('awb-package/references/package-contract.md')
    assert 'check-citation item' not in contract
    assert 'asserting that something was checked or verified' not in review
    assert 'never a scoped re-review' not in release and 'no earlier report is kept' not in release
    assert 'one pass' in reviewer and 'scoped' in reviewer and 'the evidence a narrative cites' in reviewer
    assert '`awb/read` with `command: "review-receipt"`' in reviewer


def test_review_reads_the_brief_and_keeps_tolerances_and_rules_in_bounds():
    # The review reads the brief and checks it; tolerances stay off slides; a rule is the user's to keep.
    def read(path):
        return ' '.join((ROOT / '.agents/skills' / path).read_text(encoding='utf-8').split())

    review = read('awb-package/references/review.md')
    steps = review[review.index('1. Run that command.'):review.index('4. Report exactly this')]
    step3 = steps[steps.index('3. Check what no command checks'):]
    assert '`brief.md`' in steps[:steps.index('2. Judge')]
    assert 'against `brief.md`: every part of its **Business question**' in step3
    assert ('is answered in a slide\'s headline, bullets, or chart, or listed as unanswered on the **Open questions** '
            'or **Limitations and open caveats** slide, not only in a slide\'s **Notes:** or nowhere') in step3
    assert 'how a source builds a series' in step3 and '`foundation/sources.md`' in step3
    # Writing rules live in the contract; the reviewer checks the cited support and brief's definitions.
    contract = read('awb-package/references/package-contract.md')
    rules = contract[contract.index('## Writing rules'):contract.index('## Structural consistency')]
    assert ('a result ID, an evidence path, or a foundation quality ID (`DQ-NNN`) with the path of the scan or '
            'saved query its row cites') in rules
    assert 'including a quality row and its scan or saved query' in step3
    assert "the contract's [Writing rules](package-contract.md#writing-rules) hold" in step3
    assert 'with its tolerance' not in review
    assert ('Any narrative may say figures agree within rounding or within a stated difference when '
            '`methodology.md` states the recorded difference and cites the result or judgment recording it') in rules
    assert ("A tolerance number appears only in `methodology.md` or a slide's **Notes:**, and only one recorded "
            "before the result in `brief.md` or the result's settings") in rules
    assert '`methodology.md` cites that record' in rules
    assert "one only in a judgment's `detail` included, is a problem" not in review + contract
    assert 'Only an exact check says "exactly" or "every row"' in rules
    assert 'before the data was seen' not in review
    assert ('definitions, exclusion rules, metric names, and accounts of what a metric or check counts match '
            "`brief.md`'s **Population and scope** and **Local terms or departures** and `methodology.md`'s "
            'definitions, or `methodology.md` states the departure') in step3
    assert 'a recorded check that establishes the claim' in step3
    assert ('a verification-only part confirming another result may be answered in **Notes:** alone') in step3
    assert 'record words ledger or disposition' in rules and 'ledger, flagged, or disposition' not in review + contract
    assert 'Repair a true statement by citing its record or rewording it, not deleting it' in review
    assert 'departure from the shared glossary or the brief' in read(
        'awb-package/assets/package-format/methodology-template.md')
    # Readability remains a closed list under Writing rules, quoted like every step 3 problem.
    assert '`foundation/glossary.md`' in rules and 'first use in each' in rules
    assert "the precision the brief's **Audience** states" in rules and 'Outside **Implications**' in rules
    assert "unless the brief's **Audience** records the audience as using it" in rules
    # Rule precedence, and a conflict goes to the user.
    assert 'the `error` rule wins and the line passes the `warning` one' in steps
    assert 'Take a conflict between two rules to the user rather than repairing it' in review

    # No template example puts a tolerance on a slide or in the note.
    for path in ('awb-package/assets/package-format/findings-template.md',
                 'awb-package/assets/package-format/methodology-note-template.md'):
        text = read(path)
        assert not re.search(r'within [0-9.]+ ?%', text) and '0.5%' not in text, path
    for path in ('awb-package/references/package-contract.md', 'awb-init/assets/workbench/workbench-guides/analysis.md',
                 'awb-init/references/provenance.md'):
        assert 'with its tolerance' not in read(path), path
    contract = read('awb-package/references/package-contract.md')
    assert 'check-citation item' not in contract and 'A tolerance number' in rules
    # The glossary and source register the step 3 checks read make a review stale and scope a later one.
    assert ('the checks against `brief.md`, `foundation/glossary.md`, or `foundation/sources.md` when the diff '
            'changes it') in review
    assert ('once the narratives, `brief.md`, `foundation/glossary.md`, `foundation/sources.md`, '
            '`foundation/quality.md`, or `foundation/review-rules.md` change') in review
    # So does the quality record and each scan methodology.md cites by its path, which scope a later one.
    assert 'or a scan or saved query `methodology.md` names by its path changes' in review
    assert 'every sentence citing a quality ID whose row the diff of `foundation/quality.md` changes' in review
    # Templates point to the list instead of repeating its tolerance rule.
    for path in ('awb-package/assets/package-format/findings-template.md',
                 'awb-package/assets/package-format/methodology-note-template.md'):
        assert 'Writing rules' in read(path) and 'tolerance' not in read(path)

    # Asking the user comes before recording a rule, in review.md and the skill's first step.
    rule = review[review.index('When the user corrects a draft while reviewing it'):]
    assert rule.index('ask the user before repairing') < rule.index('Only on their yes, record the rule') \
        < rule.index('review-rules add --confirmed')
    assert 'saying in plain words what would be checked' in rule and '--package <investigation>/<package>' in rule
    assert 'An `error` rule wins over a `warning` rule it conflicts with' in rule
    assert 'rather than a standard such as a word limit or a decimal place' in rule
    package = read('awb-package/SKILL.md')
    establish = package[package.index('## 1. Establish'):package.index('## 2. Gather')]
    assert 'first ask the user whether later drafts should be checked for it' in establish
    assert 'record it as a review rule only on their yes' in establish
    # A methods note length is recorded in one form that check-draft reads.
    brief = read('awb-init/assets/workbench/investigation/brief.md')
    assert '`Methods note length: about <n> words`' in brief and 'Methods note length' in establish
    assert '`note_length`' in package[package.index('## 6. Check'):package.index('## 7. Report')]



def test_package_writing_rules_are_one_short_list_read_before_drafting():
    package = ROOT / '.agents/skills/awb-package'
    contract = (package / 'references/package-contract.md').read_text(encoding='utf-8')
    rules = section(contract, '## Writing rules')
    lines = [line for line in rules.splitlines() if line.strip()]
    assert lines and all(line.startswith('- ') for line in lines)
    assert max(map(len, lines)) <= 400
    all_text = '\n'.join(path.read_text(encoding='utf-8') for path in package.rglob('*.md'))
    for rule in ('sentences in the imperative', 'record words ledger or disposition', 'first use in each',
                 'Every sentence asserting that something was checked or verified',
                 'Any narrative may say figures agree within rounding', 'A tolerance number appears only',
                 'Only an exact check says "exactly" or "every row"'):
        assert rules.count(rule) == 1, rule
        assert all_text.count(rule) == 1, rule
    skill = (package / 'SKILL.md').read_text(encoding='utf-8')
    step3 = next(line for line in skill.splitlines() if line.startswith('3. **Write**'))
    assert "contract's **Writing rules**" in step3
    review = (package / 'references/review.md').read_text(encoding='utf-8')
    assert '[Writing rules](package-contract.md#writing-rules)' in review
    assert 'ledger, flagged, or disposition' not in review
    assert 'first use' not in review and 'imperative' not in review

def test_release_reuses_a_matching_receipt_and_shows_its_repairs():
    release = ' '.join((ROOT / '.agents/skills/awb-release/SKILL.md').read_text(encoding='utf-8').split())
    step = release[release.index('## 2. Review'):release.index('## 3. Release')]
    # A receipt that still matches is reused; a changed draft is reviewed scoped against it.
    assert 'A matching receipt, `current`, needs no review' in step
    assert ('When it is `stale` or `failed`, run the scoped read-only review in [awb-package\'s '
            'references/review.md](../awb-package/references/review.md) against it, or the full one when it is '
            '`none`') in step
    assert step.index('`python3 src/awb.py review-receipt show <investigation> <package>`') < step.index('scoped')
    assert step.index('through the `read` tool') < step.index('python3 src/awb.py review-receipt show')
    # A repair made for the release is shown before release runs.
    assert ('after it, show the user the changed slides and wait for their yes before running `release`, unless '
            'they said to release without seeing it') in step
    assert '`no passed review of this draft`' in release


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
    for term in ('Finding', 'Provisional', 'Question ledger', 'Review rule', 'Release'):
        assert f'**{term}**' in quick, term
    # Terms an analyst never needs stay out of the glossary; when a flagged finding is asked about is said once.
    for term in ('Canonical view', 'Receipt', 'Disposition'):
        assert f'**{term}**' not in quick, term
    assert 'You are asked about a flagged finding only when the draft shows it' in quick
    # The expectations users missed: headline length, the datasets slide, review rounds, note length, release
    # waiver, URL data, commits, and a status request carrying other requests.
    assert 'at most 15 words' in what and 'your reason is recorded' in quick
    assert 'which a **Supporting datasets** slide then describes' in what
    assert 'released/001/' in what and "reports the copy's full path" in what
    assert 'each later one reads only what changed since' in quick and 'When a second review' in quick
    assert 'line unchanged since the last review' not in quick
    assert 'makes small repairs that change no number' in quick and 'lists them in one note' in quick
    assert 'any acceptances are recorded before repairs' in quick
    assert 'The draft is stable once' in quick
    assert 'about 500 to a page' in quick and 'more than 10% over it' in quick
    assert quick.count('unless you say to release without seeing them') == 2
    assert 'Setup and the scoping round bring no data in' in quick
    assert 'A commit saves' in quick
    assert 'are carried out after it' in quick
    # Clean and explore are one optional step, and the agent may fold them into others.
    assert '**Clean and explore, both optional.**' in quick and 'may fold these checks' in quick
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


def test_agents_md_makes_the_awb_tools_the_first_route_for_helpers():
    # The Commands section used to prefer the tools in one paragraph and say to run helpers with the CLI
    # in another, and agents followed the CLI line.
    commands = ' '.join(section(AGENTS.read_text(encoding='utf-8'), '## Commands').split())
    assert 'Run workbench helpers with `python3 src/awb.py <command>`' not in commands
    assert commands.startswith('When the host offers the `awb` MCP server, use its tools for `awb.py` commands')
    assert ('Run helpers as black boxes through the `awb` tools, else as `python3 src/awb.py <command>`'
            in commands)
    # Changing a shipped helper or package-format template needs the user's yes, asked in plain words;
    # opening one to adapt or debug it is the rule awb-package's helpers.md states too.
    assert ("open one's source only to adapt or debug it, and change shipped helpers or `package-format/` "
            "templates only once the user, asked plainly, agrees" in commands)
    helpers = (ROOT / '.agents/skills/awb-package/references/helpers.md').read_text(encoding='utf-8')
    assert 'open its source only to adapt or debug it' in helpers


HELPER_SKILLS = ('awb-package', 'awb-release', 'awb-status', 'awb-clean', 'awb-explore', 'awb-scope',
                 'awb-brainstorm', 'awb-init')


@pytest.mark.parametrize('skill', HELPER_SKILLS)
def test_each_skill_that_runs_helpers_names_the_mcp_route_under_its_heading(skill):
    text = (ROOT / f'.agents/skills/{skill}/SKILL.md').read_text(encoding='utf-8')
    heading = re.search(r'^# .+\n\n(.+)\n', text, re.M)
    assert heading and heading.group(1) == (
        "Run this skill's commands through the `awb` MCP tools when the host offers them, as the project's "
        "`AGENTS.md` **Commands** maps them; the command lines below are the fallback."), skill


def test_init_creates_the_venv_records_the_interpreter_and_fills_storage_lines():
    foundation = ' '.join(section((ROOT / '.agents/skills/awb-init/SKILL.md').read_text(encoding='utf-8'),
                                  '## 3. Create the project foundation').split())
    # Setup on a fresh project ran under the MCP server's own Python and recorded it.
    assert ('When the project has no virtual environment and the user named no interpreter, first create '
            '`.venv` in the project') in foundation
    assert 'if that fails, ask once which interpreter to use' in foundation
    assert "passing that interpreter's absolute path as `interpreter`" in foundation
    assert 'Report in one line the interpreter its `interpreter` entry records.' in foundation
    # The storage lines take the forms the landing and release helpers copy to.
    assert ("write it on README's `Landed data is kept at` or `Released packages are kept at` line: an absolute "
            "path, a path starting with `~`, or one relative to the project root starting with `./` or `../`"
            in foundation)


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
