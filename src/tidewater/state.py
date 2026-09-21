# @author Daniel McCoy Stephenson
"""The two tiers of state a time loop has, and the save file that holds them.

MetaState survives the reset: how many loops there have been, what the
player knows, which parts of the game have been shown, whether the loop has
been broken. LoopState is the current day: the hour, where the player is,
what they are carrying, what has happened *this* time through. The reset
throws LoopState away and builds a fresh one; nothing in it is remembered
unless the game first promoted it to a fact.

The save file is one JSON object holding both, validated against
schemas/save.json on every load and save.
"""

import random

from tidewater import facts

SAVE_VERSION = 1
SAVE_FILENAME = "save.json"
SCHEMA_PATH = "schemas/save.json"

# The world seed. Constant on purpose: the day is the same day every loop, so
# the sea gives up the same fish to the same casts. A player who changes
# nothing sees nothing change - that is what tells them it is a loop.
WORLD_SEED = 1897

START_HOUR = 8
START_LOCATION = "docks"


class MetaState:
    def __init__(self):
        self.loops = 1
        self.facts = []
        # The loop each fact was learned in, by fact id. The only history the
        # model keeps: it is knowledge about knowledge, so it survives the
        # reset like the facts themselves. Absent for facts from saves that
        # predate it.
        self.factLoops = {}
        self.unlocked = []
        self.endings = []
        # Once the bell has been rung the day ends like any other: this
        # counts the ordinary days that follow.
        self.loopBroken = False
        self.days = 0

    def knows(self, factId):
        return factId in self.facts

    def learn(self, factId):
        """Record a fact. Returns True if it was new."""
        if factId not in facts.FACTS:
            raise ValueError("unknown fact %r" % factId)
        if factId in self.facts:
            return False
        self.facts.append(factId)
        self.factLoops[factId] = self.loops
        return True

    def learnedIn(self, factId):
        """The loop a fact was learned in, or None if not known or not recorded."""
        return self.factLoops.get(factId)

    def toDict(self):
        return {
            "loops": self.loops,
            "facts": list(self.facts),
            "factLoops": dict(self.factLoops),
            "unlocked": list(self.unlocked),
            "endings": list(self.endings),
            "loopBroken": self.loopBroken,
            "days": self.days,
        }

    @classmethod
    def fromDict(cls, data):
        meta = cls()
        meta.loops = data["loops"]
        meta.facts = [f for f in data.get("facts", []) if f in facts.FACTS]
        meta.factLoops = {
            f: int(n) for f, n in data.get("factLoops", {}).items() if f in meta.facts
        }
        meta.unlocked = list(data.get("unlocked", []))
        meta.endings = list(data.get("endings", []))
        meta.loopBroken = data.get("loopBroken", False)
        meta.days = data.get("days", 0)
        return meta


class LoopState:
    def __init__(self):
        self.hour = START_HOUR
        self.location = START_LOCATION
        self.items = []
        self.flags = {}
        # Facts learned this loop, for the "what you learned" summary the
        # reset shows. Cleared by the reset along with everything else.
        self.newFacts = []
        # How many draws have been taken from the day's fixed sequence, so a
        # loaded game continues the same day rather than restarting the dice.
        self.rngDraws = 0

    def has(self, item):
        return item in self.items

    def draw(self, choices):
        """One draw from the day's fixed sequence.

        Each draw is a pure function of the world seed and its own index -
        a fresh generator seeded per draw - rather than the next output of one
        long-lived generator. That is what makes a loaded save continue the
        sequence exactly: replaying N draws of a long-lived generator is only
        faithful when every draw consumes the same amount of randomness, and
        random.choice does not (it rejection-samples for populations whose
        size is not a power of two)."""
        rng = random.Random(WORLD_SEED * 1000003 + self.rngDraws)
        self.rngDraws += 1
        return rng.choice(choices)

    def toDict(self):
        return {
            "hour": self.hour,
            "location": self.location,
            "items": list(self.items),
            "flags": dict(self.flags),
            "newFacts": list(self.newFacts),
            "rngDraws": self.rngDraws,
        }

    @classmethod
    def fromDict(cls, data):
        loop = cls()
        loop.hour = data["hour"]
        loop.location = data.get("location", START_LOCATION)
        loop.items = list(data.get("items", []))
        loop.flags = dict(data.get("flags", {}))
        loop.newFacts = list(data.get("newFacts", []))
        loop.rngDraws = data.get("rngDraws", 0)
        return loop


def toSaveDict(meta, loop):
    return {"version": SAVE_VERSION, "meta": meta.toDict(), "loop": loop.toDict()}


def fromSaveDict(data):
    return MetaState.fromDict(data["meta"]), LoopState.fromDict(data["loop"])
