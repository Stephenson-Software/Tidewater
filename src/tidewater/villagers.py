# @author Daniel McCoy Stephenson
"""The four villagers, and what they will say to someone who knows enough.

Every conditional line is gated on a fact, never on the loop number: what
opens a door in Tidewater is what you know, and you can know it in any loop.
Responses that teach something are callables, so the fact is learned when
the line is heard and not when the menu is built.
"""

from tak import NPC

from tidewater.loop import ROPE_HUNG

from tidewater import facts

ROPE = "rope"


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
        ],
    )


def margaret(game):
    meta = game.meta

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
                "question": "You were a fisherman?",
                "response": "Was. Don't ask me about it.",
            },
            {
                "question": "I know about the Marigold.",
                "response": theMarigold,
                "condition": lambda: meta.knows(facts.MARIGOLD),
            },
        ],
    )
