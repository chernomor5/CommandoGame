import pytest

# Adjust import to your project layout
from player import Player


class FakeCell:
    """
    Minimal cell stub implementing only what Player movement checks use.
    """
    def __init__(
        self,
        *,
        sea: bool = False,
        water: bool = False,
        road: bool = False,
        railroad: bool = False,
        shore: bool = False,
    ):
        self._sea = sea
        self._water = water
        self._road = road
        self._railroad = railroad
        self._shore = shore

    def is_sea(self) -> bool:
        return self._sea

    def is_water(self) -> bool:
        return self._water

    def is_road(self) -> bool:
        return self._road

    def is_railroad(self) -> bool:
        return self._railroad

    def is_shore(self) -> bool:
        return self._shore


class FakeBoard:
    def __init__(self, grid):
        """
        grid[y][x]
        """
        self.grid = grid
        self.WIDTH = len(grid[0]) if grid else 0
        self.HEIGHT = len(grid)

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def get_cell(self, x: int, y: int) -> FakeCell:
        return self.grid[y][x]

    def neighbors(self, x: int, y: int):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.is_in_bounds(nx, ny):
                yield nx, ny


# -----------------------------
# Helpers
# -----------------------------

def make_line_board(cells):
    """
    1-row board from list of cells: x in [0..n-1], y=0
    """
    return FakeBoard([cells])


# -----------------------------
# _early_same_cell_check tests
# -----------------------------

def test_early_check_rejects_invalid_action_points_type_or_negative():
    p = Player(x=0, y=0)
    b = make_line_board([FakeCell()])

    assert p._early_same_cell_check(b, 0, 0, -1) is False
    assert p._early_same_cell_check(b, 0, 0, 1.5) is False
    assert p._early_same_cell_check(b, 0, 0, "1") is False


def test_early_check_rejects_out_of_bounds_start_or_destination():
    p = Player(x=0, y=0)
    b = make_line_board([FakeCell()])

    # destination OOB
    assert p._early_same_cell_check(b, 1, 0, 1) is False

    # start OOB
    p2 = Player(x=9, y=9)
    assert p2._early_same_cell_check(b, 0, 0, 1) is False


def test_early_check_zero_ap_same_cell_true_otherwise_false():
    p = Player(x=0, y=0)
    b = make_line_board([FakeCell(), FakeCell()])

    assert p._early_same_cell_check(b, 0, 0, 0) is True
    assert p._early_same_cell_check(b, 1, 0, 0) is False


def test_early_check_manhattan_fast_fail():
    p = Player(x=0, y=0)
    b = make_line_board([FakeCell(), FakeCell(), FakeCell()])

    # distance=2, ap=1 => impossible
    assert p._early_same_cell_check(b, 2, 0, 1) is False

    # distance=2, ap=2 => continue (None)
    assert p._early_same_cell_check(b, 2, 0, 2) is None


# -----------------------------
# Movement checks: zero-AP rule applies to ALL modes
# -----------------------------

@pytest.mark.parametrize(
    "method_name",
    [
        "can_get_by_car",
        "can_get_by_train",
        "can_get_by_boat",
        "can_get_by_walk",
        "can_get_by_swim",
        "can_get_by_changing_stance",
    ],
)
def test_all_modes_allow_zero_ap_same_cell_if_in_bounds(method_name):
    """
    Per refactor decision: after bounds checks,
    if action_points==0 and start==dest -> True (even if mode flag is false).
    """
    p = Player(x=0, y=0, on_car=False, on_train=False, on_boat=False)
    b = make_line_board([FakeCell()])

    fn = getattr(p, method_name)
    assert fn(b, 0, 0, 0) is True


# -----------------------------
# can_get_by_car tests
# -----------------------------

def test_can_get_by_car_requires_on_car_and_road_path():
    road = FakeCell(road=True)
    land = FakeCell(road=False)

    # 0-1-2 all road => reachable
    b = make_line_board([road, road, road])

    p = Player(x=0, y=0, on_car=False)
    assert p.can_get_by_car(b, 2, 0, 2) is False  # not on_car

    p.on_car = True
    assert p.can_get_by_car(b, 2, 0, 2) is True

    # break the road in the middle => not reachable
    b2 = make_line_board([road, land, road])
    assert p.can_get_by_car(b2, 2, 0, 2) is False


def test_can_get_by_car_manhattan_fast_fail_short_circuits():
    road = FakeCell(road=True)
    b = make_line_board([road, road, road])
    p = Player(x=0, y=0, on_car=True)

    # distance=2, ap=1 -> impossible
    assert p.can_get_by_car(b, 2, 0, 1) is False


# -----------------------------
# can_get_by_train tests
# -----------------------------

