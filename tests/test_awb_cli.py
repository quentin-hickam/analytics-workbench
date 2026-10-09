# Kept cases:
# test_help_lists_every_command: --help and no arguments print every command with its summary.
# test_dispatches_to_helper_function: a command loads its helper by path and passes the project root and remaining arguments.
# test_missing_helper_or_function_and_unknown_command: each exits 2 with a message naming the remedy.

import importlib.util
import shutil
from pathlib import Path

import pytest

ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-init/assets/awb_cli.py"


def install(project):
    (project / "src").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ASSET, project / "src/awb.py")
    spec = importlib.util.spec_from_file_location("awb_cli_under_test", project / "src/awb.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_help_lists_every_command(tmp_path, capsys):
    cli = install(tmp_path)
    for argv in ([], ["--help"]):
        assert cli.main(argv) == 0
        out = capsys.readouterr().out
        assert all(name in out for name in cli.COMMANDS)


def test_dispatches_to_helper_function(tmp_path):
    cli = install(tmp_path)
    helper = tmp_path / "src/provenance.py"
    helper.write_text("def cli_stale(root, argv):\n"
                      "    (root / 'seen.txt').write_text(repr((str(root), argv)))\n"
                      "    return 3\n")
    assert cli.main(["stale", "--json"]) == 3
    assert (tmp_path / "seen.txt").read_text() == repr((str(tmp_path.resolve()), ["--json"]))


def test_missing_helper_or_function_and_unknown_command(tmp_path, capsys):
    cli = install(tmp_path)
    assert cli.main(["sql", "x.sql"]) == 2
    assert "install_helpers.py" in capsys.readouterr().err
    (tmp_path / "src/preparation").mkdir()
    (tmp_path / "src/preparation/landing.py").write_text("def session(root):\n    pass\n")
    assert cli.main(["sql", "x.sql"]) == 2
    assert "awb-update" in capsys.readouterr().err
    assert cli.main(["nope"]) == 2
    assert "unknown command" in capsys.readouterr().err
