import json
import os

import pytest

from tak.ui import UIType

from tidewater import facts
from tidewater import game as gameModule
from tidewater.game import Tidewater, describeSlot
from conftest import ScriptedUI


@pytest.fixture
def scripted(monkeypatch):
    """Build Tidewater against a ScriptedUI instead of a real front-end."""
    holder = {}

    def fakeCreate(uiType, prompt, header, **kwargs):
        ui = ScriptedUI(holder["script"], header)
        ui.currentPrompt = prompt
        holder["ui"] = ui
        return ui

    monkeypatch.setattr(gameModule, "createUserInterface", fakeCreate)

    def make(script):
        holder["script"] = script
        game = Tidewater()
        return game, holder["ui"]

    return make


# The whole solution, from a fresh save, in two loops. Every label here is a
# menu row or a dialogue question; the ScriptedUI fails loudly if one is
# missing or unavailable, so this is the test that says the game is solvable.
LOOP_ONE = [
    "Create New Save",
    "Talk to Sam",
    "What about the bell",
    "[Back]",  # 8 -> 9: SAM_BELL
    "Go to the bank",
    "Talk to Margaret",
    "old books about the harbour bell",
    "[Back]",  # 9 -> 10: MARIGOLD
    "Go home",
    "Sleep until the bell",  # -> storm, bell, reset
]
LOOP_TWO = (
    [
        "Go home",
    ]
    + ["Wait an hour"] * 10
    + [  # 8 -> 18
        "Go to the tavern",
        "Talk to Old Tom",
        "I know about the Marigold",
        "[Back]",  # 18 -> 19: rope
        "Go to the docks",
        "Climb the tower and hang the bell rope",  # 19 -> 20
        "Wait in the tower for eleven",  # -> the bell, for real
        "Quit",
    ]
)


def test_the_loop_can_be_broken_in_two_loops(scripted):
    game, ui = scripted(LOOP_ONE + LOOP_TWO)
    game.play()

    assert game.meta.loopBroken is True
    assert game.meta.loops == 2
    assert game.meta.endings == ["bell"]
    for fact in (
        facts.SAM_BELL,
        facts.MARIGOLD,
        facts.THE_STORM,
        facts.THE_BELL,
        facts.THE_ROPE,
        facts.LOOP_BROKEN,
    ):
        assert game.meta.knows(fact), fact
    assert ui.saw("This has happened before")
    assert ui.saw(
        "[You've been through this day before"
    )  # the journal unlock, announced once
    assert ui.saw("[You know when the storm comes")  # the plan, announced once
    assert ui.saw("broken the loop")
    assert ui.cleanedUp
    # The save on disk carries the ending.
    with open(game.saveFileManager.get_save_path("save.json")) as f:
        assert json.load(f)["meta"]["loopBroken"] is True


def test_the_first_loop_alone_does_not_break_anything(scripted):
    game, ui = scripted(LOOP_ONE + ["Quit"])
    game.play()
    assert game.meta.loops == 2 and not game.meta.loopBroken
    assert game.loop.hour == 8 and game.loop.location == "docks"
    assert game.meta.knows(facts.THE_STORM)  # slept through it, still heard it


def test_toms_line_needs_the_name_and_the_docks_need_the_rope(scripted):
    # Without the Marigold's name, Tom's question is not on the menu.
    game, ui = scripted(
        ["Create New Save", "Go home"]
        + ["Wait an hour"] * 10
        + ["Go to the tavern", "Talk to Old Tom", "I know about the Marigold"]
    )
    with pytest.raises(AssertionError) as error:
        game.play()
    assert "not on menu" in str(error.value)


def test_the_storm_cuts_the_docks_off(scripted):
    game, ui = scripted(
        ["Create New Save", "Go home"] + ["Wait an hour"] * 13 + ["Go to the docks"]
    )
    with pytest.raises(AssertionError) as error:
        game.play()
    assert "storm" in str(error.value)
    assert game.loop.hour == 21


def test_being_on_the_docks_when_the_storm_hits_drives_you_home(scripted):
    game, ui = scripted(["Create New Save"] + ["Wait an hour"] * 13 + ["Quit"])
    game.play()
    assert game.loop.location == "home"
    assert ui.saw("driven back up the front")


def test_fishing_is_the_same_every_loop(scripted):
    game, ui = scripted(
        [
            "Create New Save",
            "Fish",
            "Fish",
            "Go home",
            "Sleep until the bell",
            "Fish",
            "Fish",
            "Quit",
        ]
    )
    game.play()
    # The prompt line above the docks menu carries the catch.
    catches = [m[3] for m in ui.menus if m[3].startswith("An hour on the water")]
    assert len(catches) == 4
    assert catches[:2] == catches[2:]
    assert game.meta.loops == 2
    assert game.loop.rngDraws == 2


def test_a_saved_game_reloads_where_it_left_off(scripted, tmp_path):
    game, ui = scripted(LOOP_ONE + ["Quit"])
    game.play()

    game2, ui2 = scripted(
        [
            "Load Slot 1",
            "Go home",
            "Read your journal",
            "What you know",
            "Close the journal",
            "Quit",
        ]
    )
    game2.play()
    assert game2.meta.loops == 2
    assert game2.meta.knows(facts.MARIGOLD)
    assert ui2.menus[0][1][0] == "Load Slot 1 (Loop 2, 4 known)"
    assert ui2.saw("The Marigold")
    assert ui2.saw("* marks the trail")


def test_the_journal_is_not_offered_in_the_first_loop(scripted):
    game, ui = scripted(["Create New Save", "Go home", "Quit"])
    game.play()
    homeMenu = [m for m in ui.menus if m[0].startswith("Home")][0]
    assert not any("journal" in label for label in homeMenu[1])


def test_quitting_the_save_menu_plays_nothing_but_cleans_up(scripted):
    game, ui = scripted(["Quit"])
    game.play()
    assert game.running is False and ui.cleanedUp
    assert len(ui.menus) == 1


def test_a_damaged_save_is_copied_aside_and_started_fresh(scripted, tmp_path):
    game, ui = scripted(["Create New Save", "Quit"])
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path, "w") as f:
        f.write(
            '{"version": 1, "meta": {"loops": 0, "facts": []}, "loop": {"hour": 8}}'
        )  # loops < 1

    # Damaged slots are listed but unpickable, so the way in is a new slot -
    # unless the file parses as JSON, as this one does: then it is loadable
    # and fails schema validation on the way in.
    game2, ui2 = scripted(["Load Slot 1", "Quit"])
    game2.play()
    assert game2.failedLoad
    assert ui2.saw("could not be read")
    assert any(
        name.startswith("save.json.damaged-")
        for name in os.listdir(os.path.dirname(path))
    )
    assert game2.meta.loops == 1


def test_describeSlot():
    assert describeSlot({"loops": 3, "known": 2}) == "Loop 3, 2 known"
    assert (
        describeSlot({"loops": 3, "known": 7, "loopBroken": True})
        == "loop broken, 7 known"
    )
