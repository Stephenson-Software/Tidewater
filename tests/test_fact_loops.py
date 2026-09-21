"""Issue #1: each fact remembers the loop it was learned in."""

import pytest
from jsonschema.exceptions import ValidationError

from tak.saves import validateAgainstSchema

from tidewater import facts
from tidewater import loop as engine
from tidewater.loop import BELL_HOUR, STORM_HOUR, advance, timetable
from tidewater.state import SCHEMA_PATH, LoopState, MetaState, fromSaveDict, toSaveDict
from conftest import FakeGame


def test_a_fact_remembers_the_loop_it_was_learned_in_and_round_trips():
    meta = MetaState()
    meta.learn(facts.SAM_BELL)
    meta.loops = 3
    meta.learn(facts.MARIGOLD)
    meta.learn(facts.SAM_BELL)  # again: the first loop stands
    assert meta.learnedIn(facts.SAM_BELL) == 1
    assert meta.learnedIn(facts.MARIGOLD) == 3
    assert meta.learnedIn(facts.THE_ROPE) is None

    data = toSaveDict(meta, LoopState())
    validateAgainstSchema(data, SCHEMA_PATH)
    assert data["meta"]["factLoops"] == {facts.SAM_BELL: 1, facts.MARIGOLD: 3}
    loaded, _ = fromSaveDict(data)
    assert loaded.factLoops == meta.factLoops


def test_a_save_from_before_the_loops_were_recorded_still_loads():
    data = toSaveDict(MetaState(), LoopState())
    data["meta"]["facts"] = [facts.THE_BELL]
    del data["meta"]["factLoops"]
    validateAgainstSchema(data, SCHEMA_PATH)
    meta, _ = fromSaveDict(data)
    assert meta.knows(facts.THE_BELL)
    assert meta.learnedIn(facts.THE_BELL) is None
    # ...and a recorded loop for a fact no longer known is dropped with it.
    data["meta"]["factLoops"] = {facts.THE_BELL: 2, "retired_fact": 1}
    meta, _ = fromSaveDict(data)
    assert meta.factLoops == {facts.THE_BELL: 2}


def test_schema_rejects_a_loop_number_off_the_count():
    data = toSaveDict(MetaState(), LoopState())
    data["meta"]["factLoops"] = {facts.THE_BELL: 0}
    with pytest.raises(ValidationError):
        validateAgainstSchema(data, SCHEMA_PATH)


def test_the_bell_is_recorded_in_the_loop_it_ended():
    game = FakeGame()
    advance(game, BELL_HOUR - 8)
    assert game.meta.loops == 2
    assert game.meta.learnedIn(facts.THE_STORM) == 1
    assert game.meta.learnedIn(facts.THE_BELL) == 1


def test_the_timetable_marks_the_rows_the_player_witnessed():
    game = FakeGame()
    advance(game, BELL_HOUR - 8)
    game.meta.loops = 4  # a later loop: the mark keeps the loop it happened in
    lines = dict(timetable(game.meta))
    assert lines[STORM_HOUR].endswith("(witnessed, loop 1)")
    assert lines[BELL_HOUR].endswith("(witnessed, loop 1)")
    assert "witnessed" not in lines[engine.TAVERN_OPEN]
