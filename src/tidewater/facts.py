# @author Daniel McCoy Stephenson
"""Everything the player can come to know.

A fact is the unit of progress in Tidewater. The day resets; facts do not.
Each has a title for the journal and the line the journal shows under it.
Order here is the order the journal lists them in, which is roughly the
order a player is likely to learn them.

Facts also point at each other. A fact's "leads" are the things it hints
can be learned next - each a target fact id and the line the journal shows
while that target is still unknown. The line never names the target; it
says where to look, the way a rumour does. That web is what makes the
journal a map of the village rather than a checklist.
"""

THE_BELL = "the_bell"
THE_STORM = "the_storm"
SAM_BELL = "sam_bell"
GILBERT_LEDGERS = "gilbert_ledgers"
MARIGOLD = "marigold"
THE_ROPE = "the_rope"
LOOP_BROKEN = "loop_broken"
KEEPER_SAW = "keeper_saw"
OTHER_BOATS = "other_boats"
THE_HANDS = "the_hands"

FACTS = {
    THE_BELL: {
        "title": "The bell",
        "text": "At eleven at night the harbour bell rings, and the day begins "
        "again. Nobody else seems to notice. You wake on the docks at eight.",
        "leads": [
            {
                "to": SAM_BELL,
                "text": "Someone who spends all day on the docks would know "
                "about that bell.",
            },
        ],
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
        "leads": [
            {
                "to": MARIGOLD,
                "text": "A bell that has gone thirty years unrung has a reason, "
                "and a village writes its reasons down somewhere.",
            },
        ],
    },
    GILBERT_LEDGERS: {
        "title": "Margaret keeps the ledgers",
        "text": "Gilbert says anything that ever happened in this village is "
        "written down at the bank. Margaret keeps every ledger there is.",
        "leads": [
            {
                "to": MARIGOLD,
                "text": "Margaret's books will say what Gilbert won't. The bank "
                "keeps hours.",
            },
        ],
    },
    MARIGOLD: {
        "title": "The Marigold",
        "text": "From Margaret's ledger: the Marigold, Old Tom's boat, was lost "
        "in a storm thirty years ago with two hands aboard. The bell should "
        "have been rung to call them home. It wasn't - the rope had been cut.",
        "leads": [
            {
                "to": THE_ROPE,
                "text": "Tom's boat. Tom keeps the tavern, and the tavern keeps "
                "late hours. He might have kept something else.",
            },
            {
                "to": KEEPER_SAW,
                "text": "Somebody was awake that night. The lamp on the point "
                "is lit before anyone else is up.",
            },
            {
                "to": THE_HANDS,
                "text": "Two hands aboard. A village puts its names somewhere "
                "the sea can't reach.",
            },
            {
                "to": OTHER_BOATS,
                "text": "One page of a ledger. Margaret has more than one " "ledger.",
            },
        ],
    },
    THE_ROPE: {
        "title": "The rope",
        "text": "Old Tom kept the bell rope all these years. It's his to give, "
        "and he gave it to you. The tower's on the docks - it needs hanging "
        "before the storm, and the bell needs ringing when it's time.",
        "leads": [
            {
                "to": LOOP_BROKEN,
                "text": "Hang it before the storm. Be in the tower when it's "
                "eleven.",
            },
        ],
    },
    LOOP_BROKEN: {
        "title": "The day that ended",
        "text": "You hung the rope, and at eleven the bell rang for the Marigold "
        "at last. The day ended. The next one was new.",
    },
    KEEPER_SAW: {
        "title": "What the keeper saw",
        "text": "Ada keeps the light on the point. The night the Marigold went "
        "down she was in the lamp room and swung the lamp till dawn, and "
        "from up there she could see the whole front. Nobody came to the "
        "tower. Nobody rang anything.",
        "leads": [
            {
                "to": THE_HANDS,
                "text": "Ada saw two go into the water. She won't say their "
                "names. Someone has cut them in stone.",
            },
        ],
    },
    OTHER_BOATS: {
        "title": "The other boats",
        "text": "Margaret's older ledgers: the Kestrel in '91, the Two Sisters "
        "in '02, the Provider in '19 - every boat the village lost, and "
        "beside each one, in the same hand, 'bell rung'. Only the Marigold's "
        "page says otherwise.",
        "leads": [
            {
                "to": THE_HANDS,
                "text": "Every loss in the ledger has names beside it. The "
                "Marigold's two are in the churchyard, if anywhere.",
            },
        ],
    },
    THE_HANDS: {
        "title": "The two hands",
        "text": "Two stones by the churchyard wall, cut the same year: Harry "
        "Blythe, mate, and Nell Reade, deckhand, lost with the Marigold. "
        "Reade. Tom's name. She was his daughter.",
    },
}

# The facts the whole puzzle turns on, in the order they have to be learned.
# The journal marks these so a player who has learned a few knows how far
# there is to go without being told what the rest are.
TRAIL = [THE_BELL, MARIGOLD, THE_ROPE, LOOP_BROKEN]


def title(factId):
    return FACTS[factId]["title"]


def leads(factId):
    """The rumours a fact carries: [(targetFactId, line), ...]."""
    return [(lead["to"], lead["text"]) for lead in FACTS[factId].get("leads", [])]


def text(factId):
    return FACTS[factId]["text"]
