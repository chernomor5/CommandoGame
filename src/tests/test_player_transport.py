# tests/test_player_transport.py

import pytest

from player import Player


@pytest.mark.parametrize(
    "mode, expected",
    [
        ("car",   (True,  False, False)),
        ("boat",  (False, True,  False)),
        ("train", (False, False, True)),
        ("none",  (False, False, False)),
        ("  CAR  ",   (True,  False, False)),
        ("  boat  ",  (False, True,  False)),
        ("  TrAiN ",  (False, False, True)),
        ("  NoNe  ",  (False, False, False)),
    ],
)
def test_activate_transport_sets_correct_flag_only(mode, expected):
    p = Player(on_car=True, on_boat=True, on_train=True)  # ensure reset happens
    ok = p.activate_transport(mode)
    assert ok is True
    assert (p.on_car, p.on_boat, p.on_train) == expected


@pytest.mark.parametrize("mode", ["", "plane", "submarine", "walk", "swim", None, 123])
def test_activate_transport_invalid_mode_returns_false_and_clears_transport(mode):
    p = Player(on_car=True, on_boat=True, on_train=True)

    ok = p.activate_transport(mode)  # type: ignore[arg-type]
    assert ok is False
    # transport flags should remain cleared because we reset before validation
    assert p.on_car is False
    assert p.on_boat is False
    assert p.on_train is False


def test_current_transport_prefers_car_over_all():
    p = Player(on_car=True, on_boat=True, on_train=True, on_water=True, on_land=False)
    assert p.current_transport() == "car"


def test_current_transport_prefers_boat_over_train_swim_walk():
    p = Player(on_car=False, on_boat=True, on_train=True, on_water=True)
    assert p.current_transport() == "boat"


def test_current_transport_prefers_train_over_swim_walk():
    p = Player(on_car=False, on_boat=False, on_train=True, on_water=True)
    assert p.current_transport() == "train"


def test_current_transport_swim_when_on_water_and_not_on_boat():
    p = Player(on_car=False, on_boat=False, on_train=False, on_water=True, on_land=False)
    assert p.current_transport() == "swim"


def test_current_transport_walk_when_not_on_water_and_no_transport():
    p = Player(on_car=False, on_boat=False, on_train=False, on_water=False, on_land=True)
    assert p.current_transport() == "walk"

    p2 = Player(on_car=False, on_boat=False, on_train=False, on_water=False, on_land=False)
    assert p2.current_transport() == "walk"


@pytest.mark.parametrize(
    "on_land, on_water, expected_land, expected_water",
    [
        (True, False, False, True),
        (False, True, True, False),
        (False, False, False, False),
        (True, True, True, True),
    ],
)
def test_toggle_land_water_swaps_flags(on_land, on_water, expected_land, expected_water):
    p = Player(on_land=on_land, on_water=on_water)
    p.toggle_land_water()
    assert p.on_land is expected_land
    assert p.on_water is expected_water


def test_toggle_land_water_does_not_change_transport_flags():
    p = Player(on_land=True, on_water=False, on_car=True, on_boat=False, on_train=False)
    p.toggle_land_water()
    assert p.on_car is True
    assert p.on_boat is False
    assert p.on_train is False
