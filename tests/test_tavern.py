"""The tavern, scene by scene: what the door says either side of six, what an
hour by the fire costs, Tom's rope and his choice through the real menu, and
where the storm and the bell leave the player."""

from tidewater import facts, villagers
from tidewater.loop import BELL_HOUR, STORM_HOUR, TAVERN_OPEN
from tidewater.scenes.base import POINT_STORM_REASON, STORM_REASON
from tidewater.scenes.tavern import Tavern
from conftest import FakeGame, ScriptedUI

SETTLED = "[Old Tom will remember that.]"


def atTheTavern(hour, script=()):
    game = FakeGame(ScriptedUI(list(script)))
    game.loop.hour = hour
    game.loop.location = "tavern"
    return game


def labels(ui, index=0):
    return ui.menus[index][1]


def reasonFor(ui, label, index=0):
    _, options, reasons, _ = ui.menus[index]
    return reasons[options.index(label)]


def test_the_shut_tavern_says_when_it_opens_and_has_no_tom():
    game = atTheTavern(TAVERN_OPEN - 1, ["Wait an hour"])
    assert "shut. Old Tom opens at" in Tavern(game).descriptor()
    assert Tavern(game).run() == "tavern"
    assert "Talk to Old Tom" not in labels(game.ui)
    assert "Sit with a drink" not in labels(game.ui)


def test_the_tavern_opens_on_the_hour_with_tom_and_a_seat_by_the_fire():
    game = atTheTavern(TAVERN_OPEN, ["Wait an hour"])
    assert "Old Tom behind the bar" in Tavern(game).descriptor()
    Tavern(game).run()
    assert "Talk to Old Tom" in labels(game.ui)
    assert "Sit with a drink" in labels(game.ui)


def test_sitting_with_a_drink_takes_the_hour_and_teaches_nothing():
    game = atTheTavern(TAVERN_OPEN, ["Sit with a drink"])
    assert Tavern(game).run() == "tavern"
    assert game.loop.hour == TAVERN_OPEN + 1
    assert game.ui.saw("The talk is of weather and prices.")
    assert not game.meta.facts


def test_waiting_passes_an_hour():
    game = atTheTavern(TAVERN_OPEN, ["Wait an hour"])
    assert Tavern(game).run() == "tavern"
    assert game.loop.hour == TAVERN_OPEN + 1
    assert game.prompt.text == "An hour passes."


def test_talking_to_tom_takes_the_hour_whatever_is_said():
    game = atTheTavern(TAVERN_OPEN, ["Talk to Old Tom", "A drink, please.", "[Back]"])
    assert Tavern(game).run() == "tavern"
    assert game.loop.hour == TAVERN_OPEN + 1
    assert game.ui.saw("The ale is the same ale as always.")
    assert not game.ui.saw(SETTLED)


def test_tom_gives_the_rope_once_to_someone_who_knows_the_name():
    game = atTheTavern(
        TAVERN_OPEN, ["Talk to Old Tom", "I know about the Marigold.", "[Back]"]
    )
    game.learn(facts.MARIGOLD)
    Tavern(game).run()
    assert game.loop.items == [villagers.ROPE]
    assert game.meta.knows(facts.THE_ROPE)

    game.ui = ScriptedUI(["Talk to Old Tom", "I know about the Marigold.", "[Back]"])
    Tavern(game).run()
    assert game.loop.items == [villagers.ROPE]
    assert game.ui.saw("You've got it.")


def test_saying_the_stone_shows_the_beat_once_and_the_choice_is_gone():
    game = atTheTavern(
        TAVERN_OPEN, ["Talk to Old Tom", "I found Nell's stone.", "[Back]"]
    )
    game.learn(facts.THE_HANDS)
    game.loop.items.append(villagers.ROPE)
    Tavern(game).run()
    assert game.loop.flags[villagers.TOLD_TOM_OF_NELL] is True
    assert SETTLED in game.ui.dialogues

    game.ui = ScriptedUI(["Talk to Old Tom", "You were a fisherman?", "[Back]"])
    Tavern(game).run()
    assert SETTLED not in game.ui.dialogues
    assert game.ui.saw("Don't ask me about it.")


def test_leaving_the_dead_alone_is_a_choice_he_holds_you_to_as_well():
    game = atTheTavern(
        TAVERN_OPEN, ["Talk to Old Tom", "(Leave the dead alone.)", "[Back]"]
    )
    game.learn(facts.THE_HANDS)
    game.loop.items.append(villagers.ROPE)
    Tavern(game).run()
    assert game.loop.flags[villagers.TOLD_TOM_OF_NELL] is False
    assert SETTLED in game.ui.dialogues


def test_the_storm_cuts_off_the_docks_and_the_point_but_not_the_fire():
    game = atTheTavern(STORM_HOUR, ["Sit with a drink"])
    assert Tavern(game).run() == "tavern"
    assert game.loop.hour == STORM_HOUR + 1
    assert reasonFor(game.ui, "Go to the docks") == STORM_REASON
    assert reasonFor(game.ui, "Walk out to the lighthouse") == POINT_STORM_REASON
    assert reasonFor(game.ui, "Go home") is None


def test_the_bell_takes_you_from_the_tavern_back_to_the_docks():
    game = atTheTavern(BELL_HOUR - 1, ["Sit with a drink"])
    assert Tavern(game).run() == "docks"
    assert game.meta.loops == 2
    assert game.meta.knows(facts.THE_BELL)
    assert game.loop.location == "docks"
    assert game.loop.hour == 8


def test_walking_out_is_free_and_moves_you():
    game = atTheTavern(TAVERN_OPEN, ["Go to the bank"])
    assert Tavern(game).run() == "bank"
    assert game.loop.location == "bank"
    assert game.loop.hour == TAVERN_OPEN


def test_quitting_from_the_tavern_costs_no_time():
    game = atTheTavern(TAVERN_OPEN, ["Quit"])
    assert Tavern(game).run() == "quit"
    assert game.loop.hour == TAVERN_OPEN
