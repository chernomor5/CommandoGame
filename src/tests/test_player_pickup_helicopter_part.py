# tests/test_player_pickup_helicopter_part.py

import pytest

from player import Player
from helicopter_part import HelicopterPart


class FakeBoard:
    def __init__(self, width=36, height=36):
        self.width = width
        self.height = height

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


def test_pickup_fails_if_part_not_played():
    p = Player(x=1, y=1)
    part = HelicopterPart("RED")  # played=False by default

    ok = p.pickup_helicopter_part(part)
    assert ok is False
    assert p.parts == []
    assert (part.x, part.y) == (-2, -2)
    assert part.is_played() is False


def test_pickup_fails_if_part_not_on_same_cell():
    b = FakeBoard(width=3, height=3)
    p = Player(x=0, y=0)
    part = HelicopterPart("GREEN")
    part.place_on_board(b, 2, 0)

    ok = p.pickup_helicopter_part(part)
    assert ok is False
    assert p.parts == []
    assert (part.x, part.y) == (2, 0)
    assert part.is_played() is True


def test_pickup_succeeds_when_part_on_same_cell_and_played():
    b = FakeBoard(width=3, height=3)
    p = Player(x=1, y=1)
    part = HelicopterPart("BLUE")
    part.place_on_board(b, 1, 1)

    ok = p.pickup_helicopter_part(part)
    assert ok is True

    # player gets the color
    assert p.parts == ["BLUE"]

    # part removed from board
    assert (part.x, part.y) == (-2, -2)

    # played remains True by your class design
    assert part.is_played() is True


def test_pickup_cannot_pick_same_part_twice():
    b = FakeBoard(width=3, height=3)
    p = Player(x=1, y=1)
    part = HelicopterPart("RED")
    part.place_on_board(b, 1, 1)

    ok1 = p.pickup_helicopter_part(part)
    assert ok1 is True
    assert p.parts == ["RED"]

    # second attempt should fail: part coords no longer match player
    ok2 = p.pickup_helicopter_part(part)
    assert ok2 is False
    assert p.parts == ["RED"]  # unchanged
    assert (part.x, part.y) == (-2, -2)
    assert part.is_played() is True
