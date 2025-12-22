import pytest

from game_cell import GameCell
from constants import BUILDING_TYPE


def make_cell(*, sea=False, swamp=False, plain=False, forest=False, road=False, railroad=False, shore=False, building=0):
    return GameCell(
        0,
        0,
        (sea, swamp, plain, forest, road, railroad, shore, building),
    )


def full_player(**overrides):
    base = {
        "on_land": False,
        "on_water": False,
        "on_car": False,
        "on_boat": False,
        "on_train": False,
    }
    base.update(overrides)
    return base


def test_train_on_railroad_true():
    cell = make_cell(railroad=True, plain=True)
    assert cell.is_travelable(full_player(on_train=True)) is True
    
def test_train_on_railroad_and_swamp_true():
    cell = make_cell(railroad=True, swamp=True)
    assert cell.is_travelable(full_player(on_train=True)) is True


def test_train_on_non_railroad_false():
    cell = make_cell(plain=True)
    assert cell.is_travelable(full_player(on_train=True)) is False


def test_car_on_road_true():
    cell = make_cell(road=True, plain=True)
    assert cell.is_travelable(full_player(on_car=True)) is True


def test_car_on_non_road_false():
    cell = make_cell(plain=True)
    assert cell.is_travelable(full_player(on_car=True)) is False


def test_boat_on_swamp_true():
    cell = make_cell(swamp=True)
    assert cell.is_travelable(full_player(on_boat=True)) is True


def test_boat_on_sea_true():
    cell = make_cell(sea=True)
    assert cell.is_travelable(full_player(on_boat=True)) is True


def test_on_water_swim_on_sea_true():
    cell = make_cell(sea=True)
    assert cell.is_travelable(full_player(on_water=True)) is True


def test_on_water_swim_on_swamp_false():
    cell = make_cell(swamp=True)
    assert cell.is_travelable(full_player(on_water=True)) is False


def test_on_land_on_plain_true():
    cell = make_cell(plain=True)
    assert cell.is_travelable(full_player(on_land=True)) is True


def test_on_land_on_shore_true():
    cell = make_cell(shore=True)
    assert cell.is_travelable(full_player(on_land=True)) is True


def test_on_land_on_forest_true():
    cell = make_cell(forest=True)
    assert cell.is_travelable(full_player(on_land=True)) is True


def test_on_land_on_water_false():
    cell = make_cell(swamp=True)
    assert cell.is_travelable(full_player(on_land=True)) is False
    
def test_on_land_road_and_swamp_true():
    cell = make_cell(road=True, swamp=True)
    assert cell.is_travelable(full_player(on_land=True)) is True

def test_on_land_railroad_and_swamp_false():
    cell = make_cell(railroad=True, swamp=True)
    assert cell.is_travelable(full_player(on_land=True)) is False


def test_buildings_do_not_block_travel():
    cell = make_cell(plain=True, building=BUILDING_TYPE["user_home"])
    assert cell.is_travelable(full_player(on_land=True)) is True


def test_empty_player_data_all_false_returns_false():
    cell = make_cell(plain=True)
    assert cell.is_travelable({}) is False


@pytest.mark.parametrize(
    "bad_value",
    [1, 0, "yes", "False", None, [], {}, object()],
)
def test_guard_raises_on_non_bool_values(bad_value):
    cell = make_cell(plain=True)
    with pytest.raises(TypeError):
        cell.is_travelable({"on_land": bad_value})
