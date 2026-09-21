# @author Daniel McCoy Stephenson
"""One class per place. Each has run(), which shows the place's menu once,
acts on the choice, and returns the id of the place to show next - the same
one, usually - or "quit"."""

from tidewater.scenes.docks import Docks
from tidewater.scenes.shop import Shop
from tidewater.scenes.home import Home
from tidewater.scenes.tavern import Tavern
from tidewater.scenes.bank import Bank
from tidewater.scenes.journal import Journal
from tidewater.scenes.lighthouse import Lighthouse
from tidewater.scenes.churchyard import Churchyard

QUIT = "quit"


def build(game):
    return {
        "docks": Docks(game),
        "shop": Shop(game),
        "home": Home(game),
        "tavern": Tavern(game),
        "bank": Bank(game),
        "journal": Journal(game),
        "lighthouse": Lighthouse(game),
        "churchyard": Churchyard(game),
    }
