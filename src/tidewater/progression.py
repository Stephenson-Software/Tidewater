# @author Daniel McCoy Stephenson
"""What the village shows the player, and when - see tak.progression.

Conditions read the MetaState only: everything that gates a menu in a time
loop is knowledge, and knowledge lives there."""

from tak import Progression

from tidewater import facts

JOURNAL = "journal"
RESOLVE = "resolve"

UNLOCKS = [
    {
        "id": JOURNAL,
        "name": "your journal",
        "announcement": "You've been through this day before. Things worth "
        "keeping should be written down - there's a journal at home, and "
        "it seems to survive the night.",
        "condition": lambda meta: meta.loops >= 2,
    },
    {
        "id": RESOLVE,
        "name": "a plan",
        "announcement": "You know when the storm comes and you know where the "
        "rope is. Margaret's ledger, Tom's cellar, the tower before nine. It "
        "could all be done in one day.",
        "condition": lambda meta: meta.knows(facts.THE_ROPE),
    },
]

progression = Progression(UNLOCKS)


def isUnlocked(meta, featureId):
    return progression.isUnlocked(meta.unlocked, featureId)


def getNextUnlock(meta):
    return progression.getNextUnlock(meta, meta.unlocked)


def catchUp(meta):
    progression.catchUp(meta, meta.unlocked)
