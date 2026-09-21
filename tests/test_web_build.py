import os
import subprocess
import sys
import zipfile

from conftest import REPOSITORY_ROOT


def test_the_page_uses_the_kits_assets_and_names_the_game():
    with open(os.path.join(REPOSITORY_ROOT, "web", "index.html")) as f:
        page = f.read()
    assert "<title>Tidewater</title>" in page
    for asset in ("/tak/client.css", "/tak/client.js", "/tak/boot.js"):
        assert asset in page, asset
    assert 'idbName: "tidewater-saves"' in page
    assert 'saveDirEnv: "TIDEWATER_SAVE_DIR"' in page
    assert 'entry: "web/pyodide_main.py"' in page


def test_the_bundle_carries_the_game_and_the_kit(tmp_path):
    from tak.web.bundle import build

    output = build(
        REPOSITORY_ROOT,
        outputPath=str(tmp_path / "game.zip"),
        extraFiles=("version.txt", "web/pyodide_main.py"),
    )
    with zipfile.ZipFile(output) as bundle:
        names = set(bundle.namelist())
    for required in (
        "src/tidewater/game.py",
        "src/tidewater/scenes/docks.py",
        "src/tidewater/trace_client.py",
        "src/tak/ui/pyodide.py",
        "src/tak/web/assets/client.js",
        "schemas/save.json",
        "web/pyodide_main.py",
        "version.txt",
    ):
        assert required in names, required


def test_build_zip_script_runs(tmp_path):
    env = dict(os.environ)
    result = subprocess.run(
        [sys.executable, os.path.join("web", "build_zip.py")],
        cwd=REPOSITORY_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert os.path.exists(os.path.join(REPOSITORY_ROOT, "web", "game.zip"))


def test_pyodide_entry_point_builds_the_pyodide_front_end():
    with open(os.path.join(REPOSITORY_ROOT, "web", "pyodide_main.py")) as f:
        source = f.read()
    assert "UIType.PYODIDE" in source and "Tidewater(" in source
