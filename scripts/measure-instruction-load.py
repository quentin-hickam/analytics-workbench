#!/usr/bin/env python3
"""Compare declared instruction paths with a Git baseline; counts are not tokens.

A declared path missing from the baseline revision or the working tree counts as zero
words and is listed under that side's `missing`, so the script runs across layout changes.
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = '.agents/skills/'
AGENTS = SKILLS + 'awb-init/assets/workbench/AGENTS.md'
ANALYSIS = SKILLS + 'awb-init/assets/workbench/workbench-guides/analysis.md'
DATA = SKILLS + 'awb-init/assets/workbench/workbench-guides/data.md'
CONTRACT = SKILLS + 'awb-package/references/package-contract.md'


def skill(name):
    return SKILLS + name + '/SKILL.md'


def read(path, baseline):
    if baseline:
        shown = subprocess.run(['git', 'show', f'{baseline}:{path}'], cwd=ROOT,
                               capture_output=True, text=True)
        return shown.stdout if shown.returncode == 0 else None
    file = ROOT / path
    return file.read_text() if file.is_file() else None


def measure(paths, baseline=None):
    words = chars = 0
    files, missing = [], []
    for path in dict.fromkeys(paths):
        text = read(path, baseline)
        if text is None:
            missing.append(path)
            continue
        files.append(path)
        words += len(text.split())
        chars += len(text)
    return {'words': words, 'characters': chars, 'files': files, 'missing': missing}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='40a0e9330607686e1326f699c684da04c55c13a3',
                        help='Baseline revision (default: PR #6 merge, including current package and figure rules)')
    args = parser.parse_args()
    # name: (baseline paths, current paths). The baseline's AGENTS.md held every data and
    # analysis procedure, so it is the baseline path for cleaning and exploration too.
    scenarios = {
        'project_entry': ([AGENTS], [AGENTS]),
        'analysis_procedures': ([AGENTS], [AGENTS, DATA, ANALYSIS]),
        'status_entry': ([AGENTS, skill('awb-status')], [AGENTS, skill('awb-status')]),
        'release_without_revision': ([AGENTS, skill('awb-release'), skill('awb-package')],
                                     [AGENTS, skill('awb-release')]),
        'release_with_flag': ([AGENTS, skill('awb-release'), skill('awb-package')],
                              [AGENTS, skill('awb-release'), CONTRACT]),
        'narrative_revision': ([AGENTS, skill('awb-package')], [AGENTS, skill('awb-package'), CONTRACT]),
        'clean': ([AGENTS], [AGENTS, skill('awb-clean')]),
        'eda': ([AGENTS], [AGENTS, skill('awb-eda'), SKILLS + 'awb-eda/references/follow-up-queries.md']),
    }
    result = {'measurement': 'Static instruction words and characters, not model tokens or full-run cost',
              'baseline': args.baseline, 'scenarios': {}}
    for name, (before_paths, after_paths) in scenarios.items():
        before, after = measure(before_paths, args.baseline), measure(after_paths)
        reduction = (round(100 * (before['words'] - after['words']) / before['words'], 1)
                     if before['words'] else None)
        result['scenarios'][name] = {'before': before, 'after': after, 'word_reduction_percent': reduction}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
