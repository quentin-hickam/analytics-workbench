"""Public skill metadata and repository content contracts."""

import json
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


@pytest.mark.parametrize('path', sorted(ROOT.rglob('SKILL.md')),
                         ids=lambda path: str(path.relative_to(ROOT)))
def test_every_skill_has_loadable_metadata(path):
    name, description = skill_metadata(path.read_text(encoding='utf-8'))
    assert name == path.parent.name
    assert re.fullmatch(r'[a-z0-9-]{1,64}', name), name
    assert 1 <= len(description) <= 1024


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
    # dotfiles and binary content. Deleted files, Git history/metadata and ignored
    # build/cache files are outside the repository text contract. Only the root
    # CHANGELOG.md is exempt. File paths are checked along with contents.
    import subprocess

    result = subprocess.run(['git', 'ls-files', '--cached', '--others',
                             '--exclude-standard', '-z'], cwd=ROOT,
                            capture_output=True, check=True)
    offenders = []
    for entry in result.stdout.split(b'\0'):
        if not entry or entry == b'CHANGELOG.md':
            continue
        path = ROOT / entry.decode('utf-8')
        if path.is_file() and (mentions_retired_skill(entry)
                               or mentions_retired_skill(path.read_bytes())):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], offenders
