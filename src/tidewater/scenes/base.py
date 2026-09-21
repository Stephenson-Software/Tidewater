# @author Daniel McCoy Stephenson
from tidewater.loop import stormRaging

STORM_REASON = "the storm's too fierce to reach the docks"

TRAVEL_LABELS = {
    "docks": "Go to the docks",
    "shop": "Go to Gilbert's shop",
    "home": "Go home",
    "tavern": "Go to the tavern",
    "bank": "Go to the bank",
}


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
            if destination == "docks" and stormRaging(self.loop.hour):
                unavailable[len(options)] = STORM_REASON
        options.append("Quit")
        actions.append(("quit", None))

    def choose(self, descriptor, options, actions, unavailable):
        choice = int(self.ui.showOptions(descriptor, options, unavailable))
        return actions[choice - 1]

    def go(self, destination):
        self.loop.location = destination
        self.game.prompt.reset()
        return destination
