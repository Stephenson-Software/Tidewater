"""The deeper village (issue #2): the rumour web, the two new villagers and
places, and the choices people remember for a day."""


from tidewater import facts, villagers
from tidewater import loop as engine
from tidewater.loop import KEEPER_LEAVES_DOCKS, STORM_HOUR, timetable
from tidewater.scenes.journal import Journal
from tidewater.scenes.lighthouse import Lighthouse
from conftest import FakeGame, ScriptedUI


def questions(npc):
    return [o["question"] for o in npc.get_dialogue_options()]


def ask(npc, question):
    return npc.get_dialogue_response(questions(npc).index(question))


# --- the rumour web ---------------------------------------------------------


def test_every_lead_points_at_a_real_fact_and_never_names_it():
    for factId, entry in facts.FACTS.items():
        for target, text in facts.leads(factId):
            assert target in facts.FACTS, (factId, target)
            assert target != factId
            assert facts.title(target).lower() not in text.lower(), (factId, target)


def test_the_trail_is_connected_by_leads():
    # Each step of the trail is reachable from the one before by following a
    # lead, so a player reading the journal is never stranded.
    for earlier, later in zip(facts.TRAIL, facts.TRAIL[1:]):
        chain = {earlier}
        frontier = [earlier]
        while frontier:
            here = frontier.pop()
            for target, _ in facts.leads(here):
                if target not in chain:
                    chain.add(target)
                    frontier.append(target)
        assert later in chain, (earlier, later)


def test_the_journal_lists_leads_for_what_you_know_and_drops_them_once_learned():
    game = FakeGame()
    journal = Journal(game)
    assert journal.leadsText() == ""
    game.learn(facts.THE_BELL)
    text = journal.leadsText()
    assert "There's more to learn:" in text
    assert "spends all day on the docks" in text
    game.learn(facts.SAM_BELL)
    text = journal.leadsText()
    assert "spends all day on the docks" not in text
    assert "writes its reasons down" in text


# --- hours and places -------------------------------------------------------


def test_ada_keeps_her_hours_and_the_storm_shuts_the_point():
    assert engine.keeperAtDocks(8) and not engine.keeperAtDocks(KEEPER_LEAVES_DOCKS)
    assert engine.lighthouseOpen(KEEPER_LEAVES_DOCKS) and engine.lighthouseOpen(20)
    assert not engine.lighthouseOpen(STORM_HOUR) and not engine.lighthouseOpen(8)
    rows = timetable(FakeGame().meta)
    assert any(hour == KEEPER_LEAVES_DOCKS and "Ada" in line for hour, line in rows)


def test_the_storm_cuts_off_the_lighthouse_as_well_as_the_docks():
    game = FakeGame()
    game.loop.hour = STORM_HOUR
    game.loop.location = "home"
    from tidewater.scenes.home import Home

    ui = ScriptedUI(["Quit"])
    game.ui = ui
    Home(game).run()
    descriptor, options, reasons, _ = ui.menus[0]
    lighthouse = options.index("Walk out to the lighthouse")
    docks = options.index("Go to the docks")
    assert reasons[lighthouse] and "point" in reasons[lighthouse]
    assert reasons[docks] and "docks" in reasons[docks]


# --- the new villagers ------------------------------------------------------


def test_hesketh_says_nothing_until_you_know_the_name():
    game = FakeGame()
    assert "I'm looking for the Marigold's crew." not in questions(
        villagers.hesketh(game)
    )
    game.learn(facts.MARIGOLD)
    line = ask(villagers.hesketh(game), "I'm looking for the Marigold's crew.")
    assert "Nell Reade" in line
    assert game.meta.knows(facts.THE_HANDS)


def test_margarets_other_ledgers_open_with_the_marigold():
    game = FakeGame()
    assert "Were there other boats?" not in questions(villagers.margaret(game))
    game.learn(facts.MARIGOLD)
    line = ask(villagers.margaret(game), "Were there other boats?")
    assert "Kestrel" in line
    assert game.meta.knows(facts.OTHER_BOATS)


def test_ada_tells_the_night_only_to_someone_who_knows_the_name_and_was_not_hurried():
    game = FakeGame()
    assert "You'd have seen the Marigold go down." not in questions(villagers.ada(game))
    game.learn(facts.MARIGOLD)
    game.loop.flags[villagers.HURRIED_ADA] = True
    line = ask(villagers.ada(game), "You'd have seen the Marigold go down.")
    assert "end of it for today" in line
    assert not game.meta.knows(facts.KEEPER_SAW)
    game.loop.flags[villagers.HURRIED_ADA] = False
    line = ask(villagers.ada(game), "You'd have seen the Marigold go down.")
    assert "lamp room" in line
    assert game.meta.knows(facts.KEEPER_SAW)


# --- choices people remember, for a day ------------------------------------


