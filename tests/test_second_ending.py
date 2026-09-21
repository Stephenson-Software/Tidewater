"""The second way out of the loop: the light on the point, held through the
storm at nine. And the machinery that lets there be a second way at all -
the flags module and the ENDINGS table."""

import pytest

from tidewater import facts, flags, villagers
from tidewater import loop as engine
from tidewater.header import buildHeader
from tidewater.loop import BELL_HOUR, STORM_HOUR, advance
from tidewater.progression import THE_OTHER_WAY, isUnlocked
from conftest import FakeGame
from test_game import LOOP_ONE, scripted  # noqa: F401 - fixture


def questions(npc):
    return [o["question"] for o in npc.get_dialogue_options()]


# --- the table ------------------------------------------------------------


def test_every_flag_the_game_sets_is_declared_in_one_place():
    import glob
    import os
    import re

    root = os.path.join(os.path.dirname(__file__), "..", "src", "tidewater")
    written = set()
    for path in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
        if path.endswith("flags.py"):
            continue
        source = open(path).read()
        written.update(re.findall(r"flags\[([A-Za-z_.]+)\]", source))
    # Every key written is a constant, never a string literal, and every
    # constant is one the flags module declares.
    for name in written:
        assert not name.startswith(("'", '"')), name
        assert getattr(flags, name.split(".")[-1]) in flags.ALL, name


def test_the_endings_table_is_in_clock_order_with_the_light_first():
    hours = [ending.hour for ending in engine.ENDINGS]
    assert hours == sorted(hours)
    assert engine.ENDINGS[0].id == engine.ENDING_LIGHT
    assert engine.ENDINGS[0].hour == STORM_HOUR
    assert engine.ENDINGS[-1].id == engine.ENDING_BELL
    assert engine.ENDINGS[-1].hour == BELL_HOUR
    assert {e.flag for e in engine.ENDINGS} <= set(flags.ALL)


# --- the engine -----------------------------------------------------------


def test_a_lit_lamp_breaks_the_loop_at_nine():
    game = FakeGame()
    game.loop.flags[flags.LAMP_LIT] = True
    outcome = advance(game, STORM_HOUR - 8)
    assert outcome.ending == engine.ENDING_LIGHT
    assert outcome.reset is True
    assert game.meta.loopBroken is True
    assert game.meta.endings == [engine.ENDING_LIGHT]
    assert game.meta.knows(facts.THE_LIGHT_HELD)
    assert not game.meta.knows(facts.LOOP_BROKEN)
    assert game.loop.hour == 8  # a new day, not the rest of the storm
    joined = "\n".join(outcome.lines)
    assert "does not go out" in joined and "no bell at eleven" in joined
    assert "broken the loop" in joined


def test_the_storm_is_still_lived_through_on_the_way_to_the_light():
    game = FakeGame()
    game.loop.flags[flags.LAMP_LIT] = True
    outcome = advance(game, STORM_HOUR - 8)
    assert game.meta.knows(facts.THE_STORM)
    assert outcome.lines[0].startswith("The wind turns.")


def test_with_both_the_lamp_lit_and_the_rope_hung_the_night_is_mended_at_eleven():
    # The light is not an ending when the rope is hung too: it holds at
    # nine, the loop goes on, and the bell at eleven is the whole of it.
    game = FakeGame()
    game.loop.flags[flags.LAMP_LIT] = True
    game.loop.flags[flags.ROPE_HUNG] = True
    toNine = advance(game, STORM_HOUR - 8)
    assert toNine.ending is None and not toNine.reset
    assert game.loop.flags[flags.LIGHT_HELD] is True
    assert game.meta.knows(facts.THE_LIGHT_HELD)
    assert "The bell is two hours off" in "\n".join(
        toNine.lines
    )  # FakeGame starts on the docks
    toEleven = advance(game, BELL_HOUR - STORM_HOUR)
    assert toEleven.ending == engine.ENDING_BOTH
    assert game.meta.endings == [engine.ENDING_BOTH]
    assert game.meta.knows(facts.THE_NIGHT_MENDED)
    assert game.meta.knows(facts.WHO_CUT_THE_ROPE) and game.meta.knows(
        facts.WHY_IT_RINGS
    )
    assert not game.meta.knows(facts.LOOP_BROKEN)  # that is the half-mended one
    text = "\n".join(toEleven.lines)
    assert "I cut it" in text and "Both done now" in text
    assert engine.endingName(game.meta) == "the bell and the light"
    assert game.loop.flags == {}


