# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import facts
from tidewater.loop import timetable
from tidewater.scenes.base import Scene


class Journal(Scene):
    """Everything that survives the night, written down. Reading it costs no
    time: it is the player's own memory, laid out."""

    id = "journal"
    travelTo = ()

    def run(self):
        options = ["What you know", "The day, as you know it", "Close the journal"]
        choice = int(self.ui.showOptions(self.descriptor(), options))
        if choice == 1:
            self.ui.showDialogue(self.knownText())
            return self.id
        if choice == 2:
            self.ui.showDialogue(self.timetableText())
            return self.id
        return self.go("home")

    def descriptor(self):
        onTrail = sum(1 for f in facts.TRAIL if self.meta.knows(f))
        loops = "Loop %d." % self.meta.loops
        if self.meta.loopBroken:
            loops = "The loop is broken. %d loops it took." % self.meta.loops
        return "%s %d of %d things known. %d of %d on the trail of the bell." % (
            loops,
            len(self.meta.facts),
            len(facts.FACTS),
            onTrail,
            len(facts.TRAIL),
        )

    def knownText(self):
        if not self.meta.facts:
            return "Nothing yet. Every day is the first."
        lines = []
        for factId in facts.FACTS:  # registry order, not learning order
            if self.meta.knows(factId):
                marker = "*" if factId in facts.TRAIL else "-"
                lines.append(
                    "%s %s\n  %s" % (marker, facts.title(factId), facts.text(factId))
                )
        lines.append("\n(* marks the trail of the bell.)")
        return "\n\n".join(lines)

    def timetableText(self):
        rows = [
            "%s  %s" % (formatHour(hour).rjust(8), line)
            for hour, line in timetable(self.meta)
        ]
        return "\n".join(rows)