def test_can_get_by_train_requires_on_train_and_railroad_path():
    rr = FakeCell(railroad=True)
    no = FakeCell(railroad=False)

    b = make_line_board([rr, rr, rr])
    p = Player(x=0, y=0, on_train=False)
    assert p.can_get_by_train(b, 2, 0, 2) is False

    p.on_train = True
    assert p.can_get_by_train(b, 2, 0, 2) is True

    b2 = make_line_board([rr, no, rr])
    assert p.can_get_by_train(b2, 2, 0, 2) is False


# -----------------------------
# can_get_by_boat tests
# -----------------------------

def test_can_get_by_boat_requires_on_boat_and_water_path():
    w = FakeCell(water=True)
    land = FakeCell(water=False)

    b = make_line_board([w, w, w])
    p = Player(x=0, y=0, on_boat=False)
    assert p.can_get_by_boat(b, 2, 0, 2) is False

    p.on_boat = True
    assert p.can_get_by_boat(b, 2, 0, 2) is True

    b2 = make_line_board([w, land, w])
    assert p.can_get_by_boat(b2, 2, 0, 2) is False


# -----------------------------
# can_get_by_walk tests
# Walkable: (not water) OR (water and road)
# -----------------------------

def test_can_get_by_walk_allows_land_and_water_with_road_only():
    land = FakeCell(water=False, road=False)
    bridge = FakeCell(water=True, road=True)      # walkable
    water = FakeCell(water=True, road=False)      # NOT walkable

    # land -> bridge -> land (reachable)
    b = make_line_board([land, bridge, land])
    p = Player(x=0, y=0)
    assert p.can_get_by_walk(b, 2, 0, 2) is True

    # land -> water(no road) -> land (blocked)
    b2 = make_line_board([land, water, land])
    assert p.can_get_by_walk(b2, 2, 0, 2) is False


def test_can_get_by_walk_requires_start_and_dest_walkable():
    land = FakeCell(water=False, road=False)
    water = FakeCell(water=True, road=False)

    b = make_line_board([water, land])  # start not walkable
    p = Player(x=0, y=0)
    assert p.can_get_by_walk(b, 1, 0, 1) is False

    b2 = make_line_board([land, water])  # dest not walkable
    p2 = Player(x=0, y=0)
    assert p2.can_get_by_walk(b2, 1, 0, 1) is False


# -----------------------------
# can_get_by_swim tests (sea-only)
# -----------------------------

def test_can_get_by_swim_requires_sea_path():
    sea = FakeCell(sea=True)
    not_sea = FakeCell(sea=False)

    b = make_line_board([sea, sea, sea])
    p = Player(x=0, y=0)
    assert p.can_get_by_swim(b, 2, 0, 2) is True

    b2 = make_line_board([sea, not_sea, sea])
    assert p.can_get_by_swim(b2, 2, 0, 2) is False


def test_can_get_by_swim_requires_start_and_dest_sea():
    sea = FakeCell(sea=True)
    not_sea = FakeCell(sea=False)

    b = make_line_board([not_sea, sea])
    p = Player(x=0, y=0)
    assert p.can_get_by_swim(b, 1, 0, 1) is False  # start not sea

    b2 = make_line_board([sea, not_sea])
    p2 = Player(x=0, y=0)
    assert p2.can_get_by_swim(b2, 1, 0, 1) is False  # dest not sea


# -----------------------------
# can_get_by_changing_stance tests
# One cell shore, other sea, must be adjacent (4-dir)
# -----------------------------

def test_can_get_by_changing_stance_adjacent_shore_to_sea_true():
    shore = FakeCell(shore=True, sea=False)
    sea = FakeCell(shore=False, sea=True)

    b = make_line_board([shore, sea])
    p = Player(x=0, y=0)

    assert p.can_get_by_changing_stance(b, 1, 0, 1) is True
    assert p.can_get_by_changing_stance(b, 1, 0, 2) is True  # AP>0; adjacency rule is separate


def test_can_get_by_changing_stance_requires_adjacent_and_correct_types():
    shore = FakeCell(shore=True, sea=False)
    sea = FakeCell(shore=False, sea=True)
    land = FakeCell(shore=False, sea=False)

    # Not adjacent (distance=2) => Manhattan fast fail will reject when AP=1
    b = make_line_board([shore, land, sea])
    p = Player(x=0, y=0)
    assert p.can_get_by_changing_stance(b, 2, 0, 1) is False

    # Adjacent but wrong types
    b2 = make_line_board([shore, land])
    p2 = Player(x=0, y=0)
    assert p2.can_get_by_changing_stance(b2, 1, 0, 1) is False