def test_each_ending_alone_answers_the_questions_and_says_what_is_left():
    light = FakeGame()
    light.loop.flags[flags.LAMP_LIT] = True
    text = "\n".join(advance(light, STORM_HOUR - 8).lines)
    assert light.meta.knows(facts.WHO_CUT_THE_ROPE) and light.meta.knows(
        facts.WHY_IT_RINGS
    )
    assert "It was Tom" in text and "the not-doing of it" in text
    assert "still standing open" in text

    bell = FakeGame()
    bell.loop.flags[flags.ROPE_HUNG] = True
    text = "\n".join(advance(bell, BELL_HOUR - 8).lines)
    assert bell.meta.knows(facts.WHO_CUT_THE_ROPE) and bell.meta.knows(
        facts.WHY_IT_RINGS
    )
    assert "'I cut it,' he says" in text and "not-doing of it" in text
    assert "still standing open" in text


def test_the_rope_alone_still_rings_the_bell_at_eleven():
    game = FakeGame()
    game.loop.flags[flags.ROPE_HUNG] = True
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.ending == engine.ENDING_BELL
    assert game.meta.endings == [engine.ENDING_BELL]


def test_the_lamp_lit_after_the_loop_is_broken_changes_nothing():
    game = FakeGame()
    game.meta.loopBroken = True
    game.meta.endings.append(engine.ENDING_BELL)
    game.loop.flags[flags.LAMP_LIT] = True
    outcome = advance(game, BELL_HOUR - 8)
    assert outcome.ending is None
    assert game.meta.endings == [engine.ENDING_BELL]
    assert game.meta.days == 1


def test_the_morning_after_names_the_ending():
    game = FakeGame()
    game.meta.loopBroken = True
    game.meta.endings.append(engine.ENDING_LIGHT)
    outcome = advance(game, BELL_HOUR - 8)
    assert "since the light" in "\n".join(outcome.lines)
    game.meta.days = 2
    assert buildHeader(game)["chips"][0] == "Day 3 after the light"
    assert buildHeader(game)["title"] == "Tidewater - Day 3 after the light"


def test_a_broken_loop_with_no_recorded_ending_is_the_bell():
    # Saves from before there was a second ending.
    game = FakeGame()
    game.meta.loopBroken = True
    assert engine.endingName(game.meta) == "the bell"
    assert buildHeader(game)["chips"][0] == "Day 1 after the bell"


def test_the_gilbert_choice_changes_what_he_does_when_the_light_holds():
    shamed = FakeGame()
    shamed.loop.flags[flags.LAMP_LIT] = True
    shamed.loop.flags[flags.SHAMED_GILBERT] = True
    a = "\n".join(advance(shamed, STORM_HOUR - 8).lines)
    spared = FakeGame()
    spared.loop.flags[flags.LAMP_LIT] = True
    spared.loop.flags[flags.SHAMED_GILBERT] = False
    b = "\n".join(advance(spared, STORM_HOUR - 8).lines)
    assert "Gilbert is standing in his doorway" in a
    assert "Gilbert is standing in his doorway" not in b
    assert "Ada" in a and "Ada" in b


# --- the villagers --------------------------------------------------------


def test_ada_tells_how_long_the_lamp_held_only_after_the_night_and_only_if_not_hurried():
    game = FakeGame()
    game.learn(facts.MARIGOLD)
    assert "How long did the lamp hold, that night?" not in questions(
        villagers.ada(game)
    )
    game.learn(facts.KEEPER_SAW)
    ada = villagers.ada(game)
    assert "How long did the lamp hold, that night?" in questions(ada)
    line = ada.get_dialogue_response(
        questions(ada).index("How long did the lamp hold, that night?")
    )
    assert "Till nine" in line and "Gilbert" in line
    assert game.meta.knows(facts.THE_OIL)
    hurried = FakeGame()
    hurried.learn(facts.KEEPER_SAW)
    hurried.loop.flags[flags.HURRIED_ADA] = True
    assert "How long did the lamp hold, that night?" not in questions(
        villagers.ada(hurried)
    )


def test_the_oil_fact_keeps_continuity_with_what_ada_first_said():
    # She swung the lamp till her arms went; what failed was the oil, not her.
    assert "swung" in facts.text(facts.KEEPER_SAW)
    assert "oil was gone" in facts.text(facts.THE_OIL)
    assert "nine" in facts.text(facts.THE_OIL)


