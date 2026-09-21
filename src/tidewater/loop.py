# @author Daniel McCoy Stephenson
"""The clock, the day's timetable, the endings, and the reset.

Every action a scene offers costs an hour and goes through advance(). The
timetable is fixed - it is the same day every time - and two of its entries
are the whole game: the storm at nine, after which the docks can't be
reached, and the bell at eleven, which ends the day. What an hour does when
it comes depends on what the player has done to the village by then: the
ENDINGS table below is the whole of that, one row per way out of the loop,
and the clock consults it rather than any scene deciding for itself.
"""

from tak import formatHour

from tidewater import facts, flags
from tidewater.state import LoopState

STORM_HOUR = 21
BELL_HOUR = 23

# Where people are and when. A scene asks these rather than carrying its own
# copy, so the journal's timetable and the scenes can never disagree.
BANK_OPEN, BANK_CLOSE = 9, 15
SHOP_OPEN, SHOP_CLOSE = 8, 18
TAVERN_OPEN = 18
SAM_LEAVES = 17
# Ada douses the lamp at dawn, walks the front, and is back up the point by
# nine; the lamp room is hers until the storm shuts the pier.
KEEPER_LEAVES_DOCKS = 9

# Kept importable from here; the flag itself lives in tidewater.flags.
ROPE_HUNG = flags.ROPE_HUNG
LAMP_LIT = flags.LAMP_LIT

ENDING_BELL = "bell"
ENDING_LIGHT = "light"
ENDING_BOTH = "both"

# What each ending is called the morning after, in the header and the day
# report: "Day 3 after the bell", "the 2nd since the light".
ENDING_NAMES = {
    ENDING_BELL: "the bell",
    ENDING_LIGHT: "the light",
    ENDING_BOTH: "the bell and the light",
}


def endingName(meta):
    """What broke the loop, for the morning after. A save that says the loop
    is broken but records no ending predates the second one: it was the bell."""
    if not meta.endings:
        return ENDING_NAMES[ENDING_BELL]
    return ENDING_NAMES[meta.endings[-1]]


def bankOpen(hour):
    return BANK_OPEN <= hour < BANK_CLOSE


def shopOpen(hour):
    return SHOP_OPEN <= hour < SHOP_CLOSE


def tavernOpen(hour):
    return hour >= TAVERN_OPEN


def samAtDocks(hour):
    return hour < SAM_LEAVES


def keeperAtDocks(hour):
    return hour < KEEPER_LEAVES_DOCKS


def lighthouseOpen(hour):
    return KEEPER_LEAVES_DOCKS <= hour < STORM_HOUR


def stormRaging(hour):
    return hour >= STORM_HOUR


