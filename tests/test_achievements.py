# @author Daniel McCoy Stephenson
"""Achievements: every declared one is reachable, the scripted routes unlock
what they should at the moment they should, and nothing touches the save."""

import json
import re

import pytest

from tidewater import achievements, facts
from tidewater.state import MetaState

from test_game import LOOP_ONE, LOOP_TWO, scripted  # noqa: F401 - fixture
from test_second_ending import LOOP_TWO_THE_LIGHT


@pytest.fixture
def unlocks(monkeypatch):
    """Record every arcade unlock instead of sending it (it is a no-op
    outside the browser anyway)."""
    calls = []
    monkeypatch.setattr(achievements.arcade, "unlock", calls.append)
    return calls


WAITS = 6

# Loop two from LOOP_ONE's end, learning every clue and then quitting: the
# shop, the bank's other ledgers, the churchyard, Ada's story, the oil, Tom.
LOOP_TWO_EVERY_CLUE = (
    [
        "Go to Gilbert's shop",
        "Talk to Gilbert",
        "What's the matter with Old Tom?",
        "[Back]",  # 8 -> 9: GILBERT_LEDGERS
        "Go to the bank",
        "Talk to Margaret",
        "Were there other boats?",
        "[Back]",  # 9 -> 10: OTHER_BOATS
        "Go up to the churchyard",
        "Walk the rows",  # THE_HANDS
        "Walk out to the lighthouse",
        "Ask about the night the Marigold went down",
        "Let her tell it in her own time.",  # KEEPER_SAW, Ada will remember
        "Talk to Ada",
        "How long did the lamp hold",
        "[Back]",  # THE_OIL
        "Go to the tavern",  # 14, shut till six
    ]
    + ["Wait an hour"] * 4
    + [
        "Talk to Old Tom",
        "I know about the Marigold",
        "[Back]",  # THE_ROPE
        "Quit",
    ]
)


THE_MENDED_NIGHT = (
    LOOP_ONE
    + [
        "Wait an hour",
        "Walk out to the lighthouse",
        "Ask about the night the Marigold went down",
        "Let her tell it in her own time.",
        "Talk to Ada",
        "How long did the lamp hold",
        "[Back]",
        "Go to Gilbert's shop",
        "Talk to Gilbert",
        "whatever's owed",
        "[Back]",
        "Walk out to the lighthouse",
        "Fill the lamp and light it",
        "Go home",
    ]
    + ["Wait an hour"] * 4
    + [
        "Go to the tavern",
        "Talk to Old Tom",
        "I know about the Marigold",
        "[Back]",
        "Go to the docks",
        "Climb the tower and hang the bell rope",
        "Wait in the tower for eleven",
        "Quit",
    ]
)

# Each scripted route, and the unlocks it reports, in order.
ROUTES = {
    "the bell": (
        LOOP_ONE + LOOP_TWO,
        ["in-the-ledger", "first-reset", "ended-by-the-bell"],
    ),
    "the light": (
        LOOP_ONE + LOOP_TWO_THE_LIGHT,
        [
            "in-the-ledger",
            "first-reset",
            "awake-that-night",
            "remembered",  # Ada, let her tell it
            "remembered",  # Gilbert, whatever's owed
            "ended-by-the-light",
        ],
    ),
    "both": (
        THE_MENDED_NIGHT,
        [
            "in-the-ledger",
            "first-reset",
            "awake-that-night",
            "remembered",
            "remembered",
            "the-night-mended",
        ],
    ),
    "every clue": (
        LOOP_ONE + LOOP_TWO_EVERY_CLUE,
        [
            "in-the-ledger",
            "first-reset",
            "names-in-stone",
            "awake-that-night",
            "remembered",
            "every-thread",
        ],
    ),
}


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_each_route_unlocks_what_it_earns(scripted, unlocks, route):
    script, expected = ROUTES[route]
    game, ui = scripted(script)
    game.play()
    assert unlocks == expected


def test_every_declared_achievement_is_unlocked_by_some_route(scripted, unlocks):
    for script, _ in ROUTES.values():
        game, ui = scripted(script)
        game.play()
    declared = {a["id"] for a in achievements.ACHIEVEMENTS}
    assert set(unlocks) == declared


def test_declarations_are_well_formed():
    ids = [a["id"] for a in achievements.ACHIEVEMENTS]
    assert len(ids) == len(set(ids))
    assert 6 <= len(ids) <= 12
    for a in achievements.ACHIEVEMENTS:
        assert re.match(r"^[a-z][a-z0-9-]{1,30}$", a["id"]), a["id"]
        assert a["title"] and a["description"]
        assert isinstance(a["hidden"], bool)
    # Only the ending that gives the whole story away is hidden.
    assert [a["id"] for a in achievements.ACHIEVEMENTS if a["hidden"]] == [
        "the-night-mended"
    ]
    mapped = (
        set(achievements.FACT_ACHIEVEMENTS.values())
        | set(achievements.ENDING_ACHIEVEMENTS.values())
        | {achievements.REMEMBERED, achievements.EVERY_THREAD}
    )
    assert mapped == set(ids)


def test_the_clues_are_every_fact_but_what_an_ending_tells():
    assert len(achievements.CLUES) == 10
    assert facts.THE_ROPE in achievements.CLUES
    assert facts.LOOP_BROKEN not in achievements.CLUES


def test_a_loaded_save_catches_up_and_is_not_changed(scripted, unlocks):
    game, ui = scripted(LOOP_ONE + LOOP_TWO)
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path, encoding="utf-8") as saveFile:
        before = json.load(saveFile)
    del unlocks[:]

    game, ui = scripted(["Load Slot 1", "Quit"])
    game.play()
    assert unlocks == ["in-the-ledger", "first-reset", "ended-by-the-bell"]
    with open(path, encoding="utf-8") as saveFile:
        assert json.load(saveFile) == before


def test_a_broken_loop_from_before_the_second_ending_catches_up_as_the_bell(unlocks):
    meta = MetaState()
    meta.learn(facts.THE_BELL)
    meta.loopBroken = True
    before = meta.toDict()
    achievements.catchUp(meta)
    assert unlocks == ["first-reset", "ended-by-the-bell"]
    assert meta.toDict() == before


def _playAndReadSave(scripted, script):
    game, ui = scripted(script)
    game.play()
    path = game.saveFileManager.get_save_path("save.json")
    with open(path, "rb") as saveFile:
        return saveFile.read()


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_unlocking_never_changes_the_save_or_breaks_the_game(
    scripted, monkeypatch, tmp_path, route
):
    script, _ = ROUTES[route]
    monkeypatch.setattr(achievements.arcade, "unlock", lambda achievementId: None)
    quiet = _playAndReadSave(scripted, script)

    def failing(achievementId):
        raise RuntimeError("the service is down")

    # A fresh data directory, so the second run starts from nothing too.
    monkeypatch.setenv("TIDEWATER_SAVE_DIR", str(tmp_path / "second"))
    monkeypatch.setattr(achievements.arcade, "unlock", failing)
    loud = _playAndReadSave(scripted, script)
    assert loud == quiet
