import pytest

from game_cell import GameCell
from constants import BUILDING_TYPE


def make_cell(*, sea=False, swamp=False, plain=False, forest=False, road=False, railroad=False, shore=False, building=0):
    return GameCell(
        1,
        2,
        (sea, swamp, plain, forest, road, railroad, shore, building),
    )


def test_is_water_true_for_sea():
    cell = make_cell(sea=True)
    assert cell.is_water() is True


def test_is_water_true_for_swamp():
    cell = make_cell(swamp=True)
    assert cell.is_water() is True


def test_is_water_false_for_non_water():
    cell = make_cell(plain=True)
    assert cell.is_water() is False


def test_is_building_false_when_none():
    cell = make_cell(plain=True, building=BUILDING_TYPE["none"])
    assert cell.is_building() is False


def test_is_building_true_when_not_none():
    cell = make_cell(plain=True, building=BUILDING_TYPE["user_home"])
    assert cell.is_building() is True


def test_get_building_type_returns_value():
    cell = make_cell(plain=True, building=BUILDING_TYPE["bank"])
    assert cell.get_building_type() == BUILDING_TYPE["bank"]


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        # --- baseline "buildable" terrains (no building, no water, no road/railroad) ---
        ({"plain": True, "building": BUILDING_TYPE["none"]}, True),
        ({"forest": True, "building": BUILDING_TYPE["none"]}, True),
        ({"shore": True, "building": BUILDING_TYPE["none"]}, True),

        # --- baseline "not buildable" due to water ---
        ({"sea": True, "building": BUILDING_TYPE["none"]}, False),
        ({"swamp": True, "building": BUILDING_TYPE["none"]}, False),

        # --- baseline "not buildable" due to transport ---
        ({"road": True, "plain": True, "building": BUILDING_TYPE["none"]}, False),
        ({"railroad": True, "plain": True, "building": BUILDING_TYPE["none"]}, False),

        # --- baseline "not buildable" due to existing building ---
        ({"plain": True, "building": BUILDING_TYPE["user_home"]}, False),

        # ============================================================
        # NEW CASES REQUESTED
        # ============================================================

        # --- forest + road/railroad combinations ---
        ({"forest": True, "road": True, "building": BUILDING_TYPE["none"]}, False),
        ({"forest": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),
        ({"forest": True, "road": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),

        # --- forest + building (any building blocks building) ---
        ({"forest": True, "building": BUILDING_TYPE["user_home"]}, False),

        # --- forest + road/railroad + building (still false) ---
        ({"forest": True, "road": True, "building": BUILDING_TYPE["user_home"]}, False),
        ({"forest": True, "railroad": True, "building": BUILDING_TYPE["user_home"]}, False),
        ({"forest": True, "road": True, "railroad": True, "building": BUILDING_TYPE["user_home"]}, False),

        # --- plain + road/railroad combinations ---
        ({"plain": True, "road": True, "building": BUILDING_TYPE["none"]}, False),
        ({"plain": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),
        ({"plain": True, "road": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),

        # --- plain + building ---
        ({"plain": True, "building": BUILDING_TYPE["user_home"]}, False),

        # --- plain + road/railroad + building (still false) ---
        ({"plain": True, "road": True, "building": BUILDING_TYPE["user_home"]}, False),
        ({"plain": True, "railroad": True, "building": BUILDING_TYPE["user_home"]}, False),
        ({"plain": True, "road": True, "railroad": True, "building": BUILDING_TYPE["user_home"]}, False),

        # --- swamp + road/railroad combinations (water overrides, always false) ---
        ({"swamp": True, "road": True, "building": BUILDING_TYPE["none"]}, False),
        ({"swamp": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),
        ({"swamp": True, "road": True, "railroad": True, "building": BUILDING_TYPE["none"]}, False),
    ],
)
def test_is_buildable_matrix(kwargs, expected):
    cell = make_cell(**kwargs)
    assert cell.is_buildable() is expected



def test_build_sets_building_to_user_home_when_buildable():
    cell = make_cell(plain=True, building=BUILDING_TYPE["none"])
    assert cell.is_buildable() is True

    ok = cell.build()
    assert ok is True
    assert cell.get_building_type() == BUILDING_TYPE["user_home"]
    assert cell.is_building() is True


def test_build_returns_false_and_does_not_change_when_not_buildable_water():
    cell = make_cell(sea=True, building=BUILDING_TYPE["none"])
    before = cell.terrain
    assert cell.build() is False
    assert cell.terrain == before


def test_build_returns_false_and_does_not_change_when_not_buildable_road():
    cell = make_cell(road=True, plain=True, building=BUILDING_TYPE["none"])
    before = cell.terrain
    assert cell.build() is False
    assert cell.terrain == before


def test_is_shot_passing_false_if_forest():
    cell = make_cell(forest=True, building=BUILDING_TYPE["none"])
    assert cell.is_shot_passing() is False


def test_is_shot_passing_false_if_building_even_if_not_forest():
    cell = make_cell(plain=True, building=BUILDING_TYPE["user_home"])
    assert cell.is_shot_passing() is False


def test_is_shot_passing_true_if_no_building_and_not_forest():
    cell = make_cell(plain=True, building=BUILDING_TYPE["none"])
    assert cell.is_shot_passing() is True
    
def test_is_shot_passing_true_sea():
    cell = make_cell(sea=True, building=BUILDING_TYPE["none"])
    assert cell.is_shot_passing() is True