def timetable(meta):
    """The day as the player knows it, for the journal: (hour, line) pairs.

    Opening hours are common knowledge from the first loop. The storm and the
    bell are listed once they have been lived through."""
    rows = [
        (SHOP_OPEN, "Gilbert opens the shop (until %s)." % formatHour(SHOP_CLOSE)),
        (BANK_OPEN, "Margaret opens the bank (until %s)." % formatHour(BANK_CLOSE)),
        (KEEPER_LEAVES_DOCKS, "Ada goes back up to the lighthouse."),
        (SAM_LEAVES, "Sam leaves the docks."),
        (TAVERN_OPEN, "Old Tom opens the tavern."),
    ]
    if meta.knows(facts.THE_STORM):
        rows.append(
            (
                STORM_HOUR,
                _witnessed(
                    "The storm comes in. The docks and the point are cut off.",
                    meta,
                    facts.THE_STORM,
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
    """Move the clock, firing whatever the timetable has for each hour.

    Each hour is checked against ENDINGS first: an ending whose hour this is
    and whose flag the player has set fires, ends the day, and nothing later
    in the hour (or the day) runs. Then the storm, then - at the bell hour -
    the ordinary reset."""
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
            if _lightHoldsButTheNightGoesOn(game):
                _theLightHolds(game, outcome)
        ending = _endingDue(game, hour)
        if ending is not None:
            ending.handler(game, outcome)
            return outcome
        if hour >= BELL_HOUR:
            _endDay(game, outcome)
            return outcome
    return outcome


class Ending:
    """One way out of the loop: at ``hour``, if ``flag`` is set on the loop
    (and ``unless``, another flag, is not), ``handler`` breaks the loop and
    records an id on MetaState.endings."""

    def __init__(self, hour, flag, id, handler, unless=None):
        self.hour = hour
        self.flag = flag
        self.id = id
        self.handler = handler
        self.unless = unless


def _lightHoldsButTheNightGoesOn(game):
    """Nine o'clock with the lamp lit *and* the rope hung: the light is not
    an ending tonight but the first half of one. The storm is met, the loop
    goes on to eleven, and the bell rings with the point lit behind it."""
    if game.meta.loopBroken:
        return False
    return bool(game.loop.flags.get(flags.LAMP_LIT)) and bool(
        game.loop.flags.get(flags.ROPE_HUNG)
    )


def _endingDue(game, hour):
    """The ending that fires this hour, or None. Once the loop is broken the
    endings are history and the days are ordinary. The light's row stands
    down when the rope is hung as well, so that a player who has mended both
    halves of the night reaches the bell - see _lightHoldsButTheNightGoesOn."""
    if game.meta.loopBroken:
        return None
    for ending in ENDINGS:
        if ending.hour != hour or not game.loop.flags.get(ending.flag):
            continue
        if ending.unless and game.loop.flags.get(ending.unless):
            continue
        return ending
    return None


def _endDay(game, outcome):
    meta, loop = game.meta, game.loop
    if meta.loopBroken:
        meta.days += 1
        outcome.lines.append(
            "Night falls, and for once it stays fallen. You sleep. Morning "
            "comes - an ordinary one, the %s since %s."
            % (_ordinal(meta.days), endingName(meta))
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


def _whatTomTells(game, outcome, lightHeld):
    """The answers, in Tom's mouth, in the tower after the bell.

    He is the one person who could give them, and the only reason he
    climbs the tower is that somebody finally did what he could not.
    lightHeld is whether the point was lit tonight; it changes what he has
    to forgive himself for."""
    told = game.loop.flags.get(flags.TOLD_TOM_OF_NELL)
    outcome.lines.append(
        "Feet on the tower stairs. Old Tom comes up into the dark with his "
        "hat in his hand and stands looking at the rope a long while before "
        "he says anything. 'I cut it,' he says. 'Not that night. Weeks "
        "before. My mooring line was rotten and Gilbert's father wouldn't "
        "sell me rope on credit, so I came up here one night and took the "
        "bell's, and tied her up with it. It was coiled on her deck when we "
        "went out.' He does not look at you. 'So when the weather came "
        "there was nothing on this bell to pull. Nobody ashore could ring "
        "us in. We couldn't see the point and we couldn't hear the harbour, "
        "and she struck. I came ashore with the rope. I've had it thirty "
        "years.'"
    )
    if told:
        outcome.lines.append(
            "'You found Nell's stone,' he says. 'You knew, and you rang it "
            "anyway. For her.' He puts a hand flat on the bell, which is "
            "still warm from ringing, and keeps it there."
        )
    if lightHeld:
        outcome.lines.append(
            "Out on the point the beam comes round, and round again, laying "
            "a road on the water. 'That was dark too,' Tom says. 'Both of "
            "them, that night. Every other boat this village lost was called "
            "in and lit in. Not mine. That's what's been ringing. Not the "
            "bell - the not-doing of it.' The beam comes round. 'Both done "
            "now. Both, in one night, by somebody who took the trouble to "
            "find out. It can stop.'"
        )
    else:
        outcome.lines.append(
            "'Every other boat this village lost was called in with this "
            "and lit in from the point. Not mine. The lamp was dark that "
            "night too - ask Ada why, if you've the stomach for old "
            "Gilbert's bookkeeping. That's what's been ringing. Not the "
            "bell. The not-doing of it.' He looks out at the point, where "
            "there is no light. 'You've done the half of it that was mine "
            "to do. I'll take that.'"
        )
    game.learn(facts.WHO_CUT_THE_ROPE)
    game.learn(facts.WHY_IT_RINGS)


def _ringForTheMarigold(game, outcome):
    meta = game.meta
    lightHeld = bool(game.loop.flags.get(flags.LIGHT_HELD))
    meta.loopBroken = True
    meta.endings.append(ENDING_BOTH if lightHeld else ENDING_BELL)
    outcome.ending = ENDING_BOTH if lightHeld else ENDING_BELL
    outcome.lines.append(
        "Eleven o'clock. You take the rope in both hands and pull, and the "
        "harbour bell rings - not once, but again and again, the way it "
        "should have rung thirty years ago, out over the water where the "
        "Marigold went down."
    )
    outcome.lines.append(
        "Lights come on along the front. The tavern door is open and nobody "
        "is standing in it."
    )
    _whatTomTells(game, outcome, lightHeld)
    if lightHeld:
        game.learn(facts.THE_NIGHT_MENDED)
        outcome.lines.append(
            "When the last note has gone out over the water there is nothing "
            "after it but the beam going round and the rain easing, and the "
            "night, for the first time, goes on. The next morning is new. "
            "The night of the ninth is closed."
        )
    else:
        game.learn(facts.LOOP_BROKEN)
        outcome.lines.append(
            "When the last note has gone out over the water there is nothing "
            "after it but the night, and the night, for the first time, goes "
            "on. Out on the point the lamp stays dark. The next morning is "
            "new, and one half of that old night is still standing open."
        )
    outcome.lines.append("You have broken the loop. Loop %d was the last." % meta.loops)
    outcome.reset = True
    _newDay(game)


def _theLightHolds(game, outcome):
    """Nine o'clock with the lamp lit and the rope hung: the storm is met,
    and the night goes on to the bell."""
    game.loop.flags[flags.LIGHT_HELD] = True
    game.learn(facts.THE_LIGHT_HELD)
    if game.loop.location == "lighthouse":
        outcome.lines.append(
            "This time there is a light on the point to meet it. The glass "
            "goes white with spray and the lamp burns behind it, and burns, "
            "and does not go out. Ada has stopped polishing the lens. 'Half,' "
            "she says, watching the beam go round. 'That's the half that was "
            "mine. The bell's still yours, and the beam will light you down "
            "the point and along the front. Go on - you've two hours.'"
        )
    else:
        outcome.lines.append(
            "This time there is a light on the point to meet it. The beam "
            "comes round through the rain and lays a road on the water, and "
            "along the front, and up the tower steps where you stand. It "
            "burns, and burns, and does not go out. Half of the night is "
            "mended. The bell is two hours off."
        )


def _holdTheLight(game, outcome):
    """Nine o'clock with the lamp burning and no rope on the bell: the
    second way out, and Ada's answers."""
    meta = game.meta
    meta.loopBroken = True
    meta.endings.append(ENDING_LIGHT)
    game.learn(facts.THE_LIGHT_HELD)
    outcome.ending = ENDING_LIGHT
    outcome.lines.append(
        "Nine o'clock. The storm comes in off the water the way it has come "
        "in every night, and this time there is a light on the point to meet "
        "it. The glass goes white with spray and the lamp burns behind it, "
        "and burns, and does not go out."
    )
    if game.loop.flags.get(flags.SHAMED_GILBERT):
        outcome.lines.append(
            "Along the front the shutters are up against the weather, all but "
            "one: Gilbert is standing in his doorway in the rain, looking out "
            "at the point, and does not go in until the beam has swung round "
            "three times."
        )
    outcome.lines.append(
        "Up in the lamp room Ada has stopped polishing the lens and is only "
        "watching the beam go round, out over the water where the Marigold "
        "went down, and round again. After a while she talks, without "
        "looking away from it. 'You've been wondering who cut that rope. "
        "Nobody, that night - I told you, I saw the whole front and nobody "
        "went near the tower. It was Tom. Weeks before. Gilbert's father "
        "wouldn't sell him rope on credit and his mooring line was rotten, "
        "so he went up one night and took the bell's to tie her up with. It "
        "was on her deck when she went out. So there was nothing on the bell "
        "to pull that night - nobody ashore could ring her in - and my lamp "
        "was dark, so she couldn't see the point either. She struck it. He "
        "came ashore with the rope. He's had it thirty years.'"
    )
    outcome.lines.append(
        "'Every other boat this village lost was lit in from here and called "
        "in with that bell. Not that one. Both dark. That's what rings at "
        "eleven - not the bell, the not-doing of it - and that's why the day "
        "keeps coming back round. Somebody has to close it.' The beam comes "
        "round. 'You've done my half. The other half's still hanging in his "
        "cellar.'"
    )
    game.learn(facts.WHO_CUT_THE_ROPE)
    game.learn(facts.WHY_IT_RINGS)
    outcome.lines.append(
        "There is no bell at eleven. There is nothing at eleven but the rain "
        "easing, and then the morning, and the morning is new - and one half "
        "of that old night is still standing open."
    )
    outcome.lines.append("You have broken the loop. Loop %d was the last." % meta.loops)
    outcome.reset = True
    _newDay(game)


# The ways out, in the order the clock meets them. Adding an ending is a row
# here, a flag in tidewater.flags, and a handler above - never an `if` in a
# scene.
ENDINGS = (
    Ending(
        STORM_HOUR, flags.LAMP_LIT, ENDING_LIGHT, _holdTheLight, unless=flags.ROPE_HUNG
    ),
    Ending(BELL_HOUR, flags.ROPE_HUNG, ENDING_BELL, _ringForTheMarigold),
)


def _newDay(game):
    game.loop = LoopState()


def _ordinal(n):
    suffix = (
        "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )
    return "%d%s" % (n, suffix)
