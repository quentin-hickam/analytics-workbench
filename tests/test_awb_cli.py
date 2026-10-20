# Kept cases:
# test_help_lists_every_command: --help and no arguments print every command with its summary and the per-command help pointer; the commands with state before stale, review-rules between export and check-draft, friction last, export covering --result, draft-provenance gone.
# test_dispatches_to_helper_function: a command loads its helper by path and passes the project root and remaining arguments.
# test_missing_helper_or_function_and_unknown_command: each exits 2 with a message naming the remedy.
# test_interpreter_line_accepted_and_refused_forms: README's `Project interpreter:` line is read only at column 0, once, as `not yet recorded` or a path to an existing file, absolute or project-relative, in optional backticks; a repeated or empty line or a path naming no file is refused with the reason.
# test_awb_reexecutes_under_the_project_interpreter: run by another interpreter, src/awb.py reruns itself under the project's .venv interpreter, noting it on stderr; run by that interpreter it runs once, silently; README's recorded interpreter comes before .venv, a refused line is noted and skipped, and AWB_PYTHON overrides both.
# test_reexecution_never_loops: an interpreter that execs another one is run once, not again, because the rerun carries a marker it clears for its own subprocesses.
# test_aliases_of_one_interpreter_are_the_same: outside a virtual environment, two links to one binary are the same interpreter, so neither reruns the other; a virtual environment's link to it, or another file, is not.
# test_hardlinked_interpreter_in_another_prefix_is_another_interpreter: a hard link to this interpreter's binary in another directory, as package managers link one environment's interpreter from a shared cache, is not this interpreter: awb.py reruns under it with a note.
# test_recorded_interpreter_that_cannot_run_is_noted: a README interpreter that exists but cannot be executed is noted on stderr and the command runs under the interpreter that started it, without a traceback.

import importlib.util
import os
import shutil
import subprocess
import sys
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
        assert "<command> --help" in out and "Exit status" in out
    assert list(cli.COMMANDS) == ["land", "retain", "publish", "sql", "profile", "state", "questions", "stale",
                                  "export", "review-rules", "review-receipt", "check-draft", "release", "copy-releases", "friction"]
    assert "--result" in cli.COMMANDS["export"][2]


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
    assert "install_helpers.py --upgrade" in capsys.readouterr().err
    assert cli.main(["nope"]) == 2
    assert "unknown command" in capsys.readouterr().err


@pytest.mark.parametrize("readme, expected", [
    (None, ("none", None, None)),
    ("# Project\n\nActive investigation: none\n", ("none", None, None)),
    ("Project interpreter: not yet recorded\n", ("unrecorded", "not yet recorded", None)),
    ("Project interpreter: Not yet recorded\n", ("unrecorded", "Not yet recorded", None)),
    ("Project interpreter: `.venv/bin/python`\n", ("recorded", ".venv/bin/python", "{root}/.venv/bin/python")),
    ("Project interpreter:   {root}/.venv/bin/python  \n", ("recorded", "{root}/.venv/bin/python",
                                                           "{root}/.venv/bin/python")),
    ("  Project interpreter: .venv/bin/python\n", ("none", None, None)),
    ("Project interpreter: .venv/bin/python\nProject interpreter: .venv/bin/python\n",
     ("refused", None, "README.md repeats the Project interpreter line")),
    ("Project interpreter:\n", ("refused", "", "README's Project interpreter line is empty")),
    ("Project interpreter: ``\n", ("refused", "", "README's Project interpreter line is empty")),
    ("Project interpreter: .venv/bin/python3.99\n",
     ("refused", ".venv/bin/python3.99", "README's Project interpreter .venv/bin/python3.99 names no file")),
    ("Project interpreter: .venv/bin\n", ("refused", ".venv/bin", "README's Project interpreter .venv/bin names no file")),
])
def test_interpreter_line_accepted_and_refused_forms(tmp_path, readme, expected):
    cli = install(tmp_path)
    (tmp_path / ".venv/bin").mkdir(parents=True)
    (tmp_path / ".venv/bin/python").write_text("")
    root = str(tmp_path.resolve())
    if readme is not None:
        (tmp_path / "README.md").write_text(readme.replace("{root}", root))
    status, value, detail = cli.read_interpreter(cli.ROOT)
    expected = tuple(item.replace("{root}", root) if isinstance(item, str) else item for item in expected)
    assert (status, value, str(detail) if status == "recorded" else detail) == expected


def stub_project(tmp_path):
    """A project whose stale helper prints the interpreter running it, and a stub .venv whose python is a
    link to this interpreter, so running the stub runs this interpreter under the stub's path."""
    install(tmp_path)
    (tmp_path / "src/provenance.py").write_text("import sys\n\n\ndef cli_stale(root, argv):\n"
                                                "    print(sys.executable)\n    return 0\n")
    (tmp_path / ".venv/bin").mkdir(parents=True)
    os.symlink(sys.executable, tmp_path / ".venv/bin/python")
    # As in every virtual environment, pyvenv.cfg makes it one, apart from the interpreter it links to.
    (tmp_path / ".venv/pyvenv.cfg").write_text(f"home = {os.path.dirname(sys.executable)}\n")
    return tmp_path


def run(interpreter, root, **env):
    clean = {key: value for key, value in os.environ.items() if key not in ("AWB_PYTHON", "AWB_REEXECUTED")}
    return subprocess.run([str(interpreter), str(root / "src/awb.py"), "stale"], capture_output=True, text=True,
                          env={**clean, **env}, timeout=60)


