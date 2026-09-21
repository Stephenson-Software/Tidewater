# @author Daniel McCoy Stephenson
from tidewater import facts, villagers
from tidewater.scenes.base import Scene


class Churchyard(Scene):
    """Above the village, open all day. It says nothing until you know a name."""

    id = "churchyard"
    travelTo = ("docks", "shop", "home", "tavern", "bank", "lighthouse")

    def descriptor(self):
        if self.meta.knows(facts.THE_HANDS):
            return (
                "The churchyard. Two stones by the wall with anchors cut in "
                "them, and the moss kept off."
            )
        return (
            "The churchyard, above the village. Rows of names you don't know, "
            "and Hesketh the sexton somewhere among them with a rake."
        )

    def run(self):
        options, actions, unavailable = [], [], {}
        options.append("Talk to Hesketh")
        actions.append(("hesketh", None))
        options.append("Walk the rows")
        actions.append(("rows", None))
        options.append("Wait an hour")
        actions.append(("wait", None))
        self.addTravel(options, actions, unavailable)

        kind, arg = self.choose(self.descriptor(), options, actions, unavailable)
        if kind == "go":
            return self.go(arg)
        if kind == "quit":
            return "quit"
        if kind == "hesketh":
            self.ui.showInteractiveDialogue(villagers.hesketh(self.game))
        elif kind == "rows":
            if self.meta.knows(facts.MARIGOLD):
                self.game.learn(facts.THE_HANDS)
                self.ui.showDialogue(
                    "You go along the wall reading. Most of the names mean "
                    "nothing. Then two together, the same year, with anchors "
                    "cut in: Harry Blythe, mate, and Nell Reade, deckhand, "
                    "lost with the Marigold. Reade. You stand there a while."
                )
                self.ui.showDialogue(
                    "[You've learned something. It's in your journal.]"
                )
            else:
                self.ui.showDialogue(
                    "Rows of names and dates. Fishermen, mostly, and their wives. "
                    "Without a name to look for they are only stones."
                )
        elif kind == "wait":
            self.game.prompt.text = "An hour passes."
        outcome = self.game.advance(1)
        if outcome.reset:
            return self.go("docks")
        return self.id
