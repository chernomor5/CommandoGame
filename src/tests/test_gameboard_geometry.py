import pytest

from game_board import GameBoard


@pytest.fixture
def board_3x3():
    """
    Creates a 3x3 board for geometry tests.
    """
    return GameBoard(width=3, height=3)


# -------------------------------------------------
# is_in_bounds tests
# -------------------------------------------------

@pytest.mark.parametrize(
    "x,y,expected",
    [
        (0, 0, True),
        (2, 2, True),
        (1, 1, True),
        (-1, 0, False),
        (0, -1, False),
        (3, 0, False),
        (0, 3, False),
        (3, 3, False),
        (-1, -1, False),
    ],
)
def test_is_in_bounds(board_3x3, x, y, expected):
    assert board_3x3.is_in_bounds(x, y) is expected


def test_is_in_bounds_edges(board_3x3):
    """
    Explicit edge checks.
    """
    assert board_3x3.is_in_bounds(0, 0)
    assert board_3x3.is_in_bounds(2, 2)
    assert not board_3x3.is_in_bounds(3, 2)
    assert not board_3x3.is_in_bounds(2, 3)


# -------------------------------------------------
# neighbors4 tests
# -------------------------------------------------

def test_neighbors4_center(board_3x3):
    """
    Center cell should have 4 neighbors.
    """
    neighbors = set(board_3x3.neighbors4(1, 1))
    assert neighbors == {(0, 1), (2, 1), (1, 0), (1, 2)}


def test_neighbors4_corner(board_3x3):
    """
    Corner cell should have 2 neighbors.
    """
    neighbors = set(board_3x3.neighbors4(0, 0))
    assert neighbors == {(1, 0), (0, 1)}


def test_neighbors4_edge(board_3x3):
    """
    Edge (non-corner) cell should have 3 neighbors.
    """
    neighbors = set(board_3x3.neighbors4(1, 0))
    assert neighbors == {(0, 0), (2, 0), (1, 1)}


def test_neighbors4_all_within_bounds(board_3x3):
    """
    neighbors4 must never return out-of-bounds coordinates.
    """
    for x in range(3):
        for y in range(3):
            for nx, ny in board_3x3.neighbors4(x, y):
                assert board_3x3.is_in_bounds(nx, ny)


def test_neighbors4_no_diagonals(board_3x3):
    """
    neighbors4 must not include diagonal neighbors.
    """
    neighbors = set(board_3x3.neighbors4(1, 1))
    assert (0, 0) not in neighbors
    assert (2, 2) not in neighbors
    assert (0, 2) not in neighbors
    assert (2, 0) not in neighbors
