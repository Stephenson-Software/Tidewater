# @author Daniel McCoy Stephenson
"""The villagers, and what they will say to someone who knows enough.

Every conditional line is gated on a fact, never on the loop number: what
opens a door in Tidewater is what you know, and you can know it in any loop.
Responses that teach something are callables, so the fact is learned when
the line is heard and not when the menu is built.
"""

from tak import NPC

from tidewater import facts
from tidewater.flags import (
    HURRIED_ADA,
    LAMP_LIT,
    ROPE_HUNG,
    SHAMED_GILBERT,
    TOLD_MARGARET_ABOUT_TOM,
    TOLD_TOM_OF_NELL,
)

# What a villager can put in your hands for the day. Loop items: the bell
# forgets them along with everything else you did.
ROPE = "rope"
OIL = "oil"


def sam(game):
    meta = game.meta

    def aboutTheBell():
        game.learn(facts.SAM_BELL)
        return (
            "That? Hasn't rung in thirty years. There's no rope on it - go and "
            "look, the tower's open. Rusted through, I shouldn't wonder."
        )

    def lastNight():
        game.learn(facts.SAM_BELL)
        return (
            "Last night? I was in my bed, and so should you have been. There's "
            "no rope on that bell, friend. Nobody rang anything."
        )

    return NPC(
        "Sam",
        "Sam works the docks - mending nets, minding other people's boats, "
        "and watching the weather with one eye.",
        [
            {
                "question": "How's the fishing?",
                "response": "Same as yesterday. Same as it'll be tomorrow, I'd say.",
            },
            {
                "question": "What about the bell up in the tower?",
                "response": aboutTheBell,
            },
            {
                "question": "Did you hear the bell last night?",
                "response": lastNight,
                "condition": lambda: meta.knows(facts.THE_BELL),
            },
            {
                "question": "Do you know anything about the Marigold?",
                "response": "Before my time. Tom doesn't talk about it, and "
                "you'd not get him to. I'd leave it, if I were you.",
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
        ],
    )


def gilbert(game):
    meta = game.meta

    def aboutTom():
        game.learn(facts.GILBERT_LEDGERS)
        return (
            "Not my story to tell, and I'd not tell it if it were. But I'll say "
            "this: anything that ever happened in this village is written "
            "down at the bank. Margaret keeps every ledger there is, going "
            "back before either of us."
        )

    def undecidedAboutTheOil():
        return (
            meta.knows(facts.THE_OIL)
            and not game.loop.has(OIL)
            and not game.loop.flags.get(LAMP_LIT)
            and SHAMED_GILBERT not in game.loop.flags
        )

    def hisFathersBill():
        game.loop.flags[SHAMED_GILBERT] = True
        game.loop.items.append(OIL)
        return (
            "(He does not answer for a while. When he does it is to the "
            "shelf behind him, not to you.) That's a thing she's never said "
            "to me in thirty years. ... Take it. (A can, full, set on the "
            "counter hard enough to slop.) On the house. And you can tell "
            "her that. Now get out of my shop for today."
        )

    def whateverIsOwed():
        game.loop.flags[SHAMED_GILBERT] = False
        game.loop.items.append(OIL)
        return (
            "(He looks at you, and then out of the window at the point, for "
            "longer than a shopkeeper looks at anything.) Aye. Whatever's "
            "owed. (He fills a can from the barrel himself and wipes it "
            "down before he hands it over.) There's a storm coming tonight, "
            "they say. There always is. Mind how you go up that path."
        )

    def alreadyHasOil():
        if game.loop.flags.get(LAMP_LIT):
            return (
                "It's lit? (He goes to the door and looks up at the point.) So it is."
            )
        return "You've got the can. Go on up before the weather turns."

    return NPC(
        "Gilbert",
        "Gilbert keeps the shop, and the village's gossip along with it.",
        [
            {
                "question": "Anything strange lately?",
                "response": "Strange? It's the same day as ever, this one. "
                "Though Old Tom's in one of his moods - always is, this time "
                "of year.",
            },
            {"question": "What's the matter with Old Tom?", "response": aboutTom},
            {
                "question": "Does the harbour bell ever ring?",
                "response": "Not in my lifetime. Ask Sam, he's down there all day.",
                "condition": lambda: meta.knows(facts.THE_BELL),
            },
            # A choice, not a question: two ways to ask for the oil, and he
            # gives it either way - what differs is what he does with the
            # rest of his day, and what he is doing when the light holds.
            {
                "question": "It was your father's bill that put the lamp out.",
                "response": hisFathersBill,
                "condition": undecidedAboutTheOil,
            },
            {
                "question": "The lamp needs oil tonight, whatever's owed.",
                "response": whateverIsOwed,
                "condition": undecidedAboutTheOil,
            },
            {
                "question": "About the oil.",
                "response": alreadyHasOil,
                "condition": lambda: game.loop.has(OIL)
                or bool(game.loop.flags.get(LAMP_LIT)),
            },
        ],
    )


def margaret(game):
    meta = game.meta

    def theOtherLedgers():
        game.learn(facts.OTHER_BOATS)
        return (
            "Other boats? There are always other boats. (She brings down three "
            "more ledgers and opens them at the ribbons.) The Kestrel, '91. "
            "The Two Sisters, '02. The Provider, '19. Every one of them: "
            "'bell rung', in my father's hand, and his father's. It's the "
            "Marigold's page and no other that says what it says."
        )

    def undecidedAboutTom():
        return (
            meta.knows(facts.MARIGOLD)
            and TOLD_MARGARET_ABOUT_TOM not in game.loop.flags
        )

    def tomShouldSee():
        game.loop.flags[TOLD_MARGARET_ABOUT_TOM] = True
        return (
            "(She keeps her hand on the closed ledger a long while.) Thirty "
            "years, and he has never once asked. ... Perhaps he should. I'll "
            "take it across at closing."
        )

    def nothingToDoWithTom():
        game.loop.flags[TOLD_MARGARET_ABOUT_TOM] = False
        return (
            "No. I suppose it isn't. (She puts the ledger back where it has "
            "been for thirty years.)"
        )

    def theLedger():
        game.learn(facts.MARIGOLD)
        return (
            "The bell. Yes. Give me a moment. ... Here. Thirty years ago this "
            "month: the Marigold, Thomas Reade master, lost in the storm of "
            "the ninth with two hands aboard. And a note in my father's hand: "
            "'Bell not rung. Rope found cut.' Tom's boat, you understand. "
            "Somebody should have called them home, and nobody did."
        )

    return NPC(
        "Margaret",
        "Margaret runs the bank and keeps the village's books - all of them, "
        "going back further than anyone needs.",
        [
            {
                "question": "How's business?",
                "response": "Steady. It's a steady sort of village. Nothing "
                "changes here from one day to the next.",
            },
            {
                "question": "Is there anything in the old books about the harbour bell?",
                "response": theLedger,
                "condition": lambda: meta.knows(facts.SAM_BELL)
                or meta.knows(facts.GILBERT_LEDGERS),
            },
            {
                "question": "Were there other boats?",
                "response": theOtherLedgers,
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
            # A choice, not a question: two alternatives that settle the same
            # flag for the day. Telling her sends her across the road at
            # closing, and Tom has a line for it tonight.
            {
                "question": "Tom should see that page.",
                "response": tomShouldSee,
                "condition": undecidedAboutTom,
            },
            {
                "question": "That page is nothing to do with Tom now.",
                "response": nothingToDoWithTom,
                "condition": undecidedAboutTom,
            },
        ],
    )


def oldTom(game):
    meta = game.meta

    def theMarigold():
        if game.loop.flags.get(ROPE_HUNG):
            return (
                "It's hung? Then there's nothing left but the hour. Be up "
                "there when it comes."
            )
        if game.loop.has(ROPE):
            return (
                "You've got it. Go on, then - before the weather. And ring it "
                "like you mean it."
            )
        game.loop.items.append(ROPE)
        game.learn(facts.THE_ROPE)
        return (
            "... Who told you that name? No. Doesn't matter. Wait there. "
            "(He is gone a long while, down the cellar steps. When he comes "
            "back he has a coil of rope over his shoulder, old and grey and "
            "cut clean at one end.) I kept it. Thirty years. Couldn't hang it "
            "and couldn't throw it out. You take it up the tower. Hang it "
            "before the storm, and when it's eleven, you ring that bell for "
            "them. Somebody should have."
        )

    def undecidedAboutNell():
        return (
            meta.knows(facts.THE_HANDS)
            and (game.loop.has(ROPE) or game.loop.flags.get(ROPE_HUNG))
            and TOLD_TOM_OF_NELL not in game.loop.flags
        )

    def nellsStone():
        game.loop.flags[TOLD_TOM_OF_NELL] = True
        return (
            "(Nothing, for a long time. Then:) Hesketh keeps the moss off it. "
            "I know he does. I've never... Go on. Ring it for her."
        )

    def leaveTheDead():
        game.loop.flags[TOLD_TOM_OF_NELL] = False
        return "(He nods at the door.) Weather's coming. Go on."

    def margaretCameBy():
        return (
            "She did. Closing time, with her coat on, which she never does. "
            "Said someone had been reading. Thirty years that page has sat in "
            "her father's book and she never once brought it across the road. "
            "(He looks at you for the first time.) Well. You've read it. Then "
            "you'd best say the name."
        )

    return NPC(
        "Old Tom",
        "Old Tom keeps the tavern. He was a fisherman once, and does not "
        "speak of it.",
        [
            {
                "question": "A drink, please.",
                "response": "(He pours without looking. The ale is the same "
                "ale as always.)",
            },
            {
                "question": "Margaret came by, I think.",
                "response": margaretCameBy,
                "condition": lambda: bool(game.loop.flags.get(TOLD_MARGARET_ABOUT_TOM)),
            },
            {
                "question": "You were a fisherman?",
                "response": "Was. Don't ask me about it.",
            },
            {
                "question": "I know about the Marigold.",
                "response": theMarigold,
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
            # With the rope over your shoulder and her name in your journal:
            # a choice he holds you to until the bell. Telling him changes
            # what he is doing when it rings.
            {
                "question": "I found Nell's stone.",
                "response": nellsStone,
                "condition": undecidedAboutNell,
            },
            {
                "question": "(Leave the dead alone.)",
                "response": leaveTheDead,
                "condition": undecidedAboutNell,
            },
        ],
    )


def ada(game):
    """The lighthouse keeper. On the docks at dawn, in the lamp room after.

    Her story is the one line in the village that costs patience rather than
    knowledge: the lighthouse scene offers the choice, and a player who
    hurries her gets the short answer and nothing in the journal - until
    the bell forgets she was hurried."""
    meta = game.meta

    def theNight():
        if game.loop.flags.get(HURRIED_ADA):
            return (
                "No. Nobody rang anything. I told you. (She turns back to the "
                "lamp, and that is the end of it for today.)"
            )
        game.learn(facts.KEEPER_SAW)
        return (
            "You know the name, so I'll tell it once. I was in the lamp room. "
            "The glass was going white with the spray and I swung that lamp "
            "till my arms went, and I could see the whole front from up here, "
            "every window. Nobody came out to the tower. Nobody rang "
            "anything. Two of them went in off her bow and I watched it and "
            "there was not a thing I could do but keep the lamp going."
        )

    def howLongItHeld():
        game.learn(facts.THE_OIL)
        return (
            "(She does not stop polishing.) Till nine. It held till nine and "
            "then the oil was done, and I had nothing to feed it. Old Gilbert "
            "had stopped the point's oil that week - a bill, he said, my "
            "father's bill - and I'd a quarter can to my name. I swung it "
            "dry. She came round the point in the dark. (She sets the cloth "
            "down.) His boy keeps the shop now. Never once has he asked me "
            "why I don't buy my oil from him."
        )

    def theLampTonight():
        if game.loop.flags.get(LAMP_LIT):
            return (
                "(She looks at the lamp, and at you, and says nothing for a "
                "long time.) Then we'll see what nine o'clock makes of it."
            )
        return (
            "Bring it up and I'll show you the filler. Before nine, mind. "
            "After nine there's no getting up the path, and no point."
        )

    return NPC(
        "Ada",
        "Ada keeps the light on the point. She has kept it a long time.",
        [
            {
                "question": "Long night?",
                "response": "Every one of them. The lamp doesn't mind the "
                "weather and neither do I, much.",
            },
            {
                "question": "What do you see from up there?",
                "response": "Everything. That's the trouble with a lamp room. "
                "You see everything and you can do nothing about any of it.",
            },
            {
                "question": "You'd have seen the Marigold go down.",
                "response": theNight,
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
            {
                "question": "How long did the lamp hold, that night?",
                "response": howLongItHeld,
                "condition": lambda: meta.knows(facts.KEEPER_SAW)
                and not game.loop.flags.get(HURRIED_ADA),
            },
            {
                "question": "I've a can of oil for the lamp.",
                "response": theLampTonight,
                "condition": lambda: game.loop.has(OIL)
                or bool(game.loop.flags.get(LAMP_LIT)),
            },
        ],
    )


def hesketh(game):
    """The sexton. The churchyard says nothing until you know a name."""
    meta = game.meta

    def theStones():
        game.learn(facts.THE_HANDS)
        return (
            "By the wall, the two with the anchors cut in. Harry Blythe, mate. "
            "Nell Reade, deckhand - nineteen, she was. (He waits for you to "
            "hear it.) Reade. Aye. Tom's girl. He's not stood at that wall in "
            "thirty years, and I keep the moss off it for him."
        )

    return NPC(
        "Hesketh",
        "Hesketh is the sexton. He knows where everyone in the village is, "
        "including the ones who have stopped moving.",
        [
            {
                "question": "Quiet up here.",
                "response": "It is. That's rather the idea.",
            },
            {
                "question": "I'm looking for the Marigold's crew.",
                "response": theStones,
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
        ],
    )
