import pytest


class FakeCell:
    def __init__(self, buildable: bool = True):
        self._buildable = buildable
        self.build_called = False

    def is_buildable(self) -> bool:
        return self._buildable

    def build(self) -> None:
        self.build_called = True


class FakeBoard:
    def __init__(self, cell: FakeCell):
        self._cell = cell

    def get_cell(self, x: int, y: int):
        return self._cell


@pytest.fixture
def buildable_cell():
    return FakeCell(buildable=True)


@pytest.fixture
def non_buildable_cell():
    return FakeCell(buildable=False)


@pytest.fixture
def buildable_board(buildable_cell):
    return FakeBoard(buildable_cell)


@pytest.fixture
def non_buildable_board(non_buildable_cell):
    return FakeBoard(non_buildable_cell)
