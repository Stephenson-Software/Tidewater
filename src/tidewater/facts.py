# @author Daniel McCoy Stephenson
"""Everything the player can come to know.

A fact is the unit of progress in Tidewater. The day resets; facts do not.
Each has a title for the journal and the line the journal shows under it.
Order here is the order the journal lists them in, which is roughly the
order a player is likely to learn them.
"""

THE_BELL = "the_bell"
THE_STORM = "the_storm"
SAM_BELL = "sam_bell"
GILBERT_LEDGERS = "gilbert_ledgers"
MARIGOLD = "marigold"
THE_ROPE = "the_rope"
LOOP_BROKEN = "loop_broken"

FACTS = {
    THE_BELL: {
        "title": "The bell",
        "text": "At eleven at night the harbour bell rings, and the day begins "
        "again. Nobody else seems to notice. You wake on the docks at eight.",
    },
    THE_STORM: {
        "title": "The storm",
        "text": "A storm comes in off the water at nine in the evening. The docks "
        "are no place to be after that; nothing on them can be reached until "
        "the bell.",
    },
    SAM_BELL: {
        "title": "The bell has no rope",
        "text": "Sam says the harbour bell hasn't been rung in thirty years - "
        "there's no rope on it. Whatever rings at eleven, it isn't a hand.",
    },
    GILBERT_LEDGERS: {
        "title": "Margaret keeps the ledgers",
        "text": "Gilbert says anything that ever happened in this village is "
        "written down at the bank. Margaret keeps every ledger there is.",
    },
    MARIGOLD: {
        "title": "The Marigold",
        "text": "From Margaret's ledger: the Marigold, Old Tom's boat, was lost "
        "in a storm thirty years ago with two hands aboard. The bell should "
        "have been rung to call them home. It wasn't - the rope had been cut.",
    },
    THE_ROPE: {
        "title": "The rope",
        "text": "Old Tom kept the bell rope all these years. It's his to give, "
        "and he gave it to you. The tower's on the docks - it needs hanging "
        "before the storm, and the bell needs ringing when it's time.",
    },
    LOOP_BROKEN: {
        "title": "The day that ended",
        "text": "You hung the rope, and at eleven the bell rang for the Marigold "
        "at last. The day ended. The next one was new.",
    },
}

# The facts the whole puzzle turns on, in the order they have to be learned.
# The journal marks these so a player who has learned a few knows how far
# there is to go without being told what the rest are.
TRAIL = [THE_BELL, MARIGOLD, THE_ROPE, LOOP_BROKEN]


def title(factId):
    return FACTS[factId]["title"]


def text(factId):
    return FACTS[factId]["text"]
