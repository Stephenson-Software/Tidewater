# @author Daniel McCoy Stephenson
"""What the village shows the player, and when - see tak.progression.

Conditions read the MetaState only: everything that gates a menu in a time
loop is knowledge, and knowledge lives there."""

from tak import Progression

from tidewater import facts

JOURNAL = "journal"
RESOLVE = "resolve"
THE_OTHER_WAY = "the_other_way"

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
    {
        "id": THE_OTHER_WAY,
        "name": "the other way",
        "announcement": "The lamp went out at nine, and the shop opens at "
        "eight. A can of oil is a small thing to carry up a path. It could "
        "be done before the weather.",
        "condition": lambda meta: meta.knows(facts.THE_OIL),
    },
]

progression = Progression(UNLOCKS)


def isUnlocked(meta, featureId):
    return progression.isUnlocked(meta.unlocked, featureId)


def getNextUnlock(meta):
    return progression.getNextUnlock(meta, meta.unlocked)


def catchUp(meta):
    progression.catchUp(meta, meta.unlocked)
