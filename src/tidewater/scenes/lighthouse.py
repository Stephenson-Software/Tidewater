# @author Daniel McCoy Stephenson
from tidewater import facts, villagers
from tidewater.flags import HURRIED_ADA, LAMP_LIT, LIGHT_HELD
from tidewater.loop import (
    KEEPER_LEAVES_DOCKS,
    STORM_HOUR,
    lighthouseOpen,
    stormRaging,
)
from tidewater.scenes.base import Scene


class Lighthouse(Scene):
    """The lamp room on the point. Ada is here from nine until the storm.

    Her story about the night is the village's one line that costs patience:
    ask her straight and she gives you the short answer and nothing more
    today; let her tell it and it takes the hour but goes in the journal."""

    id = "lighthouse"
    travelTo = ("docks", "shop", "home", "tavern", "bank", "churchyard")

    def descriptor(self):
        hour = self.loop.hour
        if stormRaging(hour) and self.loop.flags.get(LIGHT_HELD):
            return (
                "The lamp room in the storm. Spray on the glass, the beam going "
                "round, and below it the front lit all the way to the tower. "
                "Two hours to eleven."
            )
        if lighthouseOpen(hour) and self.loop.flags.get(LAMP_LIT):
            return (
                "The lamp room. The lamp is lit and turning, hours early, and "
                "the brass is warm. Ada is not polishing anything."
            )
        if lighthouseOpen(hour):
            return (
                "The lamp room. Brass, glass, and the whole village laid out "
                "below like a map. Ada is polishing the lens."
            )
        if hour < KEEPER_LEAVES_DOCKS:
            return "The lighthouse. The lamp is out and the door is shut; Ada is down on the front."
        return "The lighthouse, shuttered against the weather."

    def run(self):
        options, actions, unavailable = [], [], {}
        if lighthouseOpen(self.loop.hour):
            options.append("Talk to Ada")
            actions.append(("ada", None))
            if self.meta.knows(facts.MARIGOLD) and not self.loop.flags.get(HURRIED_ADA):
                options.append("Ask about the night the Marigold went down")
                actions.append(("night", None))
            if self.loop.has(villagers.OIL) and not self.loop.flags.get(LAMP_LIT):
                options.append("Fill the lamp and light it")
                actions.append(("light", None))
            if self.loop.flags.get(LAMP_LIT):
                options.append("Wait in the lamp room for nine")
                actions.append(("waitForStorm", None))
        options.append("Look out over the village")
        actions.append(("look", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "ada":
            self.ui.showInteractiveDialogue(villagers.ada(self.game))
        elif kind == "night":
            return self.theNight()
        elif kind == "light":
            self.loop.items.remove(villagers.OIL)
            self.loop.flags[LAMP_LIT] = True
            self.ui.showDialogue(
                "Ada shows you the filler and stands back. The oil goes in "
                "clear and the wick takes on the second match, and the lens "
                "turns it into a bar of light that goes out over the water "
                "and comes round again. It is the middle of the day. Nobody "
                "on the front looks up. Ada does not look away."
            )
        elif kind == "waitForStorm":
            return self.afterHours(max(1, STORM_HOUR - self.loop.hour))
        elif kind == "light":
            self.loop.items.remove(villagers.OIL)
            self.loop.flags[LAMP_LIT] = True
            self.ui.showDialogue(
                "Ada shows you the filler and stands back. The oil goes in "
                "clear and the wick takes on the second match, and the lens "
                "turns it into a bar of light that goes out over the water "
                "and comes round again. It is the middle of the day. Nobody "
                "on the front looks up. Ada does not look away."
            )
        elif kind == "waitForStorm":
            return self.afterHours(max(1, STORM_HOUR - self.loop.hour))
        elif kind == "look":
            self.ui.showDialogue(
                "From here you can see the bell tower at the end of the pier, "
                "the tavern's chimney, the churchyard wall. Whoever kept this "
                "lamp thirty years ago saw all of it too."
            )
        elif kind == "wait":
            self.game.prompt.text = "An hour passes."
        return self.afterHours(1)

    def theNight(self):
        choice = int(
            self.ui.showOptions(
                "Ada stops polishing. 'You want to know about that night,' she "
                "says. 'It's not a short story.'",
                [
                    "Let her tell it in her own time.",
                    "Ask her straight: did anyone ring the bell?",
                ],
            )
        )
        if choice == 1:
            ada = villagers.ada(self.game)
            question = [o["question"] for o in ada.get_dialogue_options()].index(
                "You'd have seen the Marigold go down."
            )
            self.ui.showDialogue("Ada: " + ada.get_dialogue_response(question))
            self.ui.showDialogue("[You've learned something. It's in your journal.]")
            self.loop.flags[HURRIED_ADA] = False
            self.remember("Ada")
            # The whole story takes the hour and the one after it.
            return self.afterHours(2)
        self.ui.showDialogue(
            "Ada: No. Nobody rang anything. (She turns back to the lens.) You "
            "asked, and that's your answer. Don't ask me again today."
        )
        self.loop.flags[HURRIED_ADA] = True
        self.remember("Ada")
        return self.afterHours(1)

    def afterHours(self, hours):
        outcome = self.game.advance(hours)
        if outcome.reset:
            return self.go("docks")
        if stormRaging(self.loop.hour) and not self.loop.flags.get(LAMP_LIT):
            self.ui.showDialogue(
                "Ada shutters the lamp room and sends you down the point ahead "
                "of the weather. Nothing out here can be reached now."
            )
            return self.go("home")
        return self.id
