# tests/test_helicopter_part.py

import pytest

from helicopter_part import HelicopterPart


class FakeBoard:
    def __init__(self, width=36, height=36):
        self.width = width
        self.height = height

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


@pytest.mark.parametrize("color", ["RED", "GREEN", "BLUE", " red ", "GrEeN", " blue "])
def test_init_accepts_valid_colors_and_normalizes(color):
    p = HelicopterPart(color)
    assert p.get_color() in {"RED", "GREEN", "BLUE"}
    assert p.x == -2
    assert p.y == -2
    assert p.is_played() is False


@pytest.mark.parametrize("color", ["", "PURPLE", "YELLOW", "R", "greenish", "blu", "123"])
def test_init_rejects_invalid_colors(color):
    with pytest.raises(ValueError):
        HelicopterPart(color)


def test_is_on_board_false_when_not_played_even_if_coords_in_bounds():
    b = FakeBoard(width=3, height=3)
    p = HelicopterPart("RED")

    # force in-bounds coords but played still False
    p.x, p.y = 1, 1
    assert p.is_played() is False
    assert p.is_on_board(b) is False


def test_place_on_board_sets_coords_and_played_and_is_on_board_true():
    b = FakeBoard(width=3, height=3)
    p = HelicopterPart("GREEN")

    p.place_on_board(b, 2, 1)
    assert (p.x, p.y) == (2, 1)
    assert p.is_played() is True
    assert p.is_on_board(b) is True


def test_place_on_board_raises_if_out_of_bounds_and_does_not_change_state():
    b = FakeBoard(width=3, height=3)
    p = HelicopterPart("BLUE")

    before = (p.x, p.y, p.played)
    with pytest.raises(ValueError):
        p.place_on_board(b, 3, 0)  # x out of bounds

    assert (p.x, p.y, p.played) == before


def test_remove_from_board_resets_coords_to_minus2_but_does_not_change_played_and_returns_color():
    b = FakeBoard(width=3, height=3)
    p = HelicopterPart("RED")

    p.place_on_board(b, 1, 1)
    assert p.is_played() is True
    assert p.is_on_board(b) is True

    color = p.remove_from_board()
    assert color == "RED"

    # coords reset
    assert (p.x, p.y) == (-2, -2)

    # played unchanged by design
    assert p.is_played() is True

    # not on board because coords are out of bounds
    assert p.is_on_board(b) is False


def test_str_contains_key_fields():
    p = HelicopterPart("RED")
    s = str(p)
    assert "HelicopterPart(" in s
    assert "color=RED" in s
    assert "x=-2" in s
    assert "y=-2" in s
    assert "played=False" in s


def test_repr_is_compact_and_includes_fields():
    p = HelicopterPart("GREEN")
    r = repr(p)
    assert r.startswith("<HelicopterPart")
    assert "color=GREEN" in r
    assert "x=-2" in r
    assert "y=-2" in r
    assert "played=False" in r
    assert r.endswith(">")
