# tests/test_player_attack_verification.py

import pytest

# Adjust to your project layout:
from player import Player


class FakeCell:
    """
    Minimal cell stub for attack verification tests.
    """
    def __init__(self, *, building=False, forest=False):
        self._building = building
        self._forest = forest

    def is_building(self) -> bool:
        return self._building

    def is_forest(self) -> bool:
        return self._forest


class FakeBoard:
    """
    grid[y][x] board with in-bounds, get_cell.
    """
    def __init__(self, grid):
        self.grid = grid
        self.WIDTH = len(grid[0]) if grid else 0
        self.HEIGHT = len(grid)

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def get_cell(self, x: int, y: int) -> FakeCell:
        return self.grid[y][x]


def make_row(cells):
    return FakeBoard([cells])


def make_col(cells):
    return FakeBoard([[c] for c in cells])


# -------------------------
# _attack_cells_or_none
# -------------------------

def test_attack_cells_or_none_rejects_out_of_bounds_attacker_or_target():
    b = make_row([FakeCell(), FakeCell()])
    p = Player(x=0, y=0)

    assert p._attack_cells_or_none(b, 99, 0) is None

    p2 = Player(x=99, y=0)
    assert p2._attack_cells_or_none(b, 0, 0) is None


def test_attack_cells_or_none_rejects_building_attacker_or_target():
    # attacker building
    b = make_row([FakeCell(building=True), FakeCell()])
    p = Player(x=0, y=0)
    assert p._attack_cells_or_none(b, 1, 0) is None

    # target building
    b2 = make_row([FakeCell(), FakeCell(building=True)])
    p2 = Player(x=0, y=0)
    assert p2._attack_cells_or_none(b2, 1, 0) is None


# -------------------------
# _axis_coords_exclusive
# -------------------------

def test_axis_coords_exclusive_same_row_excludes_target_and_attacker():
    # attacker at (0,0), target at (3,0) => coords are (1,0),(2,0)
    b = make_row([FakeCell(), FakeCell(), FakeCell(), FakeCell()])
    p = Player(x=0, y=0)
    coords = p._axis_coords_exclusive(3, 0)
    assert coords == [(1, 0), (2, 0)]


def test_axis_coords_exclusive_same_col_excludes_target_and_attacker():
    # attacker at (0,0), target at (0,3) => coords are (0,1),(0,2)
    b = make_col([FakeCell(), FakeCell(), FakeCell(), FakeCell()])
    p = Player(x=0, y=0)
    coords = p._axis_coords_exclusive(0, 3)
    assert coords == [(0, 1), (0, 2)]


# -------------------------
# _los_blocked
# -------------------------

def test_los_blocked_blocks_on_building():
    b = make_row([FakeCell(), FakeCell(building=True), FakeCell()])
    p = Player(x=0, y=0)

    assert p._los_blocked(b, [(1, 0)], block_buildings=True, block_forests=False) is True


def test_los_blocked_blocks_on_forest_unless_last_allowed():
    b = make_row([FakeCell(), FakeCell(forest=True), FakeCell()])
    p = Player(x=0, y=0)

    # forest blocks when not allowed
    assert p._los_blocked(b, [(1, 0)], block_buildings=False, block_forests=True, allow_forest_on_last_scanned_cell=False) is True
    # forest allowed if it's last scanned cell
    assert p._los_blocked(b, [(1, 0)], block_buildings=False, block_forests=True, allow_forest_on_last_scanned_cell=True) is False


# -------------------------
# can_attack_with_gun
# -------------------------

def test_gun_requires_gun_and_bullet():
    b = make_row([FakeCell(), FakeCell()])
    p = Player(x=0, y=0, weapons=[])

    assert p.can_attack_with_gun(b, 1, 0) is False

    p.weapons = ["gun"]
    assert p.can_attack_with_gun(b, 1, 0) is False

    p.weapons = ["bullet"]
    assert p.can_attack_with_gun(b, 1, 0) is False

    p.weapons = ["gun", "bullet"]
    assert p.can_attack_with_gun(b, 1, 0) is True


