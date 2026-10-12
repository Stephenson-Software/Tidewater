"""Gilbert's shop and the bank keep hours: what each shows shut, what it
offers open, and that waiting outside is still an hour of the day."""

from tidewater.loop import BANK_CLOSE, BANK_OPEN, BELL_HOUR, SHOP_CLOSE, SHOP_OPEN
from tidewater.scenes.bank import Bank
from tidewater.scenes.shop import Shop
from conftest import FakeGame, ScriptedUI


def visit(scene, hour, script):
    game = FakeGame(ScriptedUI(script))
    game.loop.hour = hour
    game.loop.location = scene.id
    place = scene(game)
    return game, place, place.run()


def labels(game):
    return game.ui.menus[0][1]


# --- the shop ---------------------------------------------------------------


def test_the_shuttered_shop_says_when_it_opens_and_has_no_gilbert():
    game, shop, result = visit(Shop, SHOP_CLOSE, ["Wait an hour"])
    descriptor = game.ui.menus[0][0]
    assert descriptor == "Gilbert's shop, shuttered. He opens at 8:00 AM."
    assert "Talk to Gilbert" not in labels(game)
    assert "Look around" not in labels(game)
    assert result == "shop"
    assert game.loop.hour == SHOP_CLOSE + 1
    assert game.prompt.text == "An hour passes."


def test_the_open_shop_offers_gilbert_and_a_look_around():
    game, shop, result = visit(Shop, SHOP_OPEN, ["Look around"])
    assert "rope, hooks, lamp oil" in game.ui.menus[0][0]
    assert "Talk to Gilbert" in labels(game)
    assert game.ui.saw("a barrel of salt")
    # Looking costs an hour like anything else that isn't walking.
    assert result == "shop"
    assert game.loop.hour == SHOP_OPEN + 1


def test_the_shop_closes_on_the_hour():
    game, shop, _ = visit(Shop, SHOP_CLOSE - 1, ["Wait an hour"])
    assert "Talk to Gilbert" in labels(game)
    assert "shuttered" in shop.descriptor()


# --- the bank ---------------------------------------------------------------


def test_the_closed_bank_names_both_hours_and_has_no_margaret():
    game, bank, result = visit(Bank, BANK_OPEN - 1, ["Wait an hour"])
    descriptor = game.ui.menus[0][0]
    assert descriptor == (
        "The bank, closed. Margaret keeps hours from 9:00 AM to 3:00 PM."
    )
    assert "Talk to Margaret" not in labels(game)
    assert result == "bank"
    assert game.loop.hour == BANK_OPEN
    assert game.prompt.text == "An hour passes."
    # Waiting outside is how a player gets in.
    assert "Margaret sits behind the counter" in bank.descriptor()


def test_the_bank_closes_on_the_hour():
    game, bank, _ = visit(Bank, BANK_CLOSE - 1, ["Wait an hour"])
    assert "Talk to Margaret" in labels(game)
    assert "closed" in bank.descriptor()


# --- leaving, and the bell ----------------------------------------------------


def test_walking_out_is_free_and_moves_you():
    for scene in (Shop, Bank):
        game, _, result = visit(scene, SHOP_OPEN, ["Go home"])
        assert result == "home"
        assert game.loop.location == "home"
        assert game.loop.hour == SHOP_OPEN


def test_quit_leaves_the_clock_alone():
    for scene in (Shop, Bank):
        game, _, result = visit(scene, SHOP_OPEN, ["Quit"])
        assert result == "quit"
        assert game.loop.hour == SHOP_OPEN


def test_waiting_into_the_bell_wakes_you_on_the_docks():
    for scene in (Shop, Bank):
        game, _, result = visit(scene, BELL_HOUR - 1, ["Wait an hour"])
        assert result == "docks"
        assert game.loop.location == "docks"
        assert game.loop.hour == 8
        assert game.meta.loops == 2
