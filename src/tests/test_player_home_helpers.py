import pytest

from player import Player


def test_has_home_false_by_default():
    p = Player()
    assert p.has_home() is False


def test_at_home_false_by_default():
    p = Player()
    assert p.at_home() is False


def test_has_home_true_when_home_set():
    p = Player(home=(3, 4))
    assert p.has_home() is True


def test_at_home_true_when_position_matches_home():
    p = Player(x=3, y=4, home=(3, 4))
    assert p.at_home() is True


def test_at_home_false_when_position_does_not_match_home():
    p = Player(x=3, y=4, home=(9, 9))
    assert p.at_home() is False


def test_build_home_fails_if_already_has_home(buildable_board, buildable_cell):
    p = Player(x=1, y=2, home=(5, 5))
    ok = p.build_home(buildable_board)

    assert ok is False
    assert buildable_cell.build_called is False
    assert p.home == (5, 5)


def test_build_home_fails_if_cell_not_buildable(non_buildable_board, non_buildable_cell):
    p = Player(x=1, y=2, home=(-1, -1))
    ok = p.build_home(non_buildable_board)

    assert ok is False
    assert non_buildable_cell.build_called is False
    assert p.home == (-1, -1)


def test_build_home_success_sets_home_and_calls_cell_build(buildable_board, buildable_cell):
    p = Player(x=7, y=8, home=(-1, -1))
    ok = p.build_home(buildable_board)

    assert ok is True
    assert buildable_cell.build_called is True
    assert p.home == (7, 8)