@pytest.mark.skipif(os.name == "nt", reason="the stub venv is a POSIX symlink")
def test_awb_reexecutes_under_the_project_interpreter(tmp_path):
    root = stub_project(tmp_path)
    venv = root / ".venv/bin/python"
    result = run(sys.executable, root)
    assert result.returncode == 0 and result.stdout.strip() == str(venv)
    assert result.stderr.count("awb.py: running under") == 1 and str(venv) in result.stderr
    # Already under it: one run, no note.
    result = run(venv, root)
    assert result.returncode == 0 and result.stdout.strip() == str(venv) and result.stderr == ""
    # README's recorded interpreter comes before .venv.
    other = root / "other/bin/python"
    other.parent.mkdir(parents=True)
    os.symlink(sys.executable, other)
    (root / "README.md").write_text("# P\n\nProject interpreter: other/bin/python\n")
    result = run(venv, root)
    assert result.stdout.strip() == str(root.resolve() / "other/bin/python") and "README's Project interpreter" in result.stderr
    # A refused line is noted and the next source used.
    (root / "README.md").write_text("# P\n\nProject interpreter: gone/bin/python\n")
    result = run(sys.executable, root)
    assert result.stdout.strip() == str(root.resolve() / ".venv/bin/python")
    assert "README's Project interpreter gone/bin/python names no file" in result.stderr
    # AWB_PYTHON overrides both.
    result = run(venv, root, AWB_PYTHON=sys.executable)
    assert result.stdout.strip() == sys.executable and "AWB_PYTHON" in result.stderr
    result = run(sys.executable, root, AWB_PYTHON=sys.executable)
    assert result.stdout.strip() == sys.executable and result.stderr == ""


@pytest.mark.skipif(os.name == "nt", reason="the stub interpreter is a POSIX shell script")
def test_reexecution_never_loops(tmp_path):
    root = stub_project(tmp_path)
    log = tmp_path / "stub.log"
    stub = root / ".venv/bin/python"
    stub.unlink()
    # A wrapper that runs this interpreter: under it sys.executable is never the stub's path.
    stub.write_text(f'#!/bin/sh\necho run >> "{log}"\nexec "{sys.executable}" "$@"\n')
    stub.chmod(0o755)
    result = run(sys.executable, root)
    assert result.returncode == 0 and result.stdout.strip() == sys.executable
    assert log.read_text() == "run\n" and result.stderr.count("awb.py: running under") == 1
    # The marker is cleared for the rerun's own subprocesses.
    (root / "src/provenance.py").write_text("import os\n\n\ndef cli_stale(root, argv):\n"
                                            "    print(os.environ.get('AWB_REEXECUTED'))\n    return 0\n")
    assert run(sys.executable, root).stdout.strip() == "None"


@pytest.mark.skipif(os.name == "nt" or sys.prefix != sys.base_prefix,
                    reason="POSIX links to an interpreter outside any virtual environment")
def test_aliases_of_one_interpreter_are_the_same(tmp_path):
    cli = install(tmp_path)
    links = []
    for name in ("a/bin/python", "b/bin/python3"):
        links.append(tmp_path / name)
        links[-1].parent.mkdir(parents=True)
        os.symlink(sys.executable, links[-1])
    assert all(cli.same_interpreter(link) for link in links)
    # A virtual environment's link sees other packages, and another file is another interpreter.
    venv = tmp_path / "env/bin/python"
    venv.parent.mkdir(parents=True)
    os.symlink(sys.executable, venv)
    (tmp_path / "env/pyvenv.cfg").write_text(f"home = {os.path.dirname(sys.executable)}\n")
    other = tmp_path / "c/bin/python"
    other.parent.mkdir(parents=True)
    other.write_text("#!/bin/sh\n")
    assert not cli.same_interpreter(venv) and not cli.same_interpreter(other)
    # Started through one link with README naming the other, awb.py runs once, without a note.
    root = stub_project(tmp_path / "project")
    (root / "README.md").write_text(f"# P\n\nProject interpreter: {links[1]}\n")
    result = run(links[0], root)
    assert result.returncode == 0 and result.stdout.strip() == str(links[0]) and result.stderr == ""


@pytest.mark.skipif(os.name == "nt", reason="the copied interpreter is a POSIX executable")
def test_hardlinked_interpreter_in_another_prefix_is_another_interpreter(tmp_path):
    cli = install(tmp_path)
    # Two prefixes sharing one binary: neither is a virtual environment, and each would see its own packages.
    base, env = tmp_path / "base/bin/python3", tmp_path / "env/bin/python3"
    base.parent.mkdir(parents=True)
    env.parent.mkdir(parents=True)
    shutil.copy2(os.path.realpath(sys.executable), base)
    os.link(base, env)
    assert not cli.same_interpreter(base) or os.path.realpath(sys.executable) == str(base)
    assert not cli.same_interpreter(env)
    root = stub_project(tmp_path / "project")
    (root / "README.md").write_text(f"# P\n\nProject interpreter: {env}\n")
    result = run(base, root)
    assert result.returncode == 0 and result.stdout.strip() == str(env)
    assert f"awb.py: running under {env} (README's Project interpreter)" in result.stderr


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes")
def test_recorded_interpreter_that_cannot_run_is_noted(tmp_path):
    root = stub_project(tmp_path)
    (root / "notes.txt").write_text("not an interpreter\n")
    (root / "README.md").write_text("# P\n\nProject interpreter: notes.txt\n")
    result = run(sys.executable, root)
    assert result.returncode == 0 and result.stdout.strip() == sys.executable
    assert f"awb.py: cannot run {root.resolve() / 'notes.txt'} (README's Project interpreter)" in result.stderr
    assert f"continuing under {sys.executable}" in result.stderr and "Traceback" not in result.stderr
