from tidewater import facts, villagers
from conftest import FakeGame


def questions(npc):
    return [o["question"] for o in npc.get_dialogue_options()]


def test_sam_teaches_that_the_bell_has_no_rope():
    game = FakeGame()
    sam = villagers.sam(game)
    assert "Did you hear the bell last night?" not in questions(sam)
    sam.get_dialogue_response(1)
    assert game.meta.knows(facts.SAM_BELL)
    game.learn(facts.THE_BELL)
    assert "Did you hear the bell last night?" in questions(villagers.sam(game))


def test_gilbert_points_to_the_ledgers():
    game = FakeGame()
    gilbert = villagers.gilbert(game)
    gilbert.get_dialogue_response(
        questions(gilbert).index("What's the matter with Old Tom?")
    )
    assert game.meta.knows(facts.GILBERT_LEDGERS)


def test_margaret_only_opens_the_ledger_to_someone_who_asked_around():
    game = FakeGame()
    assert questions(villagers.margaret(game)) == ["How's business?"]
    game.learn(facts.GILBERT_LEDGERS)
    margaret = villagers.margaret(game)
    assert len(questions(margaret)) == 2
    margaret.get_dialogue_response(1)
    assert game.meta.knows(facts.MARIGOLD)


def test_margaret_also_answers_someone_sam_told():
    game = FakeGame()
    game.learn(facts.SAM_BELL)
    assert len(questions(villagers.margaret(game))) == 2


def test_tom_gives_the_rope_once_per_loop_to_someone_who_knows_the_name():
    game = FakeGame()
    assert "I know about the Marigold." not in questions(villagers.oldTom(game))
    game.learn(facts.MARIGOLD)
    tom = villagers.oldTom(game)
    first = tom.get_dialogue_response(
        questions(tom).index("I know about the Marigold.")
    )
    assert "coil of rope" in first
    assert game.loop.items == ["rope"]
    assert game.meta.knows(facts.THE_ROPE)
    again = tom.get_dialogue_response(
        questions(tom).index("I know about the Marigold.")
    )
    assert "You've got it" in again
    assert game.loop.items == ["rope"]


def test_tom_knows_when_the_rope_is_already_hung():
    from tidewater.loop import ROPE_HUNG

    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.loop.flags[ROPE_HUNG] = True
    tom = villagers.oldTom(game)
    line = tom.get_dialogue_response(questions(tom).index("I know about the Marigold."))
    assert "hung" in line and game.loop.items == []
