import random
import csv
from typing import List, Optional

from game_cell import GameCell
from constants import (
    TERRAIN_INDEX,
    BUILDING_TYPE,
    Ansi,
    ASCII_TILE_RULES,
)


class GameBoard:
    WIDTH = 36
    HEIGHT = 36

    def __init__(
        self,
        csv_path: Optional[str] = "board.csv",
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Supports two modes:

        1) CSV mode (default):
           GameBoard() or GameBoard(csv_path="board.csv")

        2) Geometry / test mode:
           GameBoard(width=..., height=...)
           Creates a plain-only board with building=0.
        """
        # Geometry / test mode
        if width is not None or height is not None:
            if width is None or height is None:
                raise ValueError("Both width and height must be provided")

            self.WIDTH = int(width)
            self.HEIGHT = int(height)

            self.grid: List[List[GameCell]] = []
            for y in range(self.HEIGHT):
                row: List[GameCell] = []
                for x in range(self.WIDTH):
                    terrain = [False] * 8
                    terrain[TERRAIN_INDEX["plain"]] = True
                    terrain[TERRAIN_INDEX["building"]] = 0
                    row.append(GameCell(x, y, tuple(terrain)))
                self.grid.append(row)

            self._recompute_shores()
            return

        # CSV mode
        if csv_path is None:
            raise ValueError("csv_path cannot be None")

        self.grid: List[List[GameCell]] = []
        self.load_from_csv(csv_path)

    # -------------------------------------------------
    # CSV loading
    # -------------------------------------------------

    @classmethod
    def from_csv(cls, csv_path: str) -> "GameBoard":
        return cls(csv_path)

    def load_from_csv(self, csv_path: str) -> None:
        required = {
            "x", "y",
            "sea", "swamp", "plain", "forest",
            "road", "railroad",
            "building",
        }

        def parse_bool(v: str) -> bool:
            s = str(v).strip().lower()
            if s in ("1", "true", "t", "yes", "y"):
                return True
            if s in ("0", "false", "f", "no", "n", ""):
                return False
            raise ValueError(f"Invalid boolean value: {v!r}")

        def parse_int(v: str) -> int:
            return int(str(v).strip())

        cells: dict[tuple[int, int], GameCell] = {}

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV missing header")

            missing = required - set(reader.fieldnames)
            if missing:
                raise ValueError(f"CSV missing columns: {sorted(missing)}")

            for row in reader:
                x = parse_int(row["x"])
                y = parse_int(row["y"])

                if not self.is_in_bounds(x, y):
                    raise ValueError(f"Out of bounds cell: ({x},{y})")

                sea = parse_bool(row["sea"])
                swamp = parse_bool(row["swamp"])
                plain = parse_bool(row["plain"])
                forest = parse_bool(row["forest"])
                road = parse_bool(row["road"])
                railroad = parse_bool(row["railroad"])
                building = parse_int(row["building"])

                # Boat rental rule
                if building == BUILDING_TYPE["boat_rental"]:
                    sea = True
                    plain = True
                    swamp = False
                    forest = False

                terrain = [False] * 8
                terrain[TERRAIN_INDEX["sea"]] = sea
                terrain[TERRAIN_INDEX["swamp"]] = swamp
                terrain[TERRAIN_INDEX["plain"]] = plain
                terrain[TERRAIN_INDEX["forest"]] = forest
                terrain[TERRAIN_INDEX["road"]] = road
                terrain[TERRAIN_INDEX["railroad"]] = railroad
                terrain[TERRAIN_INDEX["shore"]] = False
                terrain[TERRAIN_INDEX["building"]] = building

                key = (x, y)
                if key in cells:
                    raise ValueError(f"Duplicate cell at {key}")

                cells[key] = GameCell(x, y, tuple(terrain))

        if len(cells) != self.WIDTH * self.HEIGHT:
            raise ValueError("CSV does not contain full board")

        self.grid = [
            [cells[(x, y)] for x in range(self.WIDTH)]
            for y in range(self.HEIGHT)
        ]

        self._recompute_shores()

    # -------------------------------------------------
    # Geometry helpers
    # -------------------------------------------------

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def get_cell(self, x: int, y: int) -> GameCell:
        return self.grid[y][x]

    def neighbors(self, x: int, y: int, neighbor_count: int = 4):
        """
        Yield neighboring (nx, ny) coordinates.

        neighbor_count:
          - 4 (default): orthogonal neighbors only
          - 8: orthogonal + diagonal neighbors
        """
        if neighbor_count == 4:
            directions = (
                (1, 0), (-1, 0),
                (0, 1), (0, -1),
            )
        elif neighbor_count == 8:
            directions = (
                (1, 0), (-1, 0),
                (0, 1), (0, -1),
                (1, 1), (1, -1),
                (-1, 1), (-1, -1),
            )
        else:
            raise ValueError("neighbor_count must be 4 or 8")

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_in_bounds(nx, ny):
                yield nx, ny

    # -------------------------------------------------
    # Shore derivation
    # -------------------------------------------------

    def _set_shore(self, cell: GameCell, value: bool) -> None:
        t = list(cell.terrain)
        t[TERRAIN_INDEX["shore"]] = value
        cell.terrain = tuple(t)

    def _recompute_shores(self) -> None:
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                cell = self.get_cell(x, y)
                if cell.is_water():
                    self._set_shore(cell, False)
                else:
                    touches_water = any(
                        self.get_cell(nx, ny).is_water()
                        for nx, ny in self.neighbors(x, y, neighbor_count=4)
                    )
                    self._set_shore(cell, touches_water)

    # -------------------------------------------------
    # Drop logic (loop-based)
    # -------------------------------------------------

    def drop_to_island(self, is_player: bool) -> tuple[int, int]:
        while True:
            x = random.randint(0, self.WIDTH - 1)
            y = random.randint(0, self.HEIGHT - 1)

            cell = self.get_cell(x, y)

            if cell.is_building():
                continue
            if is_player and cell.is_swamp():
                continue

            return x, y

    # -------------------------------------------------
    # ASCII visualization
    # -------------------------------------------------

    def _ascii_symbol(self, cell: GameCell):
        for rule, symbol, color in ASCII_TILE_RULES:
            if rule == "building" and cell.is_building():
                return symbol, color
            if rule == "railroad" and cell.is_railroad():
                return symbol, color
            if rule == "road" and cell.is_road():
                return symbol, color
            if rule == "swamp_forest" and cell.is_swamp() and cell.is_forest():
                return symbol, color
            if rule == "swamp" and cell.is_swamp():
                return symbol, color
            if rule == "forest" and cell.is_forest():
                return symbol, color
            if rule == "sea" and cell.is_sea():
                return symbol, color
            if rule == "plain" and cell.is_plain():
                return symbol, color

        return "?", Ansi.WHITE

    def print_ascii(self, use_color: bool = True) -> None:
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                symbol, color = self._ascii_symbol(self.get_cell(x, y))
                if use_color:
                    row.append(f"{color}{symbol}{Ansi.RESET}")
                else:
                    row.append(symbol)
            print("".join(row))

    def print_ascii_legend(self, use_color: bool = True) -> None:
        print("Legend:")
        for rule, symbol, color in ASCII_TILE_RULES:
            label = rule.replace("_", " ").title()
            rendered = f"{color}{symbol}{Ansi.RESET}" if use_color else symbol
            print(f"  {rendered} : {label}")

    # -------------------------------------------------
    # Debug printing
    # -------------------------------------------------

    def print_board(
        self,
        x1: Optional[int] = None,
        y1: Optional[int] = None,
        x2: Optional[int] = None,
        y2: Optional[int] = None,
    ) -> None:
        if x1 is None:
            for row in self.grid:
                for cell in row:
                    print(cell)
            return

        if not self.is_in_bounds(x1, y1):
            raise ValueError("Coordinates out of bounds")

        if x2 is None:
            print(self.get_cell(x1, y1))
            return

        if not self.is_in_bounds(x2, y2):
            raise ValueError("Coordinates out of bounds")

        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                print(self.get_cell(x, y))

    # -------------------------------------------------
    # String / repr
    # -------------------------------------------------

    def __str__(self) -> str:
        return "\n".join(str(cell) for row in self.grid for cell in row)

    def __repr__(self) -> str:
        return f"<GameBoard {self.WIDTH}x{self.HEIGHT}>"