def test_gun_requires_same_row_or_same_col():
    b = FakeBoard([[FakeCell(), FakeCell()],
                  [FakeCell(), FakeCell()]])
    p = Player(x=0, y=0, weapons=["gun", "bullet"])

    assert p.can_attack_with_gun(b, 1, 1) is False


def test_gun_blocks_on_forest_in_path_but_allows_forest_at_target():
    # row: A . F T
    # attacker at x=0, target at x=3
    # forest at x=2 (path) blocks
    b_block = make_row([FakeCell(), FakeCell(), FakeCell(forest=True), FakeCell()])
    p = Player(x=0, y=0, weapons=["gun", "bullet"])
    assert p.can_attack_with_gun(b_block, 3, 0) is False

    # row: A . . T(forest) -> allowed since target not scanned
    b_ok = make_row([FakeCell(), FakeCell(), FakeCell(), FakeCell(forest=True)])
    assert p.can_attack_with_gun(b_ok, 3, 0) is True


def test_gun_blocks_on_building_in_path_and_rejects_building_target_via_guard():
    # building in path blocks
    b_block = make_row([FakeCell(), FakeCell(building=True), FakeCell(), FakeCell()])
    p = Player(x=0, y=0, weapons=["gun", "bullet"])
    assert p.can_attack_with_gun(b_block, 3, 0) is False

    # building at target rejected by _attack_cells_or_none
    b_target_building = make_row([FakeCell(), FakeCell(), FakeCell(), FakeCell(building=True)])
    assert p.can_attack_with_gun(b_target_building, 3, 0) is False


# -------------------------
# can_attack_with_rocket
# -------------------------

def test_rocket_requires_rpg_and_rocket():
    b = make_row([FakeCell(), FakeCell(), FakeCell()])
    p = Player(x=0, y=0, weapons=[])

    assert p.can_attack_with_rocket(b, 2, 0) is False
    p.weapons = ["rpg"]
    assert p.can_attack_with_rocket(b, 2, 0) is False
    p.weapons = ["rocket"]
    assert p.can_attack_with_rocket(b, 2, 0) is False

    p.weapons = ["rpg", "rocket"]
    # Aim rule: target_y within +/-1 of self.y => horizontal shot possible
    assert p.can_attack_with_rocket(b, 2, 0) is True


def test_rocket_distance_must_be_between_2_and_19():
    # 1x25 row; attacker at 0
    b = make_row([FakeCell() for _ in range(25)])
    p = Player(x=0, y=0, weapons=["rpg", "rocket"])

    # distance 1 invalid
    assert p.can_attack_with_rocket(b, 1, 0) is False
    # distance 2 valid
    assert p.can_attack_with_rocket(b, 2, 0) is True
    # distance 19 valid
    assert p.can_attack_with_rocket(b, 19, 0) is True
    # distance 20 invalid
    assert p.can_attack_with_rocket(b, 20, 0) is False


def test_rocket_allows_forest_on_last_scanned_cell_only():
    # attacker at x=0, target at x=3 -> distance=3 -> steps_to_check=2 -> scanned: x=1,2
    # forest at x=1 blocks
    b_block = make_row([FakeCell(), FakeCell(forest=True), FakeCell(), FakeCell()])
    p = Player(x=0, y=0, weapons=["rpg", "rocket"])
    assert p.can_attack_with_rocket(b_block, 3, 0) is False

    # forest at x=2 (last scanned cell) allowed
    b_ok = make_row([FakeCell(), FakeCell(), FakeCell(forest=True), FakeCell()])
    assert p.can_attack_with_rocket(b_ok, 3, 0) is True


def test_rocket_blocks_on_any_building_on_scanned_path_and_rejects_building_target_via_guard():
    # building on scanned path blocks
    b_block = make_row([FakeCell(), FakeCell(building=True), FakeCell(), FakeCell()])
    p = Player(x=0, y=0, weapons=["rpg", "rocket"])
    assert p.can_attack_with_rocket(b_block, 3, 0) is False

    # building at target rejected by _attack_cells_or_none
    b_target_building = make_row([FakeCell(), FakeCell(), FakeCell(), FakeCell(building=True)])
    assert p.can_attack_with_rocket(b_target_building, 3, 0) is False
