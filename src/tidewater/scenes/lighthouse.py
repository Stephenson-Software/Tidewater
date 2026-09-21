# @author Daniel McCoy Stephenson
from tidewater import facts, villagers
from tidewater.loop import KEEPER_LEAVES_DOCKS, lighthouseOpen, stormRaging
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
            if self.meta.knows(facts.MARIGOLD) and not self.loop.flags.get(
                villagers.HURRIED_ADA
            ):
                options.append("Ask about the night the Marigold went down")
                actions.append(("night", None))
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
            self.loop.flags[villagers.HURRIED_ADA] = False
            self.remember("Ada")
            # The whole story takes the hour and the one after it.
            return self.afterHours(2)
        self.ui.showDialogue(
            "Ada: No. Nobody rang anything. (She turns back to the lens.) You "
            "asked, and that's your answer. Don't ask me again today."
        )
        self.loop.flags[villagers.HURRIED_ADA] = True
        self.remember("Ada")
        return self.afterHours(1)

    def afterHours(self, hours):
        outcome = self.game.advance(hours)
        if outcome.reset:
            return self.go("docks")
        if stormRaging(self.loop.hour):
            self.ui.showDialogue(
                "Ada shutters the lamp room and sends you down the point ahead "
                "of the weather. Nothing out here can be reached now."
            )
            return self.go("home")
        return self.id
