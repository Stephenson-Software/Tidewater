# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import facts, premise
from tidewater.loop import timetable
from tidewater.scenes.base import Scene


class Journal(Scene):
    """Everything that survives the night, written down. Reading it costs no
    time: it is the player's own memory, laid out."""

    id = "journal"
    travelTo = ()

    def run(self):
        options = [
            "What is happening to you",
            "What you know",
            "The day, as you know it",
            "Close the journal",
        ]
        choice = int(self.ui.showOptions(self.descriptor(), options))
        if choice == 1:
            self.ui.showDialogue(premise.text(self.meta))
            return self.id
        if choice == 2:
            self.ui.showDialogue(self.knownText() + self.leadsText())
            return self.id
        if choice == 3:
            self.ui.showDialogue(self.timetableText())
            return self.id
        return self.go("home")

    def descriptor(self):
        loops = "Loop %d." % self.meta.loops
        if self.meta.loopBroken:
            loops = "The loop is broken. %d loops it took." % self.meta.loops
        trails = "; ".join(
            "%d of %d on the trail of %s"
            % (sum(1 for f in trail if self.meta.knows(f)), len(trail), name)
            for name, trail in facts.TRAILS.items()
        )
        return "%s %d of %d things known. %s." % (
            loops,
            len(self.meta.facts),
            len(facts.FACTS),
            trails,
        )

    def knownText(self):
        if not self.meta.facts:
            return "Nothing yet. Every day is the first."
        lines = []
        for factId in facts.FACTS:  # registry order, not learning order
            if self.meta.knows(factId):
                marker = "*" if any(factId in t for t in facts.TRAILS.values()) else "-"
                loop = self.meta.learnedIn(factId)
                when = "" if loop is None else " - loop %d" % loop
                lines.append(
                    "%s %s%s\n  %s"
                    % (marker, facts.title(factId), when, facts.text(factId))
                )
        lines.append("\n(* marks the trail of the bell, or of the light.)")
        return "\n\n".join(lines)

    def leadsText(self):
        """The rumour web: under what you know, where it points that you
        haven't been. Never names the missing fact - says where to look."""
        lines = []
        for factId in facts.FACTS:
            if not self.meta.knows(factId):
                continue
            for target, text in facts.leads(factId):
                if not self.meta.knows(target) and text not in lines:
                    lines.append(text)
        if not lines:
            return ""
        return "\n\nThere's more to learn:\n" + "\n".join("? " + line for line in lines)

    def timetableText(self):
        rows = [
            "%s  %s" % (formatHour(hour).rjust(8), line)
            for hour, line in timetable(self.meta)
        ]
        return "\n".join(rows)
