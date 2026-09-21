import pytest

from tak.saves import validateAgainstSchema

from tidewater import facts
from tidewater.state import (
    SCHEMA_PATH,
    WORLD_SEED,
    LoopState,
    MetaState,
    fromSaveDict,
    toSaveDict,
)


def test_a_new_game_validates_and_round_trips():
    meta, loop = MetaState(), LoopState()
    data = toSaveDict(meta, loop)
    validateAgainstSchema(data, SCHEMA_PATH)
    meta2, loop2 = fromSaveDict(data)
    assert meta2.toDict() == meta.toDict()
    assert loop2.toDict() == loop.toDict()


def test_learn_records_a_fact_once_and_rejects_unknown_ones():
    meta = MetaState()
    assert meta.learn(facts.THE_BELL) is True
    assert meta.learn(facts.THE_BELL) is False
    assert meta.facts == [facts.THE_BELL]
    with pytest.raises(ValueError):
        meta.learn("the_kraken")


def test_unknown_facts_in_a_save_are_dropped_on_load():
    data = toSaveDict(MetaState(), LoopState())
    data["meta"]["facts"] = ["retired_fact", facts.THE_BELL]
    meta, _ = fromSaveDict(data)
    assert meta.facts == [facts.THE_BELL]


def test_the_day_is_the_same_day_every_loop():
    # Same seed, same draws: a player who does the same thing sees the same
    # thing. That is how the loop announces itself without a word.
    a, b = LoopState(), LoopState()
    assert [a.draw(range(100)) for _ in range(8)] == [
        b.draw(range(100)) for _ in range(8)
    ]
    assert a.rngDraws == 8
    assert WORLD_SEED == 1897


@pytest.mark.parametrize("savedAfter", range(0, 40, 3))
def test_a_loaded_day_continues_the_same_sequence(savedAfter):
    # A population of 100 - not a power of two - is the case that broke the
    # first implementation, which replayed a long-lived generator: choice()
    # rejection-samples, so N replayed draws did not consume what the N real
    # draws had. Every save point must continue identically.
    a = LoopState()
    for _ in range(savedAfter):
        a.draw(range(100))
    rest = [a.draw(range(100)) for _ in range(5)]
    b = LoopState.fromDict(toSaveDict(MetaState(), a)["loop"])
    assert b.rngDraws == savedAfter + 5
    a2 = LoopState.fromDict({"hour": 8, "rngDraws": savedAfter})
    assert [a2.draw(range(100)) for _ in range(5)] == rest


def test_schema_rejects_an_hour_off_the_clock():
    from jsonschema.exceptions import ValidationError

    data = toSaveDict(MetaState(), LoopState())
    data["loop"]["hour"] = 24
    with pytest.raises(ValidationError):
        validateAgainstSchema(data, SCHEMA_PATH)
