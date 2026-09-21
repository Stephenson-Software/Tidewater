# @author Daniel McCoy Stephenson
from tak import formatHour

from tidewater import facts
from tidewater.loop import stormRaging

LOCATION_NAMES = {
    "docks": "The Docks",
    "shop": "Gilbert's Shop",
    "home": "Home",
    "tavern": "The Tavern",
    "bank": "The Bank",
    "lighthouse": "The Lighthouse",
    "churchyard": "The Churchyard",
}

ITEM_NAMES = {"rope": "the bell rope"}


def buildHeader(game):
    """The status line: the loop (or the day, once the loop is broken), the
    hour, where the player is, what they carry, how much they know."""
    meta, loop = game.meta, game.loop
    if meta.loopBroken:
        first = "Day %d after the bell" % (meta.days + 1)
    else:
        first = "Loop %d" % meta.loops
    chips = [first, formatHour(loop.hour), LOCATION_NAMES.get(loop.location, "")]
    if stormRaging(loop.hour):
        chips.append({"text": "Storm", "class": "low"})
    for item in loop.items:
        chips.append("Carrying: %s" % ITEM_NAMES.get(item, item))
    known = len(meta.facts)
    chips.append("Known: %d/%d" % (known, len(facts.FACTS)))
    return {"title": "Tidewater - %s" % first, "chips": chips}
