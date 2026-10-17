from tidewater import facts
from tidewater.progression import (
    JOURNAL,
    RESOLVE,
    THE_OTHER_WAY,
    catchUp,
    getNextUnlock,
    isUnlocked,
)
from conftest import FakeGame


def drain(meta):
    """Every unlock getNextUnlock hands out, one call at a time."""
    ids = []
    while True:
        unlock = getNextUnlock(meta)
        if unlock is None:
            return ids
        ids.append(unlock["id"])


def test_a_fresh_game_has_nothing_to_announce():
    game = FakeGame()
    assert getNextUnlock(game.meta) is None
    assert game.meta.unlocked == []


def test_the_journal_is_announced_on_the_second_loop():
    game = FakeGame()
    game.meta.loops = 2
    unlock = getNextUnlock(game.meta)
    assert unlock["id"] == JOURNAL
    assert "journal at home" in unlock["announcement"]
    assert isUnlocked(game.meta, JOURNAL)


def test_knowing_where_the_rope_is_makes_a_plan():
    game = FakeGame()
    game.learn(facts.THE_ROPE)
    assert drain(game.meta) == [RESOLVE]
    assert isUnlocked(game.meta, RESOLVE)
    assert not isUnlocked(game.meta, JOURNAL)


def test_unlocks_arrive_one_per_call_in_table_order():
    game = FakeGame()
    game.meta.loops = 2
    game.learn(facts.THE_ROPE)
    game.learn(facts.THE_OIL)
    assert getNextUnlock(game.meta)["id"] == JOURNAL
    assert game.meta.unlocked == [JOURNAL]
    assert drain(game.meta) == [RESOLVE, THE_OTHER_WAY]


def test_an_unlock_is_announced_once():
    game = FakeGame()
    game.meta.loops = 2
    assert drain(game.meta) == [JOURNAL]
    game.meta.loops = 3
    assert getNextUnlock(game.meta) is None


def test_catch_up_grants_everything_earned_and_leaves_nothing_to_announce():
    game = FakeGame()
    game.meta.loops = 4
    game.learn(facts.THE_ROPE)
    catchUp(game.meta)
    assert game.meta.unlocked == [JOURNAL, RESOLVE]
    assert getNextUnlock(game.meta) is None
    assert not isUnlocked(game.meta, THE_OTHER_WAY)


def test_unlocks_survive_the_save_file():
    from tidewater.state import MetaState

    game = FakeGame()
    game.meta.loops = 2
    catchUp(game.meta)
    restored = MetaState.fromDict(game.meta.toDict())
    assert isUnlocked(restored, JOURNAL)
    assert getNextUnlock(restored) is None
