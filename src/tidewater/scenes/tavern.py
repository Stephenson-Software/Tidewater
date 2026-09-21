# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import villagers
from tidewater.loop import TAVERN_OPEN, tavernOpen
from tidewater.scenes.base import Scene


class Tavern(Scene):
    id = "tavern"
    travelTo = ("docks", "shop", "home", "bank", "lighthouse", "churchyard")

    def descriptor(self):
        if tavernOpen(self.loop.hour):
            return "The tavern. A fire, a few regulars, and Old Tom behind the bar saying nothing."
        return "The tavern, shut. Old Tom opens at %s." % formatHour(TAVERN_OPEN)

    def run(self):
        options, actions, unavailable = [], [], {}
        if tavernOpen(self.loop.hour):
            options.append("Talk to Old Tom")
            actions.append(("tom", None))
            options.append("Sit with a drink")
            actions.append(("drink", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "tom":
            self.talk(villagers.oldTom(self.game), villagers.TOLD_TOM_OF_NELL)
        elif kind == "drink":
            self.ui.showDialogue(
                "You sit by the fire. The talk is of weather and prices. Nobody "
                "mentions the bell, or the Marigold, or anything that happened "
                "more than a week ago."
            )
        elif kind == "wait":
            self.game.prompt.text = "An hour passes."
        outcome = self.game.advance(1)
        if outcome.reset:
            return self.go("docks")
        return self.id
