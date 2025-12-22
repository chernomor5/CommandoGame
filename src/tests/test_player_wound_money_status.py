from player import Player


def test_modify_wound_heals_by_one_only_if_wounded():
    p = Player(wound=0)
    p.modify_wound()
    assert p.wound == 0

    p.wound = 2
    p.modify_wound()
    assert p.wound == 1


def test_modify_wound_damage_applies_only_if_unwounded():
    p = Player(wound=0)
    p.modify_wound(3)
    assert p.wound == 3

    # Damage does not stack if already wounded
    p.modify_wound(2)
    assert p.wound == 3


def test_transact_money_prevents_negative():
    p = Player(money=100)

    assert p.transact_money(-50) == 0
    assert p.money == 50

    assert p.transact_money(-999) == -1
    assert p.money == 50

    assert p.transact_money(200) == 0
    assert p.money == 250


def test_activate_transport_sets_correct_flag_only():
    p = Player(on_car=False, on_boat=False, on_train=False)
    p.activate_transport("car")
    assert p.on_car is True
    assert p.on_boat is False
    assert p.on_train is False

    p = Player(on_car=False, on_boat=False, on_train=False)
    p.activate_transport("boat")
    assert p.on_boat is True
    assert p.on_car is False
    assert p.on_train is False

    p = Player(on_car=False, on_boat=False, on_train=False)
    p.activate_transport("train")
    assert p.on_train is True
    assert p.on_car is False
    assert p.on_boat is False


def test_toggle_land_water_swaps_flags():
    p = Player(on_land=True, on_water=False)
    p.toggle_land_water()
    assert p.on_land is False
    assert p.on_water is True

    p.toggle_land_water()
    assert p.on_land is True
    assert p.on_water is False
