"""The docks, scene by scene: which rows the pier offers before and after the
rope, what the tower and Ada cost, and where an hour on the front leaves the
player."""

from tidewater import facts, villagers
from tidewater.flags import ROPE_HUNG
from tidewater.loop import BELL_HOUR, KEEPER_LEAVES_DOCKS, SAM_LEAVES, STORM_HOUR
from tidewater.scenes.docks import CATCHES, Docks
from conftest import FakeGame, ScriptedUI


def atTheDocks(hour, script=()):
    game = FakeGame(ScriptedUI(list(script)))
    game.loop.hour = hour
    game.loop.location = "docks"
    return game


def labels(ui, index=0):
    return ui.menus[index][1]


def test_looking_at_the_tower_takes_the_hour_and_shows_the_empty_eye():
    game = atTheDocks(10, ["Look at the bell tower"])
    assert Docks(game).run() == "docks"
    assert game.loop.hour == 11
    assert game.ui.saw("the bell has no rope - just a rusted eye")
    # Looking teaches nothing: the rope is Tom's to give.
    assert not game.meta.facts


def test_talking_to_ada_on_the_front_takes_the_hour_and_she_is_gone_by_nine():
    game = atTheDocks(8, ["Talk to Ada", "Long night?", "[Back]"])
    assert Docks(game).run() == "docks"
    assert game.loop.hour == KEEPER_LEAVES_DOCKS
    assert game.ui.saw("The lamp doesn't mind the weather")
    game.ui = ScriptedUI(["Wait an hour"])
    Docks(game).run()
    assert "Talk to Ada" not in labels(game.ui)


def test_sam_is_on_the_menu_until_he_leaves_the_docks():
    game = atTheDocks(SAM_LEAVES - 1, ["Wait an hour"])
    Docks(game).run()
    assert "Talk to Sam" in labels(game.ui)
    game.ui = ScriptedUI(["Wait an hour"])
    Docks(game).run()
    assert game.loop.hour == SAM_LEAVES + 1
    assert "Talk to Sam" not in labels(game.ui)
    assert "empty but for the gulls" in game.ui.menus[0][0]


def test_the_tower_row_becomes_the_rope_row_and_then_the_wait_for_eleven():
    game = atTheDocks(10, ["Wait an hour"])
    Docks(game).run()
    assert "Look at the bell tower" in labels(game.ui)
    assert "Climb the tower and hang the bell rope" not in labels(game.ui)
    assert "Wait in the tower for eleven" not in labels(game.ui)

    game.loop.items.append(villagers.ROPE)
    game.ui = ScriptedUI(["Climb the tower and hang the bell rope"])
    Docks(game).run()
    assert "Look at the bell tower" not in labels(game.ui)
    assert game.loop.flags[ROPE_HUNG] is True
    assert villagers.ROPE not in game.loop.items
    assert game.ui.saw("the knot holds")

    game.ui = ScriptedUI(["Wait an hour"])
    Docks(game).run()
    assert "Wait in the tower for eleven" in labels(game.ui)
    assert not any("bell tower" in label for label in labels(game.ui))
    assert "Climb the tower and hang the bell rope" not in labels(game.ui)
    assert "rope hangs from the bell, waiting" in game.ui.menus[0][0]


def test_the_storm_drives_a_player_with_no_rope_hung_off_the_pier():
    game = atTheDocks(STORM_HOUR - 1, ["Wait an hour"])
    assert Docks(game).run() == "home"
    assert game.loop.location == "home"
    assert game.ui.saw("Nothing on the docks can be reached now.")


def test_a_hung_rope_keeps_the_player_in_the_tower_through_the_storm():
    game = atTheDocks(STORM_HOUR - 1, ["Wait an hour"])
    game.loop.flags[ROPE_HUNG] = True
    assert Docks(game).run() == "docks"
    assert game.loop.hour == STORM_HOUR
    assert "Rain drives against the shutters" in Docks(game).descriptor()


def test_waiting_in_the_tower_runs_the_clock_to_the_bell_and_out_of_the_loop():
    game = atTheDocks(STORM_HOUR, ["Wait in the tower for eleven"])
    game.loop.flags[ROPE_HUNG] = True
    assert Docks(game).run() == "docks"
    # One row, every hour to eleven, and the bell is rung for real.
    assert game.meta.loopBroken is True
    assert game.meta.endings == ["bell"]
    assert game.meta.loops == 1
    assert game.loop.hour == 8 and not game.loop.flags.get(ROPE_HUNG)
    assert game.ui.saw("You take the rope in both hands and pull")
    assert game.meta.knows(facts.LOOP_BROKEN)


def test_waiting_in_the_tower_from_noon_takes_every_hour_to_eleven():
    game = atTheDocks(12, ["Wait in the tower for eleven"])
    game.loop.flags[ROPE_HUNG] = True
    Docks(game).run()
    # The storm at nine passes with the player in the tower, not sent home.
    assert game.meta.knows(facts.THE_STORM)
    assert game.meta.endings == ["bell"]
    assert not game.ui.saw("driven back up the front")


def test_fishing_takes_the_hour_and_names_the_catch_in_the_prompt():
    game = atTheDocks(10, ["Fish"])
    assert Docks(game).run() == "docks"
    assert game.loop.hour == 11
    assert game.loop.rngDraws == 1
    assert any(catch in game.prompt.text for catch in CATCHES)


def test_quitting_from_the_docks_costs_no_time():
    game = atTheDocks(10, ["Quit"])
    assert Docks(game).run() == "quit"
    assert game.loop.hour == 10
