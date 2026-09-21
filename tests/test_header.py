from tidewater import facts
from tidewater.header import buildHeader
from tidewater.loop import ROPE_HUNG, STORM_HOUR
from conftest import FakeGame


def chips(game):
    return [c if isinstance(c, dict) else c for c in buildHeader(game)["chips"]]


def test_a_fresh_game():
    game = FakeGame()
    assert buildHeader(game) == {
        "title": "Tidewater - Loop 1",
        "chips": ["Loop 1", "8:00 AM", "The Docks", "Known: 0/%d" % len(facts.FACTS)],
    }


def test_the_storm_is_flagged_in_red():
    game = FakeGame()
    game.loop.hour = STORM_HOUR
    game.loop.location = "home"
    assert {"text": "Storm", "class": "low"} in chips(game)
    assert "Home" in chips(game)


def test_carried_items_and_knowledge_show():
    game = FakeGame()
    game.loop.items.append("rope")
    game.learn(facts.THE_BELL)
    game.learn(facts.MARIGOLD)
    assert "Carrying: the bell rope" in chips(game)
    assert "Known: 2/%d" % len(facts.FACTS) in chips(game)


def test_after_the_bell_the_header_counts_days():
    game = FakeGame()
    game.meta.loopBroken = True
    game.meta.days = 2
    header = buildHeader(game)
    assert header["chips"][0] == "Day 3 after the bell"
    assert header["title"] == "Tidewater - Day 3 after the bell"


def test_an_unknown_location_shows_blank_rather_than_crashing():
    game = FakeGame()
    game.loop.location = "boathouse"
    assert "" in chips(game)
