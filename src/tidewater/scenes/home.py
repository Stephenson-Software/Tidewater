# @author Daniel McCoy Stephenson
from tidewater.loop import BELL_HOUR
from tidewater.progression import JOURNAL, isUnlocked
from tidewater.scenes.base import Scene


class Home(Scene):
    id = "home"
    travelTo = ("docks", "shop", "tavern", "bank")

    def descriptor(self):
        return "Home: a bunk, a stove, a window on the harbour. The bed is made, as it is every morning."

    def run(self):
        options, actions, unavailable = [], [], {}
        options.append("Sleep until the bell")
        actions.append(("sleep", None))
        if isUnlocked(self.meta, JOURNAL):
            options.append("Read your journal")
            actions.append(("journal", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "journal":
            return self.go("journal")
        if kind == "sleep":
            self.game.prompt.text = "You sleep."
            outcome = self.game.advance(max(1, BELL_HOUR - self.loop.hour))
        else:
            self.game.prompt.text = "An hour passes."
            outcome = self.game.advance(1)
        if outcome.reset:
            return self.go("docks")
        return self.id
