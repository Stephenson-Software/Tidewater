"""The location stills (RFC 0025): one picture per place, shipped in game.zip,
shown above that place's menu in the browser and nowhere else."""

import importlib.util
import json
import os
import struct
import zipfile

import pytest

from tak import Prompt

from tidewater import game as gameModule
from tidewater import stills
from tidewater.game import Tidewater
from conftest import REPOSITORY_ROOT, ScriptedUI

PLACES = ["docks", "shop", "home", "tavern", "bank", "lighthouse", "churchyard"]
MANIFEST = os.path.join(REPOSITORY_ROOT, "art", "stills.json")


def manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def pngSize(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", path
    return struct.unpack(">II", head[16:24])


def test_every_place_has_one_still_with_alt_text_a_scene_and_a_picture():
    stillsByPlace = manifest()["stills"]
    assert sorted(stillsByPlace) == sorted(PLACES)
    width, height = manifest()["size"]
    for place, entry in stillsByPlace.items():
        assert entry["alt"].strip(), place
        assert os.path.exists(os.path.join(REPOSITORY_ROOT, entry["scene"])), place
        png = os.path.join(REPOSITORY_ROOT, "pictures", place + ".png")
        assert pngSize(png) == (width, height), place


def test_the_setting_is_marked_provisional_and_every_sun_is_placed():
    data = manifest()
    assert data["provisional"] is True
    for place, entry in data["stills"].items():
        for field in ("date", "time", "utcOffset", "latitude", "longitude"):
            assert entry["sun"][field] not in (None, ""), (place, field)


def test_the_pictures_fit_the_budget():
    budget = manifest()["budgetBytes"]
    pictures = os.path.join(REPOSITORY_ROOT, "pictures")
    used = sum(os.path.getsize(os.path.join(pictures, n)) for n in os.listdir(pictures))
    assert used <= budget, used


def loadRenderScript():
    spec = importlib.util.spec_from_file_location(
        "render", os.path.join(REPOSITORY_ROOT, "art", "render.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_render_script_refuses_a_still_whose_sun_is_not_filled_in():
    render = loadRenderScript()
    still = {
        "sun": {
            "date": "2021-01-10",
            "time": "14:00",
            "utcOffset": 1,
            "latitude": None,
            "longitude": None,
        }
    }
    assert render.sunProblems("strip", still) == [
        "strip: sun.latitude is not filled in",
        "strip: sun.longitude is not filled in",
    ]
    assert render.sunProblems("strip", {}) == ['strip: no "sun" entry']


def test_the_render_script_passes_its_own_check():
    assert loadRenderScript().main(["--check"]) == 0


def test_the_bundle_carries_the_pictures_and_their_manifest_but_not_the_scenes(
    tmp_path,
):
    from tak.web.bundle import build

    output = build(
        REPOSITORY_ROOT,
        outputPath=str(tmp_path / "game.zip"),
        sourceDirectories=("src", "schemas", "pictures"),
        extraFiles=("version.txt", "web/pyodide_main.py", "art/stills.json"),
    )
    with zipfile.ZipFile(output) as bundle:
        names = set(bundle.namelist())
    for place in PLACES:
        assert "pictures/%s.png" % place in names, place
    assert "art/stills.json" in names
    assert not any(name.endswith(".scene") for name in names)
    with open(os.path.join(REPOSITORY_ROOT, "web", "build_zip.py")) as f:
        script = f.read()
    assert '"pictures"' in script and '"art/stills.json"' in script


def test_load_reads_the_alt_text_and_tolerates_a_missing_manifest(tmp_path):
    alts = stills.load()
    assert sorted(alts) == sorted(PLACES)
    assert stills.load(str(tmp_path / "nowhere.json")) == {}


def test_show_sets_a_places_picture_and_clears_it_elsewhere():
    ui = ScriptedUI([])
    stills.show(ui, PLACES[0], {PLACES[0]: "A place."})
    assert ui.picture() == {"key": PLACES[0], "alt": "A place."}
    stills.show(ui, "journal", {PLACES[0]: "A place."})
    assert ui.picture() is None


def test_each_place_is_drawn_with_its_own_still(monkeypatch):
    holder = {}

    def fakeCreate(uiType, prompt, header, **kwargs):
        ui = ScriptedUI(holder["script"], header)
        ui.currentPrompt = prompt
        holder["ui"] = ui
        return ui

    monkeypatch.setattr(gameModule, "createUserInterface", fakeCreate)
    holder["script"] = ["Create New Save", "Go to Gilbert's shop", "Quit"]
    game = Tidewater()
    ui = holder["ui"]
    seen = []
    showOptions = ui.showOptions

    def recording(descriptor, optionList, unavailableOptions=None):
        seen.append((ui.picture() or {}).get("key"))
        return showOptions(descriptor, optionList, unavailableOptions)

    ui.showOptions = recording
    game.play()
    assert seen == ["docks", "shop"]
