# Kept cases:
# test_missing_paths_count_zero_and_are_listed: a path absent from the working tree or the baseline revision adds no words and is listed under missing instead of raising.
# test_package_required_files_stay_under_their_word_budget: the package skill, contract, and review together stay within their combined count before #112.
# test_package_number_and_evidence_reference_stays_under_its_word_budget: the file the skill links for both number contexts and missing evidence holds at most 2500 words.

import importlib.util
from pathlib import Path
import re

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/measure-instruction-load.py"


def load():
    spec = importlib.util.spec_from_file_location("measure_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_paths_count_zero_and_are_listed():
    measure = load().measure
    present, absent = "README.md", "no-such-dir/absent.md"
    for baseline in (None, "HEAD"):
        both = measure([present, absent], baseline)
        alone = measure([present], baseline)
        assert both["missing"] == [absent]
        assert both["files"] == [present]
        assert both["words"] == alone["words"] > 0


# The project AGENTS.md is loaded in every session, so it holds this budget: its word and character
# counts before #62 added its conversation rules. A new rule cuts as many words elsewhere in it.
AGENTS_WORDS, AGENTS_CHARACTERS = 814, 5716


def test_always_loaded_agents_md_does_not_grow():
    module = load()
    loaded = module.measure([module.AGENTS])
    assert loaded["files"] == [module.AGENTS]
    assert loaded["words"] <= AGENTS_WORDS
    assert loaded["characters"] <= AGENTS_CHARACTERS


PACKAGE_REQUIRED_WORDS, PACKAGE_NUMBER_AND_EVIDENCE_WORDS = 7716, 2500


def test_package_required_files_stay_under_their_word_budget():
    module = load()
    paths = [module.skill("awb-package"), module.CONTRACT, module.REVIEW]
    loaded = module.measure(paths)
    assert loaded["files"] == paths
    assert loaded["words"] <= PACKAGE_REQUIRED_WORDS


def test_package_number_and_evidence_reference_stays_under_its_word_budget():
    module = load()
    skill = module.read(module.skill("awb-package"), None)
    assert len(re.findall(r"\]\(references/numbers-and-evidence\.md(?:#[^)]+)?\)", skill)) == 2
    loaded = module.measure([module.NUMBERS_AND_EVIDENCE])
    assert loaded["files"] == [module.NUMBERS_AND_EVIDENCE]
    assert loaded["words"] <= PACKAGE_NUMBER_AND_EVIDENCE_WORDS
