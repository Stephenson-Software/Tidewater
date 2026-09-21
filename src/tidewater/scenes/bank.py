# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import villagers
from tidewater.loop import BANK_CLOSE, BANK_OPEN, bankOpen
from tidewater.scenes.base import Scene


class Bank(Scene):
    id = "bank"
    travelTo = ("docks", "shop", "home", "tavern")

    def descriptor(self):
        if bankOpen(self.loop.hour):
            return "The bank. Margaret sits behind the counter with a ledger open in front of her."
        return "The bank, closed. Margaret keeps hours from %s to %s." % (
            formatHour(BANK_OPEN),
            formatHour(BANK_CLOSE),
        )

    def run(self):
        options, actions, unavailable = [], [], {}
        if bankOpen(self.loop.hour):
            options.append("Talk to Margaret")
            actions.append(("margaret", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "margaret":
            self.ui.showInteractiveDialogue(villagers.margaret(self.game))
        elif kind == "wait":
            self.game.prompt.text = "An hour passes."
        outcome = self.game.advance(1)
        if outcome.reset:
            return self.go("docks")
        return self.id
