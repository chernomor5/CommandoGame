import json

from game_cell import GameCell
from constants import BUILDING_TYPE


def make_cell(*, sea=False, swamp=False, plain=False, forest=False, road=False, railroad=False, shore=False, building=0):
    return GameCell(
        3,
        5,
        (sea, swamp, plain, forest, road, railroad, shore, building),
    )


def test_repr_is_valid_json_and_has_expected_keys():
    cell = make_cell(plain=True, building=BUILDING_TYPE["user_home"])
    s = repr(cell)
    data = json.loads(s)

    assert data["x"] == 3
    assert data["y"] == 5

    assert data["sea"] is False
    assert data["swamp"] is False
    assert data["plain"] is True
    assert data["forest"] is False
    assert data["road"] is False
    assert data["railroad"] is False
    assert data["shore"] is False

    assert data["building_id"] == BUILDING_TYPE["user_home"]

    assert data["is_water"] is False
    assert data["is_building"] is True
    assert data["is_buildable"] is False
    assert data["is_shot_passing"] is False


def test_str_equals_repr():
    cell = make_cell(forest=True, building=BUILDING_TYPE["none"])
    assert str(cell) == repr(cell)
