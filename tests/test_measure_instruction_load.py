# Kept cases:
# test_missing_paths_count_zero_and_are_listed: a path absent from the working tree or the baseline revision adds no words and is listed under missing instead of raising.

import importlib.util
from pathlib import Path

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
