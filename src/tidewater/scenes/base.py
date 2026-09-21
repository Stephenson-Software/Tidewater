# @author Daniel McCoy Stephenson
from tidewater.flags import LIGHT_HELD
from tidewater.loop import stormRaging

STORM_REASON = "the storm's too fierce to reach the docks"
POINT_STORM_REASON = "the storm's too fierce to reach the point"

TRAVEL_LABELS = {
    "docks": "Go to the docks",
    "shop": "Go to Gilbert's shop",
    "home": "Go home",
    "tavern": "Go to the tavern",
    "bank": "Go to the bank",
    "lighthouse": "Walk out to the lighthouse",
    "churchyard": "Go up to the churchyard",
}

# Places the storm cuts off: the pier and the point beyond it.
STORM_BOUND = {"docks": STORM_REASON, "lighthouse": POINT_STORM_REASON}


class Scene:
    """Shared menu plumbing: a scene builds paired options/actions lists so
    rows can come and go with the player's progress without the numbers
    drifting - see tak's unavailableReasons - and the travel rows are the
    same on every menu."""

    id = ""
    travelTo = ()

    def __init__(self, game):
        self.game = game

    @property
    def ui(self):
        return self.game.ui

    @property
    def meta(self):
        return self.game.meta

    @property
    def loop(self):
        return self.game.loop

    def addTravel(self, options, actions, unavailable):
        for destination in self.travelTo:
            options.append(TRAVEL_LABELS[destination])
            actions.append(("go", destination))
            if destination in STORM_BOUND and stormRaging(self.loop.hour):
                # With the light held on the point the beam lays a road along
                # the front: the docks can be reached through the weather,
                # which is what makes the bell reachable after the lamp.
                if destination == "docks" and self.loop.flags.get(LIGHT_HELD):
                    continue
                unavailable[len(options)] = STORM_BOUND[destination]
        options.append("Quit")
        actions.append(("quit", None))

    def choose(self, descriptor, options, actions, unavailable):
        choice = int(self.ui.showOptions(descriptor, options, unavailable))
        return actions[choice - 1]

    def go(self, destination):
        self.loop.location = destination
        self.game.prompt.reset()
        return destination

    def remember(self, who):
        """The beat after a choice someone will hold you to - until the bell.

        The choice itself sets a flag on the loop, so the reset forgets it
        along with the rest of the day; that is the point. If a choice
        teaches something, that part is promoted to a fact separately."""
        self.ui.showDialogue("[%s will remember that.]" % who)

    def talk(self, npc, choiceFlag=None):
        """Run a conversation; if it settled a choice this loop, say so."""
        decided = choiceFlag in self.loop.flags if choiceFlag else False
        self.ui.showInteractiveDialogue(npc)
        if choiceFlag and not decided and choiceFlag in self.loop.flags:
            self.remember(npc.name)
