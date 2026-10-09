#!/usr/bin/env python3
"""Compare declared instruction paths with a Git baseline; counts are not tokens."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = '.agents/skills/'
AGENTS = SKILLS + 'awb-init/assets/workbench/AGENTS.md'
ANALYSIS = SKILLS + 'awb-init/assets/workbench/workbench-guides/analysis.md'
DATA = SKILLS + 'awb-init/assets/workbench/workbench-guides/data.md'


def skill(name):
    return SKILLS + name + '/SKILL.md'


def measure(paths, baseline=None):
    words = chars = 0
    for path in dict.fromkeys(paths):
        if baseline:
            text = subprocess.run(['git', 'show', f'{baseline}:{path}'], cwd=ROOT,
                                  check=True, capture_output=True, text=True).stdout
        else:
            text = (ROOT / path).read_text()
        words += len(text.split())
        chars += len(text)
    return {'words': words, 'characters': chars, 'files': list(dict.fromkeys(paths))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='40a0e9330607686e1326f699c684da04c55c13a3',
                        help='Baseline revision (default: PR #6 merge, including current package and figure rules)')
    args = parser.parse_args()
    scenarios = {
        'project_entry': ([AGENTS], [AGENTS]),
        'analysis_procedures': ([AGENTS], [AGENTS, DATA, ANALYSIS]),
        'status_entry': ([AGENTS, skill('awb-status')], [AGENTS, skill('awb-status'), SKILLS + 'awb-status/references/next-requests.md']),
        'table': ([AGENTS, skill('awb-visualize')],
                  [AGENTS, ANALYSIS, skill('awb-visualize'), SKILLS + 'awb-visualize/references/tables.md']),
        'release_without_revision': ([AGENTS, skill('awb-release'), skill('awb-package')],
                    [AGENTS, skill('awb-release'), SKILLS + 'awb-package/references/package-contract.md',
                     SKILLS + 'awb-package/references/manifest-helper.md',
                     SKILLS + 'awb-package/references/findings-helper.md']),
        'narrative_revision': ([AGENTS, skill('awb-package')],
                    [AGENTS, skill('awb-package'), SKILLS + 'awb-package/references/package-contract.md',
                     SKILLS + 'awb-package/references/manifest-helper.md',
                     SKILLS + 'awb-package/references/findings-helper.md']),
    }
    result = {'measurement': 'Static instruction words and characters, not model tokens or full-run cost',
              'baseline': args.baseline, 'scenarios': {}}
    for name, (before_paths, after_paths) in scenarios.items():
        before, after = measure(before_paths, args.baseline), measure(after_paths)
        result['scenarios'][name] = {'before': before, 'after': after,
            'word_reduction_percent': round(100 * (before['words'] - after['words']) / before['words'], 1)}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
