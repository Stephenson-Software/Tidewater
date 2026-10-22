from tidewater import facts, flags
from tidewater import loop as engine
from tidewater.loop import BELL_HOUR, ROPE_HUNG, STORM_HOUR, advance, timetable
from conftest import FakeGame


def test_an_hour_passes_quietly_before_the_storm():
    game = FakeGame()
    outcome = advance(game, 1)
    assert game.loop.hour == 9
    assert outcome.lines == [] and not outcome.reset


def test_the_storm_comes_in_at_nine_and_is_learned_once():
    game = FakeGame()
    outcome = advance(game, STORM_HOUR - 8)
    assert game.loop.hour == STORM_HOUR
    assert game.meta.knows(facts.THE_STORM)
    assert any("storm" in line for line in outcome.lines)
    assert any("learned" in line for line in outcome.lines)
    assert game.loop.newFacts == [facts.THE_STORM]
    assert engine.stormRaging(game.loop.hour)


def test_the_bell_resets_the_day_and_keeps_the_facts():
    game = FakeGame()
    game.loop.items.append("rope")  # carried, not hung: lost with the day
    game.learn(facts.SAM_BELL)
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.reset is True and outcome.ending is None
    assert game.meta.loops == 2
    assert game.meta.knows(facts.THE_BELL)
    assert game.meta.knows(facts.SAM_BELL)
    assert game.loop.hour == 8 and game.loop.items == [] and game.loop.newFacts == []
    joined = "\n".join(outcome.lines)
    assert "This has happened before" in joined
    assert (
        "the bell has no rope" in joined
        and "the bell" in joined
        and "the storm" in joined
    )


def test_the_second_reset_does_not_repeat_the_first_realisation():
    game = FakeGame()
    advance(game, BELL_HOUR - 8)
    outcome = advance(game, BELL_HOUR - 8)
    assert game.meta.loops == 3
    assert "This has happened before" not in "\n".join(outcome.lines)
    assert not any("What you kept" in line for line in outcome.lines)


def test_advancing_past_the_bell_stops_at_the_reset():
    game = FakeGame()
    outcome = advance(game, 40)
    assert outcome.reset and game.loop.hour == 8 and game.meta.loops == 2


def test_a_hung_rope_breaks_the_loop_at_eleven():
    game = FakeGame()
    game.loop.flags[ROPE_HUNG] = True
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.ending == engine.ENDING_BELL
    assert game.meta.loopBroken is True
    assert game.meta.endings == [engine.ENDING_BELL]
    assert game.meta.knows(facts.LOOP_BROKEN)
    assert game.meta.loops == 1  # the loop count stops where it was
    assert "broken the loop" in "\n".join(outcome.lines)


def test_after_the_bell_the_days_are_ordinary():
    game = FakeGame()
    game.meta.loopBroken = True
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.reset and outcome.ending is None
    assert game.meta.days == 1 and game.meta.loops == 1
    assert "1st since the bell" in "\n".join(outcome.lines)
    advance(game, BELL_HOUR - 8)
    assert game.meta.days == 2
    assert game.meta.endings == []


def test_the_timetable_grows_with_what_is_known():
    game = FakeGame()
    hours = [hour for hour, _ in timetable(game.meta)]
    assert STORM_HOUR not in hours and BELL_HOUR not in hours
    game.learn(facts.THE_STORM)
    game.learn(facts.THE_BELL)
    hours = [hour for hour, _ in timetable(game.meta)]
    assert hours == sorted(hours) and STORM_HOUR in hours and BELL_HOUR in hours


def test_opening_hours():
    assert engine.bankOpen(9) and engine.bankOpen(14) and not engine.bankOpen(15)
    assert engine.shopOpen(8) and not engine.shopOpen(18)
    assert not engine.tavernOpen(17) and engine.tavernOpen(18)
    assert engine.samAtDocks(16) and not engine.samAtDocks(17)


def test_the_morning_after_counts_in_ordinals():
    expected = {
        1: "1st",
        2: "2nd",
        3: "3rd",
        4: "4th",
        11: "11th",
        12: "12th",
        13: "13th",
        21: "21st",
        22: "22nd",
        23: "23rd",
        101: "101st",
        111: "111th",
        112: "112th",
    }
    assert {n: engine._ordinal(n) for n in expected} == expected


def test_a_rope_hung_after_the_loop_is_broken_rings_nothing():
    game = FakeGame()
    game.meta.loopBroken = True
    game.meta.endings.append(engine.ENDING_LIGHT)
    game.loop.flags[ROPE_HUNG] = True
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.reset and outcome.ending is None
    assert game.meta.endings == [engine.ENDING_LIGHT]
    assert game.meta.days == 1
    assert not game.meta.knows(facts.LOOP_BROKEN)
    assert "1st since the light" in "\n".join(outcome.lines)


def test_both_halves_done_after_the_loop_is_broken_mend_nothing():
    game = FakeGame()
    game.meta.loopBroken = True
    game.meta.endings.append(engine.ENDING_BELL)
    game.loop.flags[ROPE_HUNG] = True
    game.loop.flags[engine.LAMP_LIT] = True
    outcome = advance(game, STORM_HOUR - 8)
    assert not game.loop.flags.get(flags.LIGHT_HELD)
    assert not game.meta.knows(facts.THE_LIGHT_HELD)
    outcome = advance(game, BELL_HOUR - STORM_HOUR)
    assert outcome.reset and outcome.ending is None
    assert game.meta.endings == [engine.ENDING_BELL]
    assert not game.meta.knows(facts.THE_NIGHT_MENDED)
    assert game.meta.days == 1
