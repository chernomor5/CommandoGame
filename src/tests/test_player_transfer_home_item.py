import pytest

from player import Player


def make_player_at_home(**kwargs) -> Player:
    # Put player at home position and ensure home exists.
    p = Player(x=2, y=3, home=(2, 3), **kwargs)
    return p


def test_transfer_requires_home_and_at_home():
    # Has home but not at home
    p = Player(x=0, y=0, home=(1, 1), weapons=["gun"], home_weapons=[])
    assert p.transfer_home_item(category="weapon", direction="to_home", identifier="gun") is False

    # No home
    p2 = Player(x=0, y=0, home=(-1, -1), weapons=["gun"], home_weapons=[])
    assert p2.transfer_home_item(category="weapon", direction="to_home", identifier="gun") is False


def test_transfer_rejects_invalid_category_or_direction():
    p = make_player_at_home(weapons=["gun"], home_weapons=[])

    assert p.transfer_home_item(category="bad", direction="to_home", identifier="gun") is False
    assert p.transfer_home_item(category="weapon", direction="bad", identifier="gun") is False


def test_transfer_weapon_to_home_success():
    p = make_player_at_home(weapons=["gun", "rpg"], home_weapons=["knife"])

    ok = p.transfer_home_item(category="weapon", direction="to_home", identifier="gun")
    assert ok is True
    assert p.weapons == ["rpg"]
    assert p.home_weapons == ["knife", "gun"]


def test_transfer_weapon_to_player_success():
    p = make_player_at_home(weapons=["rpg"], home_weapons=["gun", "knife"])

    ok = p.transfer_home_item(category="weapon", direction="to_player", identifier="gun")
    assert ok is True
    assert p.home_weapons == ["knife"]
    assert p.weapons == ["rpg", "gun"]


def test_transfer_part_inventory_success():
    p = make_player_at_home(parts=["engine"], home_parts=[], inventory=["medkit"], home_inventory=[])

    assert p.transfer_home_item(category="part", direction="to_home", identifier="engine") is True
    assert p.parts == []
    assert p.home_parts == ["engine"]

    assert p.transfer_home_item(category="inventory", direction="to_home", identifier="medkit") is True
    assert p.inventory == []
    assert p.home_inventory == ["medkit"]


def test_transfer_item_not_found_returns_false():
    p = make_player_at_home(weapons=["gun"], home_weapons=[])

    assert p.transfer_home_item(category="weapon", direction="to_home", identifier="knife") is False
    assert p.weapons == ["gun"]
    assert p.home_weapons == []


def test_transfer_requires_identifier_for_non_money():
    p = make_player_at_home(weapons=["gun"], home_weapons=[])

    assert p.transfer_home_item(category="weapon", direction="to_home", identifier=None) is False
    assert p.transfer_home_item(category="weapon", direction="to_home", identifier="") is False
    assert p.transfer_home_item(category="weapon", direction="to_home", identifier="   ") is False


def test_transfer_money_to_home_success():
    p = make_player_at_home(money=1000, home_money=100)

    ok = p.transfer_home_item(category="money", direction="to_home", amount=400)
    assert ok is True
    assert p.money == 600
    assert p.home_money == 500


def test_transfer_money_to_player_success():
    p = make_player_at_home(money=100, home_money=900)

    ok = p.transfer_home_item(category="money", direction="to_player", amount=500)
    assert ok is True
    assert p.money == 600
    assert p.home_money == 400


def test_transfer_money_fails_on_invalid_amount_or_insufficient_funds():
    p = make_player_at_home(money=100, home_money=10)

    assert p.transfer_home_item(category="money", direction="to_home", amount=None) is False
    assert p.transfer_home_item(category="money", direction="to_home", amount=0) is False
    assert p.transfer_home_item(category="money", direction="to_home", amount=-5) is False

    assert p.transfer_home_item(category="money", direction="to_home", amount=999) is False
    assert p.transfer_home_item(category="money", direction="to_player", amount=999) is False


def test_transfer_normalization_trims_and_lowercases():
    p = make_player_at_home(weapons=["gun"], home_weapons=[])

    ok = p.transfer_home_item(category="  WEAPON  ", direction="  TO_HOME  ", identifier="  gun  ")
    assert ok is True
    assert p.weapons == []
    assert p.home_weapons == ["gun"]
