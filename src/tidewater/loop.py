# @author Daniel McCoy Stephenson
"""The clock, the day's timetable, and the reset.

Every action a scene offers costs an hour and goes through advance(). The
timetable is fixed - it is the same day every time - and two of its entries
are the whole game: the storm at nine, after which the docks can't be
reached, and the bell at eleven, which ends the day. What the bell does when
it rings depends on whether the rope is hanging.
"""

from tak import formatHour

from tidewater import facts
from tidewater.state import LoopState

STORM_HOUR = 21
BELL_HOUR = 23

# Where people are and when. A scene asks these rather than carrying its own
# copy, so the journal's timetable and the scenes can never disagree.
BANK_OPEN, BANK_CLOSE = 9, 15
SHOP_OPEN, SHOP_CLOSE = 8, 18
TAVERN_OPEN = 18
SAM_LEAVES = 17

ROPE_HUNG = "ropeHung"
ENDING_BELL = "bell"


def bankOpen(hour):
    return BANK_OPEN <= hour < BANK_CLOSE


def shopOpen(hour):
    return SHOP_OPEN <= hour < SHOP_CLOSE


def tavernOpen(hour):
    return hour >= TAVERN_OPEN


def samAtDocks(hour):
    return hour < SAM_LEAVES


def stormRaging(hour):
    return hour >= STORM_HOUR


def timetable(meta):
    """The day as the player knows it, for the journal: (hour, line) pairs.

    Opening hours are common knowledge from the first loop. The storm and the
    bell are listed once they have been lived through."""
    rows = [
        (SHOP_OPEN, "Gilbert opens the shop (until %s)." % formatHour(SHOP_CLOSE)),
        (BANK_OPEN, "Margaret opens the bank (until %s)." % formatHour(BANK_CLOSE)),
        (SAM_LEAVES, "Sam leaves the docks."),
        (TAVERN_OPEN, "Old Tom opens the tavern."),
    ]
    if meta.knows(facts.THE_STORM):
        rows.append(
            (
                STORM_HOUR,
                _witnessed(
                    "The storm comes in. The docks are cut off.", meta, facts.THE_STORM
                ),
            )
        )
    if meta.knows(facts.THE_BELL):
        rows.append(
            (
                BELL_HOUR,
                _witnessed(
                    "The bell rings. The day begins again.", meta, facts.THE_BELL
                ),
            )
        )
    return sorted(rows)


def _witnessed(line, meta, factId):
    """A timetable row the player lived through rather than was told, marked
    with the loop it happened in - the common-knowledge rows carry no mark."""
    loop = meta.learnedIn(factId)
    if loop is None:
        return line
    return "%s (witnessed, loop %d)" % (line, loop)


class Outcome:
    """What an advance() had to say, and whether the day ended.

    lines are shown to the player in order. reset is True when the loop came
    round (the scene should send the player back to the docks); ending is set
    when the bell rang for real."""

    def __init__(self):
        self.lines = []
        self.reset = False
        self.ending = None


def advance(game, hours=1):
    """Move the clock, firing whatever the timetable has for each hour."""
    outcome = Outcome()
    for _ in range(hours):
        game.loop.hour += 1
        hour = game.loop.hour
        if hour == STORM_HOUR:
            outcome.lines.append(
                "The wind turns. Within the hour a storm is coming in off the "
                "water, and the docks are lost behind sheets of rain."
            )
            if game.learn(facts.THE_STORM):
                outcome.lines.append(
                    "[You've learned something. It's in your journal.]"
                )
        if hour >= BELL_HOUR:
            _endDay(game, outcome)
            return outcome
    return outcome


def _endDay(game, outcome):
    meta, loop = game.meta, game.loop
    if loop.flags.get(ROPE_HUNG) and not meta.loopBroken:
        _ringForTheMarigold(game, outcome)
        return
    if meta.loopBroken:
        meta.days += 1
        outcome.lines.append(
            "Night falls, and for once it stays fallen. You sleep. Morning "
            "comes - an ordinary one, the %s since the bell." % _ordinal(meta.days)
        )
        outcome.reset = True
        _newDay(game)
        return

    learned = list(loop.newFacts)
    # Learned before the count moves on: the bell was heard at the end of
    # *this* loop, and the journal records it there.
    firstReset = game.learn(facts.THE_BELL)
    meta.loops += 1
    outcome.lines.append(
        "Eleven o'clock. Out on the water the harbour bell rings - once, "
        "clear and cold - and the sound goes through you like a tide going out."
    )
    outcome.lines.append(
        "You wake on the docks. The boards are dry. The sun is where it was "
        "at eight this morning, because it is eight this morning."
    )
    if firstReset:
        learned.append(facts.THE_BELL)
        outcome.lines.append(
            "This has happened before. You are sure of it. Nobody else is."
        )
    if learned:
        outcome.lines.append(
            "What you kept from that day: "
            + "; ".join(facts.title(f).lower() for f in learned)
            + "."
        )
    outcome.reset = True
    _newDay(game)


def _ringForTheMarigold(game, outcome):
    meta = game.meta
    meta.loopBroken = True
    meta.endings.append(ENDING_BELL)
    game.learn(facts.LOOP_BROKEN)
    outcome.ending = ENDING_BELL
    outcome.lines.append(
        "Eleven o'clock. You take the rope in both hands and pull, and the "
        "harbour bell rings - not once, but again and again, the way it "
        "should have rung thirty years ago, out over the water where the "
        "Marigold went down."
    )
    outcome.lines.append(
        "Lights come on along the front. Old Tom is standing at the tavern "
        "door with his hat off. When the last note has gone out over the "
        "water there is nothing after it but the night, and the night, for "
        "the first time, goes on."
    )
    outcome.lines.append("You have broken the loop. Loop %d was the last." % meta.loops)
    outcome.reset = True
    _newDay(game)


def _newDay(game):
    game.loop = LoopState()


def _ordinal(n):
    suffix = (
        "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )
    return "%d%s" % (n, suffix)