def test_gilberts_choice_needs_the_fact_and_gives_the_oil_either_way():
    game = FakeGame()
    gilbert = villagers.gilbert(game)
    assert not any("bill" in q or "oil" in q.lower() for q in questions(gilbert))
    game.learn(facts.THE_OIL)
    gilbert = villagers.gilbert(game)
    assert "It was your father's bill that put the lamp out." in questions(gilbert)
    assert "The lamp needs oil tonight, whatever's owed." in questions(gilbert)
    gilbert.get_dialogue_response(
        questions(gilbert).index("The lamp needs oil tonight, whatever's owed.")
    )
    assert game.loop.items == [villagers.OIL]
    assert game.loop.flags[flags.SHAMED_GILBERT] is False
    # Settled: the pair is gone, the follow-up is there, and no second can.
    again = villagers.gilbert(game)
    assert "It was your father's bill that put the lamp out." not in questions(again)
    assert "About the oil." in questions(again)

    other = FakeGame()
    other.learn(facts.THE_OIL)
    gilbert = villagers.gilbert(other)
    gilbert.get_dialogue_response(
        questions(gilbert).index("It was your father's bill that put the lamp out.")
    )
    assert other.loop.items == [villagers.OIL]
    assert other.loop.flags[flags.SHAMED_GILBERT] is True


def test_the_bell_forgets_the_oil_and_the_lamp():
    game = FakeGame()
    game.learn(facts.THE_OIL)
    game.loop.items.append(villagers.OIL)
    game.loop.flags[flags.SHAMED_GILBERT] = True
    advance(game, BELL_HOUR - 8)  # no lamp lit: an ordinary reset
    assert game.loop.items == [] and game.loop.flags == {}
    assert game.meta.knows(facts.THE_OIL)


def test_the_light_trail_is_connected_by_leads():
    # Same guarantee the bell's trail has: each step is reachable from the one
    # before by following leads, so the journal never strands the player.
    for earlier, later in zip(facts.TRAIL_LIGHT, facts.TRAIL_LIGHT[1:]):
        chain = {earlier}
        frontier = [earlier]
        while frontier:
            here = frontier.pop()
            for target, _ in facts.leads(here):
                if target not in chain:
                    chain.add(target)
                    frontier.append(target)
        assert later in chain, (earlier, later)


def test_the_other_way_is_announced_once_the_oil_is_known():
    game = FakeGame()
    assert not isUnlocked(game.meta, THE_OTHER_WAY)
    from tidewater.progression import getNextUnlock

    game.learn(facts.THE_OIL)
    ids = []
    while True:
        unlock = getNextUnlock(game.meta)
        if unlock is None:
            break
        ids.append(unlock["id"])
    assert THE_OTHER_WAY in ids


# --- the whole thing, played ---------------------------------------------

# From LOOP_ONE's end (Marigold known, storm and bell lived through), the
# light in one day: Ada's whole story (two hours), the question she only
# answers afterwards, the shop, the climb back up, the lamp, and nine o'clock.
LOOP_TWO_THE_LIGHT = [
    "Wait an hour",  # 8 -> 9: Ada goes up to the point
    "Walk out to the lighthouse",
    "Ask about the night the Marigold went down",
    "Let her tell it in her own time.",  # 9 -> 11: KEEPER_SAW
    "Talk to Ada",
    "How long did the lamp hold",
    "[Back]",  # 11 -> 12: THE_OIL
    "Go to Gilbert's shop",
    "Talk to Gilbert",
    "whatever's owed",
    "[Back]",  # 12 -> 13: the oil, and Gilbert will remember that
    "Walk out to the lighthouse",
    "Fill the lamp and light it",  # 13 -> 14
    "Wait in the lamp room for nine",  # -> the storm, and the light holds
    "Quit",
]


def test_the_loop_can_be_broken_by_the_light_in_two_loops(scripted):
    game, ui = scripted(LOOP_ONE + LOOP_TWO_THE_LIGHT)
    game.play()

    assert game.meta.loopBroken is True
    assert game.meta.loops == 2
    assert game.meta.endings == ["light"]
    for fact in (facts.KEEPER_SAW, facts.THE_OIL, facts.THE_LIGHT_HELD):
        assert game.meta.knows(fact), fact
    assert not game.meta.knows(facts.THE_ROPE)
    assert ui.saw("[Gilbert will remember that.]")
    assert ui.saw("[The lamp went out at nine")  # the plan, announced once
    assert ui.saw("does not go out")
    assert ui.saw("no bell at eleven")
    assert ui.cleanedUp
    # The oil was spent on the lamp, and the header said so while carried.
    chips = [[c["text"] for c in h["chips"]] for h in ui.headers]
    assert any("Carrying: a can of lamp oil" in c for c in chips)
    assert chips[-1][0] == "Day 1 after the light"


