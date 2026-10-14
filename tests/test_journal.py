"""The journal: the player's own memory, laid out. Its three pages and the
line at the top, read off the state the way a player would see them."""

from tidewater import facts
from tidewater.scenes.journal import Journal
from conftest import FakeGame, ScriptedUI


def readPage(game, label):
    game.ui = ScriptedUI([label])
    nextScene = Journal(game).run()
    return nextScene, game.ui


# --- the line at the top ----------------------------------------------------


def test_the_descriptor_counts_loops_facts_and_both_trails():
    game = FakeGame()
    game.meta.loops = 3
    game.learn(facts.THE_BELL)
    game.learn(facts.MARIGOLD)
    game.learn(facts.THE_STORM)
    assert Journal(game).descriptor() == (
        "Loop 3. 3 of %d things known. 2 of 4 on the trail of the bell; "
        "2 of 5 on the trail of the light." % len(facts.FACTS)
    )


def test_the_descriptor_says_how_many_loops_it_took_once_broken():
    game = FakeGame()
    game.meta.loops = 4
    game.meta.loopBroken = True
    descriptor = Journal(game).descriptor()
    assert descriptor.startswith("The loop is broken. 4 loops it took. ")
    assert "Loop 4." not in descriptor


# --- what you know ----------------------------------------------------------


def test_an_empty_journal_says_every_day_is_the_first():
    nextScene, ui = readPage(FakeGame(), "What you know")
    assert nextScene == "journal"
    assert ui.dialogues == ["Nothing yet. Every day is the first."]


def test_known_facts_are_listed_in_registry_order_not_learning_order():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.learn(facts.THE_BELL)
    text = Journal(game).knownText()
    assert text.index(facts.title(facts.THE_BELL)) < text.index(
        facts.title(facts.MARIGOLD)
    )


def test_trail_facts_are_starred_and_carry_the_loop_they_were_learned_in():
    game = FakeGame()
    game.learn(facts.THE_BELL)
    game.meta.loops = 2
    game.learn(facts.THE_STORM)
    text = Journal(game).knownText()
    assert "* %s - loop 1\n" % facts.title(facts.THE_BELL) in text
    assert "- %s - loop 2\n" % facts.title(facts.THE_STORM) in text
    assert text.endswith("(* marks the trail of the bell, or of the light.)")


def test_a_fact_from_a_save_without_its_loop_is_listed_unmarked():
    game = FakeGame()
    game.meta.facts = [facts.THE_STORM]  # as fromDict leaves an older save
    entry = "- %s\n  %s" % (facts.title(facts.THE_STORM), facts.text(facts.THE_STORM))
    assert entry in Journal(game).knownText()


def test_the_known_page_shows_the_leads_under_the_facts():
    game = FakeGame()
    game.learn(facts.THE_BELL)
    _, ui = readPage(game, "What you know")
    (page,) = ui.dialogues
    assert page.index(facts.title(facts.THE_BELL)) < page.index(
        "There's more to learn:"
    )


# --- the day, as you know it ------------------------------------------------


def test_the_first_days_timetable_is_opening_hours_in_hour_order():
    nextScene, ui = readPage(FakeGame(), "The day, as you know it")
    assert nextScene == "journal"
    (page,) = ui.dialogues
    rows = page.split("\n")
    assert rows[0] == " 8:00 AM  Gilbert opens the shop (until 6:00 PM)."
    assert rows[-1] == " 6:00 PM  Old Tom opens the tavern."
    assert not any("storm" in row or "bell" in row for row in rows)


def test_the_storm_and_the_bell_join_the_timetable_once_lived_through():
    game = FakeGame()
    game.meta.loops = 2
    game.learn(facts.THE_STORM)
    game.learn(facts.THE_BELL)
    rows = Journal(game).timetableText().split("\n")
    assert rows[-2].startswith(" 9:00 PM  The storm comes in.")
    assert rows[-2].endswith("(witnessed, loop 2)")
    assert rows[-1] == (
        "11:00 PM  The bell rings. The day begins again. (witnessed, loop 2)"
    )


def test_a_storm_from_a_save_without_its_loop_is_timetabled_unmarked():
    game = FakeGame()
    game.meta.facts = [facts.THE_STORM]  # as fromDict leaves an older save
    rows = Journal(game).timetableText().split("\n")
    assert rows[-1] == (
        " 9:00 PM  The storm comes in. The docks and the point are cut off."
    )


def test_closing_the_journal_goes_home():
    game = FakeGame()
    game.loop.location = "journal"
    nextScene, ui = readPage(game, "Close the journal")
    assert nextScene == "home"
    assert game.loop.location == "home"
    assert ui.dialogues == []
