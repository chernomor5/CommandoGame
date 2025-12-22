from player import Player


def test_add_remove_part_lifo():
    p = Player()
    assert p.remove_part() is None

    p.add_part("engine")
    p.add_part("rotor")
    assert p.remove_part() == "rotor"
    assert p.remove_part() == "engine"
    assert p.remove_part() is None


def test_add_remove_item_lifo_and_by_name():
    p = Player()
    assert p.remove_item() is None

    p.add_item("medkit")
    p.add_item("ammo")
    p.add_item("ammo")

    assert p.remove_item("ammo") == "ammo"
    assert p.inventory == ["medkit", "ammo"]

    assert p.remove_item("fuel") is None
    assert p.remove_item() == "ammo"
    assert p.remove_item() == "medkit"
    assert p.remove_item() is None


def test_add_remove_weapon_lifo_and_by_name():
    p = Player()
    assert p.remove_weapon() is None

    p.add_weapon("gun")
    p.add_weapon("ammo")
    p.add_weapon("rpg")

    assert p.remove_weapon("ammo") == "ammo"
    assert p.weapons == ["gun", "rpg"]

    assert p.remove_weapon("knife") is None
    assert p.remove_weapon() == "rpg"
    assert p.remove_weapon() == "gun"
    assert p.remove_weapon() is None
