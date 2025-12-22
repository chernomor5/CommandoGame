import csv
import pytest

from game_board import GameBoard
from constants import BUILDING_TYPE, ASCII_TILE_RULES


# ----------------------------
# Test helpers
# ----------------------------

def write_board_csv(
    path,
    *,
    sea_border_thickness=1,
    swamp_cells=None,
    forest_cells=None,
    road_cells=None,
    railroad_cells=None,
    building_cells=None,
    boat_rental_cells=None,
):
    W = H = 36
    swamp_cells = swamp_cells or set()
    forest_cells = forest_cells or set()
    road_cells = road_cells or set()
    railroad_cells = railroad_cells or set()
    building_cells = building_cells or {}
    boat_rental_cells = boat_rental_cells or set()

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "sea", "swamp", "plain", "forest", "road", "railroad", "building"])

        for y in range(H):
            for x in range(W):
                dist = min(x, y, W - 1 - x, H - 1 - y)
                is_sea = dist < sea_border_thickness

                sea = 1 if is_sea else 0
                swamp = 0
                forest = 0
                road = 0
                railroad = 0
                building = building_cells.get((x, y), BUILDING_TYPE["none"])

                if (x, y) in boat_rental_cells:
                    building = BUILDING_TYPE["boat_rental"]

                if (x, y) in swamp_cells and sea == 0:
                    swamp = 1

                if (x, y) in forest_cells and sea == 0:
                    forest = 1

                if (x, y) in road_cells and sea == 0:
                    road = 1

                if (x, y) in railroad_cells and sea == 0:
                    railroad = 1

                plain = 1 if (sea == 0 and swamp == 0 and forest == 0) else 0
                w.writerow([x, y, sea, swamp, plain, forest, road, railroad, building])


def write_minimal_header_only_csv(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "sea", "swamp", "plain", "forest", "road", "railroad", "building"])


# ----------------------------
# Existing tests (kept)
# ----------------------------

def test_load_from_csv_builds_full_grid(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))

    assert len(b.grid) == 36
    assert all(len(row) == 36 for row in b.grid)

    assert b.get_cell(0, 0).is_sea()
    assert b.get_cell(35, 35).is_sea()


def test_load_from_csv_requires_full_board(tmp_path):
    csv_path = tmp_path / "incomplete.csv"
    write_minimal_header_only_csv(csv_path)

    with pytest.raises(ValueError):
        GameBoard(str(csv_path))


def test_load_from_csv_rejects_duplicate_coordinates(tmp_path):
    csv_path = tmp_path / "dup.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "sea", "swamp", "plain", "forest", "road", "railroad", "building"])
        w.writerow([0, 0, 1, 0, 0, 0, 0, 0, 0])
        w.writerow([0, 0, 1, 0, 0, 0, 0, 0, 0])

    with pytest.raises(ValueError):
        GameBoard(str(csv_path))


def test_shore_recompute_border_sea_sets_inner_ring_shore(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))

    c = b.get_cell(1, 1)
    assert not c.is_water()
    assert c.is_shore()


def test_shore_recompute_interior_land_not_shore(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))

    c = b.get_cell(2, 2)
    assert not c.is_water()
    assert not c.is_shore()


def test_boat_rental_rule_enforced_on_load(tmp_path):
    csv_path = tmp_path / "board.csv"
    boat_xy = (10, 10)

    write_board_csv(
        csv_path,
        sea_border_thickness=0,
        swamp_cells={boat_xy},
        forest_cells={boat_xy},
        boat_rental_cells={boat_xy},
    )

    b = GameBoard(str(csv_path))
    c = b.get_cell(*boat_xy)

    assert c.get_building_type() == BUILDING_TYPE["boat_rental"]
    assert c.is_sea()
    assert c.is_plain()
    assert not c.is_swamp()
    assert not c.is_forest()


def test_drop_to_island_loop_retries_building_and_swamp_for_player(tmp_path, monkeypatch):
    csv_path = tmp_path / "board.csv"

    building_xy = (5, 5)
    swamp_xy = (6, 6)
    valid_xy = (7, 7)

    write_board_csv(
        csv_path,
        sea_border_thickness=0,
        swamp_cells={swamp_xy},
        building_cells={building_xy: BUILDING_TYPE["user_home"]},
    )

    b = GameBoard(str(csv_path))

    seq = iter([5, 5, 6, 6, 7, 7])
    monkeypatch.setattr("random.randint", lambda a, z: next(seq))

    x, y = b.drop_to_island(is_player=True)
    assert (x, y) == valid_xy


