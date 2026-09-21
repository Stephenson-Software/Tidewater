# @author Daniel McCoy Stephenson
"""The story, said plainly.

Everything here is also in the facts, the villagers' mouths and the endings -
but scattered, in character, and in the order the player happens to find it.
This is the same story told straight, in the journal, growing as the player
learns: each paragraph is shown once its facts are known, so it never says
more than the player has earned, and never less than they have.

It exists because a playtester finished an ending and said: I got no
answers. The answers were there. They were not in one place, in plain words.
"""

from tidewater import facts

OPENING = (
    "You came in on the coast road yesterday with a rod, no money to speak "
    "of, and no work. A fishing village: docks, a shop, a bank, a tavern, a "
    "lighthouse on the point. Nobody here knows you. You slept on the docks."
    "\n\n"
    "It is the ninth of the month. Somebody said that at the tavern last "
    "night, and the room went quiet, and nobody said why."
)

# (needed facts, paragraph). Shown in order; a paragraph appears once every
# fact it needs is known. The first needs nothing.
PARAGRAPHS = [
    (
        (),
        "WHERE YOU ARE. A fishing village, on the ninth of the month. You "
        "are a stranger with a rod. You know nobody.",
    ),
    (
        (facts.THE_BELL,),
        "WHAT IS HAPPENING TO YOU. At eleven at night a bell rings, and you "
        "wake on the docks at eight in the morning of the same day. Nobody "
        "else notices. Nothing you do lasts - not money, not what you carry, "
        "not where you were standing. What you have LEARNED lasts. That is "
        "the only thing that does, and it is how you will get out.",
    ),
    (
        (facts.SAM_BELL,),
        "THE BELL HAS NO ROPE. Nobody in the village can be ringing it. "
        "Whatever rings at eleven is not a hand.",
    ),
    (
        (facts.MARIGOLD,),
        "WHAT HAPPENED HERE. Thirty years ago tonight - the ninth - a boat "
        "called the Marigold went down in a storm off the point, with two "
        "people lost. When a boat is out in weather, this village does two "
        "things to bring her home: it RINGS THE BELL so she can hear where "
        "the harbour is, and it KEEPS THE LIGHT on the point so she can see "
        "the rocks. That night, neither was done. The ledger says the bell "
        "rope had been cut.",
    ),
    (
        (facts.THE_HANDS,),
        "WHO WAS LOST. Harry Blythe, the mate, and Nell Reade, deckhand. "
        "Reade is Old Tom's name. She was his daughter. Tom was her captain, "
        "and he came home.",
    ),
    (
        (facts.KEEPER_SAW,),
        "THE LIGHT. Ada was in the lamp room that night. Nobody came to "
        "the bell tower, all night. Whatever happened to the rope happened "
        "before the storm.",
    ),
    (
        (facts.THE_OIL,),
        "WHY THE LIGHT WENT OUT. Ada's oil ran dry at nine. Old Gilbert, "
        "who kept the shop then, had cut off the lighthouse's oil that week "
        "over an unpaid bill. Ada swung the lamp until there was nothing to "
        "burn, and the Marigold came round the point in the dark.",
    ),
    (
        (facts.WHO_CUT_THE_ROPE,),
        "WHY THE BELL DID NOT RING. Tom cut the rope himself, weeks before. "
        "His mooring line was rotten and the same shopkeeper would not sell "
        "him rope on credit, so he took the bell's and tied his boat up "
        "with it. It was coiled on her deck the night she went out. So when "
        "the storm came there was nothing on the bell to pull, and nobody "
        "ashore could ring her in - and with the lamp dark she could not see "
        "the point. She struck it. Tom came ashore with the rope and has "
        "kept it thirty years.",
    ),
    (
        (facts.WHY_IT_RINGS,),
        "WHY THE DAY REPEATS. Every boat this village ever lost was called "
        "in with the bell and lit in from the point, and its loss was "
        "written down as done. The Marigold was not. Her night was never "
        "finished - nobody rang, nobody lit, and for thirty years nobody "
        "said so. A night that was never finished does not end. It comes "
        "back round, on its anniversary, to whoever will finish it. This "
        "year that is you: the one person in the village who was not here, "
        "and so the one person who can look at it.",
    ),
    (
        (facts.LOOP_BROKEN,),
        "WHAT YOU DID. You hung the rope and rang the bell at eleven - "
        "called her in, thirty years late. Tom heard it and told you the "
        "truth. That was half of what the night was owed, and it was enough "
        "to let the day end. The light on the point is still dark. The "
        "morning after is real, and ordinary, and the village is as it was.",
    ),
    (
        (facts.THE_LIGHT_HELD,),
        "WHAT YOU DID. You put oil in the lamp and lit it, and it held "
        "through the storm at nine - lit her in, thirty years late. Ada told "
        "you the truth. That was half of what the night was owed, and it was "
        "enough to let the day end. The bell still has no rope. The morning "
        "after is real, and ordinary, and the village is as it was.",
    ),
    (
        (facts.THE_NIGHT_MENDED,),
        "WHAT YOU DID. Both. The light held at nine and the bell rang at "
        "eleven with the beam on the water - everything the village owed the "
        "Marigold, done in one night by the one person who found out what "
        "it was. Tom said it all aloud in the tower. The night of the ninth "
        "is finished. It will not come back.",
    ),
]

# The ending paragraphs replace one another rather than stacking: whichever
# is the latest thing the player did is the one that stands.
ENDING_FACTS = (facts.LOOP_BROKEN, facts.THE_LIGHT_HELD, facts.THE_NIGHT_MENDED)


def text(meta):
    """The story so far, in plain words, for the journal."""
    shown = []
    for needed, paragraph in PARAGRAPHS:
        if all(meta.knows(f) for f in needed):
            shown.append((needed, paragraph))
    # Keep only the last ending paragraph earned (the whole night, if both).
    endings = [p for p in shown if p[0] and p[0][0] in ENDING_FACTS]
    if endings:
        keep = endings[-1]
        if meta.knows(facts.THE_NIGHT_MENDED):
            keep = next(p for p in shown if p[0] == (facts.THE_NIGHT_MENDED,))
        shown = [p for p in shown if p not in endings or p is keep]
    known = sum(1 for p in PARAGRAPHS if all(meta.knows(f) for f in p[0]))
    footer = "\n\n(%d of %d parts of the story known. The rest is in the village.)" % (
        known,
        len(PARAGRAPHS),
    )
    return "\n\n".join(paragraph for _, paragraph in shown) + footer