def test_the_lit_lamp_and_the_hung_rope_together_mend_the_night(scripted):
    # Loop two: light the lamp AND hang the rope; the light holds at nine and
    # the bell at eleven is the whole of it.
    script = (
        LOOP_ONE
        + [
            "Wait an hour",
            "Walk out to the lighthouse",
            "Ask about the night the Marigold went down",
            "Let her tell it in her own time.",
            "Talk to Ada",
            "How long did the lamp hold",
            "[Back]",
            "Go to Gilbert's shop",
            "Talk to Gilbert",
            "father's bill",
            "[Back]",  # -> 13, shamed
            "Walk out to the lighthouse",
            "Fill the lamp and light it",  # -> 14
            "Go home",
        ]
        + ["Wait an hour"] * 4
        + [  # -> 18
            "Go to the tavern",
            "Talk to Old Tom",
            "I know about the Marigold",
            "[Back]",  # -> 19, rope
            "Go to the docks",
            "Climb the tower and hang the bell rope",  # -> 20
            "Wait in the tower for eleven",  # -> nine holds, eleven ends it
            "Quit",
        ]
    )
    game, ui = scripted(script)
    game.play()
    assert game.meta.endings == ["both"]
    assert game.meta.knows(facts.THE_NIGHT_MENDED)
    assert game.meta.knows(facts.WHO_CUT_THE_ROPE) and game.meta.knows(
        facts.WHY_IT_RINGS
    )
    assert not game.meta.knows(facts.LOOP_BROKEN)
    assert ui.saw("up the tower steps where you stand") and ui.saw("Both done now")
    assert [c["text"] for c in ui.headers[-1]["chips"]][
        0
    ] == "Day 1 after the bell and the light"
    lit = [m for m in ui.menus if m[0].startswith("The lamp room. The lamp is lit")]
    assert lit and "Wait in the lamp room for nine" in lit[0][1]


def test_the_journal_counts_both_trails(scripted):
    game, ui = scripted(
        LOOP_ONE
        + ["Go home", "Read your journal", "What you know", "Close the journal", "Quit"]
    )
    game.play()
    journal = [m for m in ui.menus if "on the trail of" in m[0]][0][0]
    assert "on the trail of the bell" in journal
    assert "on the trail of the light" in journal
    assert ui.saw("(* marks the trail of the bell, or of the light.)")


def test_the_held_light_opens_the_way_from_the_lamp_room_to_the_tower(scripted):
    # Light the lamp, hang the rope, then wait in the lamp room for nine:
    # the beam lights the front, the docks are reachable through the storm,
    # and the bell at eleven mends the night.
    script = (
        LOOP_ONE
        + [
            "Wait an hour",
            "Walk out to the lighthouse",
            "Ask about the night the Marigold went down",
            "Let her tell it in her own time.",
            "Talk to Ada",
            "How long did the lamp hold",
            "[Back]",
            "Go to Gilbert's shop",
            "Talk to Gilbert",
            "whatever's owed",
            "[Back]",  # -> 13
            "Go home",
        ]
        + ["Wait an hour"] * 5
        + [  # -> 18
            "Go to the tavern",
            "Talk to Old Tom",
            "I know about the Marigold",
            "[Back]",  # -> 19, rope
            "Go to the docks",
            "Climb the tower and hang the bell rope",  # -> 20
            "Walk out to the lighthouse",
            "Fill the lamp and light it",  # -> 21: the light holds, the night goes on
            "Go to the docks",  # through the storm, by the beam
            "Wait in the tower for eleven",
            "Quit",
        ]
    )
    game, ui = scripted(script)
    game.play()
    assert game.meta.endings == ["both"]
    assert ui.saw("the beam will light you down the point")
    lampRoom = [m for m in ui.menus if m[0].startswith("The lamp room in the storm")]
    assert lampRoom, "the lamp-room-in-the-storm menu was never shown"
    docksRow = lampRoom[0][1].index("Go to the docks")
    assert lampRoom[0][2][docksRow] is None  # reachable, not greyed out
