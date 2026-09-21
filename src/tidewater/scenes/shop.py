# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import villagers
from tidewater.loop import SHOP_OPEN, shopOpen
from tidewater.scenes.base import Scene


class Shop(Scene):
    id = "shop"
    travelTo = ("docks", "home", "tavern", "bank", "lighthouse", "churchyard")

    def descriptor(self):
        if shopOpen(self.loop.hour):
            return (
                "Gilbert's shop: rope, hooks, lamp oil, and Gilbert behind the counter."
            )
        return "Gilbert's shop, shuttered. He opens at %s." % formatHour(SHOP_OPEN)

    def run(self):
        options, actions, unavailable = [], [], {}
        if shopOpen(self.loop.hour):
            options.append("Talk to Gilbert")
            actions.append(("gilbert", None))
            options.append("Look around")
            actions.append(("browse", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "gilbert":
            self.talk(villagers.gilbert(self.game), villagers.SHAMED_GILBERT)
        elif kind == "browse":
            self.ui.showDialogue(
                "Rope by the fathom, hooks by the dozen, a barrel of salt. "
                "Nothing here you need and nothing you can afford."
            )
        elif kind == "wait":
            self.game.prompt.text = "An hour passes."
        outcome = self.game.advance(1)
        if outcome.reset:
            return self.go("docks")
        return self.id
