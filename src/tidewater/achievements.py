# @author Daniel McCoy Stephenson
"""Achievements on arcade (Stephenson-Software RFC 0014).

Knowledge is the only progression in Tidewater, so the achievements are
mostly facts: learning a few of the important ones, learning every clue the
village holds, and each of the ways out of the loop. One is a moment rather
than a fact: the first time someone will remember a choice.

The ids below are declared in the gateway's config/play/boards.yaml and are
permanent once used: never rename one. Titles and descriptions here are the
declaration's, kept beside the code that unlocks them; the hidden one is
shown as "Hidden achievement" until earned.

Unlocking is fire-and-forget (tak.arcade): a no-op outside the browser, when
the player is not signed in, or off arcade, and it never raises. Nothing here
reads or writes the save file; catchUp() only reads MetaState.
"""

from tak import arcade

from tidewater import facts
from tidewater.loop import ENDING_BELL, ENDING_BOTH, ENDING_LIGHT

FIRST_RESET = "first-reset"
IN_THE_LEDGER = "in-the-ledger"
AWAKE_THAT_NIGHT = "awake-that-night"
NAMES_IN_STONE = "names-in-stone"
REMEMBERED = "remembered"
EVERY_THREAD = "every-thread"
ENDED_BY_THE_BELL = "ended-by-the-bell"
ENDED_BY_THE_LIGHT = "ended-by-the-light"
THE_NIGHT_MENDED = "the-night-mended"

ACHIEVEMENTS = [
    {
        "id": FIRST_RESET,
        "title": "Eight O'Clock Again",
        "description": "Live through the whole day and wake on the docks again",
        "hidden": False,
    },
    {
        "id": IN_THE_LEDGER,
        "title": "In the Ledger",
        "description": "Find what the village wrote down thirty years ago",
        "hidden": False,
    },
    {
        "id": AWAKE_THAT_NIGHT,
        "title": "Awake That Night",
        "description": "Hear from the one who was awake that night",
        "hidden": False,
    },
    {
        "id": NAMES_IN_STONE,
        "title": "Names in Stone",
        "description": "Find the names the sea can't reach",
        "hidden": False,
    },
    {
        "id": REMEMBERED,
        "title": "They'll Remember That",
        "description": "Make a choice someone will hold you to for the day",
        "hidden": False,
    },
    {
        "id": EVERY_THREAD,
        "title": "Every Thread",
        "description": "Learn everything the village can tell you",
        "hidden": False,
    },
    {
        "id": ENDED_BY_THE_BELL,
        "title": "The Bell",
        "description": "Break the loop with the bell",
        "hidden": False,
    },
    {
        "id": ENDED_BY_THE_LIGHT,
        "title": "The Light",
        "description": "Break the loop with the light",
        "hidden": False,
    },
    {
        "id": THE_NIGHT_MENDED,
        "title": "The Night, Mended",
        "description": "Light the lamp and ring the bell on the same night",
        "hidden": True,
    },
]

# Learning one of these facts unlocks the achievement beside it.
FACT_ACHIEVEMENTS = {
    facts.THE_BELL: FIRST_RESET,
    facts.MARIGOLD: IN_THE_LEDGER,
    facts.KEEPER_SAW: AWAKE_THAT_NIGHT,
    facts.THE_HANDS: NAMES_IN_STONE,
}

# Each way out of the loop, by the ending id loop.py records.
ENDING_ACHIEVEMENTS = {
    ENDING_BELL: ENDED_BY_THE_BELL,
    ENDING_LIGHT: ENDED_BY_THE_LIGHT,
    ENDING_BOTH: THE_NIGHT_MENDED,
}

# The facts that are what an ending tells or what it is. A save only ever has
# one ending, so "every fact" is not reachable; every clue the village holds
# before the night is closed is.
ENDING_FACTS = (
    facts.LOOP_BROKEN,
    facts.THE_LIGHT_HELD,
    facts.WHO_CUT_THE_ROPE,
    facts.WHY_IT_RINGS,
    facts.THE_NIGHT_MENDED,
)
CLUES = tuple(f for f in facts.FACTS if f not in ENDING_FACTS)


def unlock(achievementId):
    """Report one unlock. Never raises; the game never waits on it."""
    try:
        arcade.unlock(achievementId)
    except Exception:
        pass


def factLearned(meta, factId):
    """A fact was just learned for the first time."""
    achievementId = FACT_ACHIEVEMENTS.get(factId)
    if achievementId is not None:
        unlock(achievementId)
    if factId in CLUES and all(meta.knows(clue) for clue in CLUES):
        unlock(EVERY_THREAD)


def endingReached(endingId):
    """The loop was just broken this way."""
    achievementId = ENDING_ACHIEVEMENTS.get(endingId)
    if achievementId is not None:
        unlock(achievementId)


def choiceRemembered():
    """Someone will hold the player to a choice for the rest of the day."""
    unlock(REMEMBERED)


def catchUp(meta):
    """Re-report what a loaded save has already earned, for saves made
    before achievements existed or while signed out. Unlocks are idempotent
    on the service. Reads meta; changes nothing."""
    for factId in meta.facts:
        achievementId = FACT_ACHIEVEMENTS.get(factId)
        if achievementId is not None:
            unlock(achievementId)
    if all(meta.knows(clue) for clue in CLUES):
        unlock(EVERY_THREAD)
    endings = list(meta.endings)
    if meta.loopBroken and not endings:
        endings = [ENDING_BELL]  # a save from before the second ending
    for endingId in endings:
        endingReached(endingId)