def test_margarets_choice_is_a_pair_that_settles_once_and_tom_hears_of_it():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    margaret = villagers.margaret(game)
    assert "Tom should see that page." in questions(margaret)
    assert "That page is nothing to do with Tom now." in questions(margaret)
    assert "Margaret came by, I think." not in questions(villagers.oldTom(game))

    ask(margaret, "Tom should see that page.")
    assert game.loop.flags[villagers.TOLD_MARGARET_ABOUT_TOM] is True
    # Settled: neither alternative is offered again today.
    assert "Tom should see that page." not in questions(villagers.margaret(game))
    assert "That page is nothing to do with Tom now." not in questions(
        villagers.margaret(game)
    )
    # And Tom has a line for it tonight.
    line = ask(villagers.oldTom(game), "Margaret came by, I think.")
    assert "Closing time" in line


def test_the_other_alternative_also_settles_it_and_tom_hears_nothing():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    ask(villagers.margaret(game), "That page is nothing to do with Tom now.")
    assert game.loop.flags[villagers.TOLD_MARGARET_ABOUT_TOM] is False
    assert "Tom should see that page." not in questions(villagers.margaret(game))
    assert "Margaret came by, I think." not in questions(villagers.oldTom(game))


def test_the_bell_forgets_a_choice():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    ask(villagers.margaret(game), "Tom should see that page.")
    engine.advance(game, 40)  # to the bell and round again
    assert villagers.TOLD_MARGARET_ABOUT_TOM not in game.loop.flags
    assert "Tom should see that page." in questions(villagers.margaret(game))
    assert game.meta.knows(facts.MARIGOLD)  # what was learned stays


def test_toms_choice_needs_the_name_and_the_rope_and_changes_the_ending():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.learn(facts.THE_HANDS)
    assert "I found Nell's stone." not in questions(villagers.oldTom(game))
    game.loop.items.append(villagers.ROPE)
    tom = villagers.oldTom(game)
    assert "I found Nell's stone." in questions(tom)
    assert "(Leave the dead alone.)" in questions(tom)
    ask(tom, "I found Nell's stone.")
    assert game.loop.flags[villagers.TOLD_TOM_OF_NELL] is True
    game.loop.flags[engine.ROPE_HUNG] = True
    outcome = engine.advance(game, 40)
    assert outcome.ending == engine.ENDING_BELL
    assert "over and over" in "\n".join(outcome.lines)


# --- the beat, through the scenes --------------------------------------------


def test_talking_to_margaret_shows_the_beat_once_a_choice_is_settled():
    from tidewater.scenes.bank import Bank

    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.loop.hour = 10
    ui = ScriptedUI(["Talk to Margaret", "Tom should see that page.", "[Back]"])
    game.ui = ui
    Bank(game).run()
    assert "[Margaret will remember that.]" in ui.dialogues
    # A second conversation with nothing settled shows no beat.
    ui2 = ScriptedUI(["Talk to Margaret", "How's business?", "[Back]"])
    game.ui = ui2
    Bank(game).run()
    assert "[Margaret will remember that.]" not in ui2.dialogues


def test_letting_ada_tell_it_costs_two_hours_and_goes_in_the_journal():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.loop.hour = 10
    game.loop.location = "lighthouse"
    ui = ScriptedUI(["Ask about the night", "Let her tell it"])
    game.ui = ui
    Lighthouse(game).run()
    assert game.meta.knows(facts.KEEPER_SAW)
    assert game.loop.hour == 12
    assert "[Ada will remember that.]" in ui.dialogues


def test_hurrying_ada_costs_one_hour_and_closes_the_subject_for_the_day():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    game.loop.hour = 10
    game.loop.location = "lighthouse"
    ui = ScriptedUI(["Ask about the night", "Ask her straight"])
    game.ui = ui
    assert Lighthouse(game).run() == "lighthouse"
    assert not game.meta.knows(facts.KEEPER_SAW)
    assert game.loop.hour == 11
    assert game.loop.flags[villagers.HURRIED_ADA] is True
    # The row is gone for the rest of the day.
    ui2 = ScriptedUI(["Wait an hour"])
    game.ui = ui2
    Lighthouse(game).run()
    assert not any("Ask about the night" in label for label in ui2.menus[0][1])


def test_the_churchyard_rows_only_read_once_you_know_the_name():
    from tidewater.scenes.churchyard import Churchyard

    game = FakeGame()
    game.loop.location = "churchyard"
    ui = ScriptedUI(["Walk the rows"])
    game.ui = ui
    Churchyard(game).run()
    assert not game.meta.knows(facts.THE_HANDS)
    game.learn(facts.MARIGOLD)
    ui = ScriptedUI(["Walk the rows"])
    game.ui = ui
    Churchyard(game).run()
    assert game.meta.knows(facts.THE_HANDS)
    assert ui.saw("Nell Reade")