def test_drop_to_island_allows_swamp_for_non_player(tmp_path, monkeypatch):
    csv_path = tmp_path / "board.csv"
    swamp_xy = (6, 6)
    write_board_csv(csv_path, sea_border_thickness=0, swamp_cells={swamp_xy})

    b = GameBoard(str(csv_path))

    seq = iter([6, 6])
    monkeypatch.setattr("random.randint", lambda a, z: next(seq))

    x, y = b.drop_to_island(is_player=False)
    assert (x, y) == swamp_xy


def test_print_ascii_no_color_shape(tmp_path, capsys):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))
    b.print_ascii(use_color=False)

    out = capsys.readouterr().out.rstrip("\n").splitlines()
    assert len(out) == 36
    assert all(len(line) == 36 for line in out)

    joined = "\n".join(out)
    assert "~" in joined
    assert "." in joined


def test_print_ascii_legend_contains_all_rules(tmp_path, capsys):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))
    b.print_ascii_legend(use_color=False)

    out = capsys.readouterr().out
    assert "Legend:" in out

    for rule, symbol, _color in ASCII_TILE_RULES:
        assert symbol in out, f"Missing symbol {symbol!r} for rule {rule!r}"


    # ----------------------------
    # NEW tests you requested
    # ----------------------------

def test_print_board_single_cell_prints_one_cell(tmp_path, capsys):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))
    b.print_board(0, 0)

    out = capsys.readouterr().out.strip()
    assert out  # something printed
    # Should look like JSON produced by GameCell.__str__()
    assert '"x": 0' in out
    assert '"y": 0' in out


def test_print_board_region_prints_correct_number_of_cells(tmp_path, capsys):
    """
    Region is inclusive, so a 2x2 region prints 4 cells.
    Each cell prints multiple lines of JSON, so count by occurrences of '"x":'.
    """
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    b = GameBoard(str(csv_path))
    b.print_board(0, 0, 1, 1)

    out = capsys.readouterr().out
    assert out.count('"x":') == 4


def test_print_board_raises_if_only_x1_given(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)
    b = GameBoard(str(csv_path))

    with pytest.raises(TypeError):
        # Missing y1 (python signature itself should raise TypeError)
        b.print_board(0)  # type: ignore


def test_print_board_raises_for_out_of_bounds_single_cell(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)
    b = GameBoard(str(csv_path))

    with pytest.raises(ValueError):
        b.print_board(36, 0)

    with pytest.raises(ValueError):
        b.print_board(0, 36)

    with pytest.raises(ValueError):
        b.print_board(-1, 0)

    with pytest.raises(ValueError):
        b.print_board(0, -1)


def test_print_board_raises_for_out_of_bounds_region(tmp_path):
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)
    b = GameBoard(str(csv_path))

    with pytest.raises(ValueError):
        b.print_board(0, 0, 36, 0)

    with pytest.raises(ValueError):
        b.print_board(0, 0, 0, 36)

    with pytest.raises(ValueError):
        b.print_board(-1, 0, 0, 0)

    with pytest.raises(ValueError):
        b.print_board(0, -1, 0, 0)


def test_default_constructor_requires_board_csv_in_cwd(tmp_path, monkeypatch):
    """
    GameBoard() defaults to csv_path="board.csv".
    We simulate running in a directory *without* board.csv and expect FileNotFoundError.
    """
    monkeypatch.chdir(tmp_path)  # empty dir
    with pytest.raises(FileNotFoundError):
        GameBoard()


def test_default_constructor_succeeds_when_board_csv_exists(tmp_path, monkeypatch):
    """
    If board.csv exists in CWD, GameBoard() should load it successfully.
    """
    csv_path = tmp_path / "board.csv"
    write_board_csv(csv_path, sea_border_thickness=1)

    monkeypatch.chdir(tmp_path)
    b = GameBoard()  # reads ./board.csv

    assert len(b.grid) == 36
    assert b.get_cell(0, 0).is_sea()
