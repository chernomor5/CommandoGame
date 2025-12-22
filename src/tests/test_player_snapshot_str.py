import json

from player import Player


def test_snapshot_default_includes_all_sections():
    p = Player(x=1, y=2)
    snap = p.snapshot()

    assert set(snap.keys()) == {"state", "status", "carried_inventory", "home_inventory"}
    assert snap["state"]["x"] == 1
    assert snap["state"]["y"] == 2


def test_snapshot_filters_sections():
    p = Player(x=5, y=6, money=123)

    snap = p.snapshot({"state", "carried_inventory"})
    assert set(snap.keys()) == {"state", "carried_inventory"}
    assert snap["state"]["x"] == 5
    assert snap["carried_inventory"]["money"] == 123


def test_snapshot_invalid_sections_are_ignored():
    p = Player(x=5, y=6)
    snap = p.snapshot({"state", "bad_key"})
    assert set(snap.keys()) == {"state"}


def test_snapshot_home_inventory_empty_when_no_home():
    p = Player(home=(-1, -1))
    snap = p.snapshot({"home_inventory"})
    assert snap == {"home_inventory": {}}


def test_snapshot_home_inventory_includes_is_at_home_when_home_exists():
    p = Player(x=2, y=3, home=(2, 3), home_money=50)
    snap = p.snapshot({"home_inventory", "state"})

    assert snap["state"]["has_home"] is True
    assert snap["home_inventory"]["is_at_home"] is True
    assert snap["home_inventory"]["home_money"] == 50


def test_str_outputs_json_of_full_snapshot():
    p = Player(x=1, y=2, money=10, weapons=["gun"])
    s = str(p)

    data = json.loads(s)  # should be valid JSON
    assert set(data.keys()) == {"state", "status", "carried_inventory", "home_inventory"}
    assert data["state"]["x"] == 1
    assert data["carried_inventory"]["money"] == 10
    assert data["carried_inventory"]["weapons"] == ["gun"]
