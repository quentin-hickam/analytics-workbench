"""Execute the documented recipe against the bundled project style API."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image


SKILL = Path(__file__).resolve().parents[1] / ".agents/skills/awb-visualize"


def test_documented_recipe_uses_current_style_and_saves_checked_png(tmp_path):
    module = tmp_path / "src/presentation/style.py"
    module.parent.mkdir(parents=True)
    shutil.copy2(SKILL / "assets/awb_style.py", module)
    recipe = (SKILL / "references/plotting-recipes.md").read_text()
    code = re.search(r"```python\n(.*?)\n```", recipe, re.DOTALL).group(1)
    call = '''
path = draw_rates(
    ["North", "West", "East"], [0.21, 0.12, 0.09],
    "West closes 12% of cases late", "rates.png",
    {"Source": "cases.closed", "Comment": "recorded estimates"},
)
assert path.name == "rates.png"
'''
    # A fresh project process catches import/API drift without borrowing modules
    # from the test runner. save_figure must pass check_text before writing.
    result = subprocess.run(
        [sys.executable, "-c", code + call],
        cwd=tmp_path,
        env={
            **os.environ,
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(tmp_path / "matplotlib"),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    with Image.open(tmp_path / "rates.png") as image:
        assert image.width == 1300
        assert image.convert("RGBA").getchannel("A").getextrema() == (255, 255)
        assert image.info["Source"] == "cases.closed"
        assert image.info["Comment"] == "recorded estimates"
