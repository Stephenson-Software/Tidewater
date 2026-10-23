"""The lamp room on the point, scene by scene: what it says at each part of
the day, which rows it offers, and where the storm leaves the player."""

from tidewater import facts, villagers
from tidewater.flags import LAMP_LIT, LIGHT_HELD, ROPE_HUNG
from tidewater.loop import BELL_HOUR, KEEPER_LEAVES_DOCKS, STORM_HOUR
from tidewater.scenes.lighthouse import Lighthouse
from conftest import FakeGame, ScriptedUI


def atTheLighthouse(hour, script=()):
    game = FakeGame(ScriptedUI(list(script)))
    game.loop.hour = hour
    game.loop.location = "lighthouse"
    return game


def labels(ui, index=0):
    return ui.menus[index][1]


def test_before_nine_the_door_is_shut_and_ada_is_not_offered():
    game = atTheLighthouse(8, ["Look out over the village"])
    lighthouse = Lighthouse(game)
    assert "Ada is down on the front" in lighthouse.descriptor()
    lighthouse.run()
    assert not any("Ada" in label for label in labels(game.ui))
    assert not any("Fill the lamp" in label for label in labels(game.ui))


def test_looking_out_takes_the_hour_and_names_what_the_keeper_could_see():
    game = atTheLighthouse(KEEPER_LEAVES_DOCKS, ["Look out over the village"])
    assert Lighthouse(game).run() == "lighthouse"
    assert game.loop.hour == KEEPER_LEAVES_DOCKS + 1
    assert game.ui.saw("the bell tower at the end of the pier")


def test_quitting_from_the_lamp_room_costs_no_time():
    game = atTheLighthouse(10, ["Quit"])
    assert Lighthouse(game).run() == "quit"
    assert game.loop.hour == 10


def test_the_oil_lights_the_lamp_and_offers_the_wait_for_nine():
    game = atTheLighthouse(10, ["Fill the lamp and light it"])
    game.loop.items.append(villagers.OIL)
    Lighthouse(game).run()
    assert game.loop.flags[LAMP_LIT] is True
    assert villagers.OIL not in game.loop.items
    assert "lamp is lit and turning" in Lighthouse(game).descriptor()
    game.ui = ScriptedUI(["Look out over the village"])
    Lighthouse(game).run()
    assert "Wait in the lamp room for nine" in labels(game.ui)
    assert "Fill the lamp and light it" not in labels(game.ui)


def test_the_storm_sends_a_player_with_a_dark_lamp_home():
    game = atTheLighthouse(STORM_HOUR - 1, ["Wait an hour"])
    assert Lighthouse(game).run() == "home"
    assert game.loop.location == "home"
    assert game.ui.saw("Ada shutters the lamp room")


def test_after_nine_the_lamp_room_offers_no_ada_rows_and_no_wait_for_nine():
    game = atTheLighthouse(STORM_HOUR, ["Wait an hour"])
    game.learn(facts.MARIGOLD)
    game.loop.flags[LAMP_LIT] = True
    game.loop.flags[ROPE_HUNG] = True
    game.loop.flags[LIGHT_HELD] = True
    assert Lighthouse(game).run() == "lighthouse"
    assert not any("Ada" in label for label in labels(game.ui))
    assert "Wait in the lamp room for nine" not in labels(game.ui)


def test_the_held_light_counts_down_to_the_bell():
    game = atTheLighthouse(STORM_HOUR)
    game.loop.flags[LAMP_LIT] = True
    game.loop.flags[LIGHT_HELD] = True
    lighthouse = Lighthouse(game)
    assert lighthouse.descriptor().endswith("Two hours to eleven.")
    game.loop.hour = BELL_HOUR - 1
    assert lighthouse.descriptor().endswith("An hour to eleven.")
