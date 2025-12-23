from constants import HELICOPTER_COLORS


class HelicopterPart:
    def __init__(self, color: str):
        color = color.strip().upper()
        if color not in HELICOPTER_COLORS:
            raise ValueError(f"Invalid helicopter part color: {color}")

        self.color: str = color
        self.x: int = -2
        self.y: int = -2
        self.played: bool = False

    # -------------------------------------------------
    # State checks
    # -------------------------------------------------

    def is_on_board(self, board) -> bool:
        """
        Returns True if the part is placed on the board,
        coordinates are within bounds, and it is marked as played.
        """
        return self.played and board.is_in_bounds(self.x, self.y)

    def is_played(self) -> bool:
        return self.played

    def get_color(self) -> str:
        return self.color

    # -------------------------------------------------
    # Board placement
    # -------------------------------------------------

    def place_on_board(self, board, x: int, y: int) -> None:
        """
        Place the part on the board at (x, y).
        """
        if not board.is_in_bounds(x, y):
            raise ValueError(f"Coordinates out of bounds: ({x}, {y})")

        self.x = x
        self.y = y
        self.played = True

    def remove_from_board(self) -> str:
        """
        Remove the part from the board and return its color.
        Note: does NOT modify the 'played' flag.
        """
        self.x = -2
        self.y = -2
        return self.color

    # -------------------------------------------------
    # String / repr
    # -------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable, stable representation.
        """
        return (
            f"HelicopterPart("
            f"color={self.color}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"played={self.played}"
            f")"
        )

    def __repr__(self) -> str:
        """
        Developer / debug representation.
        """
        return (
            f"<HelicopterPart color={self.color} "
            f"x={self.x} y={self.y} played={self.played}>"
        )
