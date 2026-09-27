# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import facts, villagers
from tidewater.flags import ROPE_HUNG
from tidewater.loop import BELL_HOUR, keeperAtDocks, samAtDocks, stormRaging
from tidewater.scenes.base import Scene

CATCHES = [
    "a fat mackerel",
    "a minnow, thrown back",
    "nothing at all",
    "a flounder",
    "a boot",
    "two herring on one hook",
    "a crab that would not let go",
    "a sea bass, the best of the day",
]


class Docks(Scene):
    id = "docks"
    travelTo = ("shop", "home", "tavern", "bank", "lighthouse", "churchyard")

    def descriptor(self):
        hour = self.loop.hour
        if self.loop.flags.get(ROPE_HUNG):
            if stormRaging(hour):
                return (
                    "The bell tower. Rain drives against the shutters and the "
                    "rope sways in your hands. It's %s." % formatHour(hour)
                )
            return "The docks. Up in the tower the rope hangs from the bell, waiting."
        # Knowledge, not the loop counter, decides the morning: the bell is
        # the fact the first reset leaves behind, and "Again." belongs to
        # someone who has heard it.
        if hour == 8 and not self.meta.knows(facts.THE_BELL):
            return (
                "You wake on the docks with a rod beside you and the whole sea in "
                "front of you. It's eight in the morning."
            )
        if hour == 8:
            return "The docks, eight in the morning. Again."
        if keeperAtDocks(hour):
            return (
                "The docks. Sam is at the nets, and Ada from the lighthouse is "
                "walking the front with the lamp's oil can, as she does at dawn."
            )
        if samAtDocks(hour):
            return "The docks. Sam is at the nets. The bell tower stands at the end of the pier."
        return "The docks, empty but for the gulls. The bell tower stands at the end of the pier."

    def run(self):
        options, actions, unavailable = [], [], {}
        options.append("Fish")
        actions.append(("fish", None))
        if samAtDocks(self.loop.hour):
            options.append("Talk to Sam")
            actions.append(("sam", None))
        if keeperAtDocks(self.loop.hour):
            options.append("Talk to Ada")
            actions.append(("ada", None))
        if self.loop.has(villagers.ROPE) and not self.loop.flags.get(ROPE_HUNG):
            options.append("Climb the tower and hang the bell rope")
            actions.append(("hang", None))
        elif not self.loop.flags.get(ROPE_HUNG):
            options.append("Look at the bell tower")
            actions.append(("tower", None))
        if self.loop.flags.get(ROPE_HUNG):
            options.append("Wait in the tower for eleven")
            actions.append(("waitForBell", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "fish":
            catch = self.loop.draw(CATCHES)
            self.game.prompt.text = "An hour on the water brings up %s." % catch
            return self.afterHour()
        if kind == "sam":
            self.ui.showInteractiveDialogue(villagers.sam(self.game))
            return self.afterHour()
        if kind == "ada":
            self.ui.showInteractiveDialogue(villagers.ada(self.game))
            return self.afterHour()
        if kind == "tower":
            self.ui.showDialogue(
                "The tower at the end of the pier is open to the weather. Steps "
                "wind up to the bell, and the bell has no rope - just a rusted "
                "eye where one used to hang."
            )
            return self.afterHour()
        if kind == "hang":
            self.loop.flags[ROPE_HUNG] = True
            self.loop.items.remove(villagers.ROPE)
            self.ui.showDialogue(
                "You climb the tower with the rope over your shoulder. The eye "
                "takes it; the knot holds. When you let go the rope hangs "
                "straight and still, and the bell above it waits."
            )
            return self.afterHour()
        if kind == "waitForBell":
            return self.afterHours(max(1, BELL_HOUR - self.loop.hour))
        if kind == "wait":
            self.game.prompt.text = "An hour passes."
            return self.afterHour()
        return self.id

    def afterHour(self):
        return self.afterHours(1)

    def afterHours(self, hours):
        outcome = self.game.advance(hours)
        if outcome.reset:
            return self.go("docks")
        if stormRaging(self.loop.hour) and not self.loop.flags.get(ROPE_HUNG):
            # Driven off the pier: the storm scene puts the player back among
            # the houses, and the docks stay out of reach until the bell.
            self.ui.showDialogue(
                "You are driven back up the front by the rain to the shelter of "
                "the houses. Nothing on the docks can be reached now."
            )
            return self.go("home")
        return self.id
