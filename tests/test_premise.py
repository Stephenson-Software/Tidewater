from tidewater import facts, premise
from tidewater.game import Tidewater
from conftest import FakeGame


def test_a_stranger_knows_only_where_they_are():
    game = FakeGame()
    text = premise.text(game.meta)
    assert text.startswith("WHERE YOU ARE.")
    assert "WHAT IS HAPPENING" not in text
    assert "1 of %d parts" % len(premise.PARAGRAPHS) in text


def test_the_story_grows_with_the_facts_in_plain_words():
    game = FakeGame()
    game.learn(facts.THE_BELL)
    assert "What you have LEARNED lasts" in premise.text(game.meta)
    game.learn(facts.MARIGOLD)
    text = premise.text(game.meta)
    assert "RINGS THE BELL" in text and "KEEPS THE LIGHT" in text
    assert "WHY THE BELL DID NOT RING" not in text
    game.learn(facts.WHO_CUT_THE_ROPE)
    game.learn(facts.WHY_IT_RINGS)
    text = premise.text(game.meta)
    assert "took the bell's and tied his boat up" in text
    assert "A night that was never finished does not end" in text
    assert "the one person in the village who was not here" in text


def test_the_ending_paragraph_is_the_latest_one_and_both_wins():
    game = FakeGame()
    game.learn(facts.LOOP_BROKEN)
    text = premise.text(game.meta)
    assert "You hung the rope" in text and "Both." not in text
    game.learn(facts.THE_LIGHT_HELD)
    text = premise.text(game.meta)
    assert text.count("WHAT YOU DID.") == 1 and "put oil in the lamp" in text
    game.learn(facts.THE_NIGHT_MENDED)
    text = premise.text(game.meta)
    assert text.count("WHAT YOU DID.") == 1 and "Both." in text


def test_every_paragraph_needs_only_real_facts():
    for needed, _ in premise.PARAGRAPHS:
        for f in needed:
            assert f in facts.FACTS, f


def test_the_rope_story_is_told_the_same_way_everywhere():
    # One version of events: the rope was on the deck, so the bell had none.
    for text in (
        facts.text(facts.WHO_CUT_THE_ROPE),
        dict(premise.PARAGRAPHS)[(facts.WHO_CUT_THE_ROPE,)],
    ):
        assert "coiled on her deck" in text
        assert "quay" not in text
