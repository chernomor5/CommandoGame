import json
from typing import Tuple

from constants import TERRAIN_INDEX, BUILDING_TYPE


class GameCell:
    """
    terrain tuple layout:
    (sea, swamp, plain, forest, road, railroad, shore, building)
    """

    def __init__(
        self,
        x: int,
        y: int,
        terrain: Tuple[bool, bool, bool, bool, bool, bool, bool, int],
    ):
        self.x = x
        self.y = y
        self.terrain = terrain

    # --- terrain checks ---

    def is_sea(self) -> bool:
        return self.terrain[TERRAIN_INDEX["sea"]]

    def is_swamp(self) -> bool:
        return self.terrain[TERRAIN_INDEX["swamp"]]

    def is_plain(self) -> bool:
        return self.terrain[TERRAIN_INDEX["plain"]]

    def is_forest(self) -> bool:
        return self.terrain[TERRAIN_INDEX["forest"]]

    def is_road(self) -> bool:
        return self.terrain[TERRAIN_INDEX["road"]]

    def is_railroad(self) -> bool:
        return self.terrain[TERRAIN_INDEX["railroad"]]

    def is_shore(self) -> bool:
        return self.terrain[TERRAIN_INDEX["shore"]]

    # --- building checks ---

    def is_building(self) -> bool:
        return self.terrain[TERRAIN_INDEX["building"]] != BUILDING_TYPE["none"]

    def get_building_type(self) -> int:
        return self.terrain[TERRAIN_INDEX["building"]]

    # --- combined rules ---

    def is_water(self) -> bool:
        return self.is_sea() or self.is_swamp()

    def is_shot_passing(self) -> bool:
        return not self.is_building() and not self.is_forest()

    def is_buildable(self) -> bool:
        if self.is_building() or self.is_water():
            return False
        if self.is_road() or self.is_railroad():
            return False
        return True

    # --- internal helpers ---

    def _set_building(self, value: int) -> None:
        self.terrain = self.terrain[:TERRAIN_INDEX["building"]] + (value,)

    # --- actions ---

    def build(self) -> bool:
        if not self.is_buildable():
            return False
        self._set_building(BUILDING_TYPE["user_home"])
        return True

    # --- travel rules ---

    def is_travelable(self, player_data: dict) -> bool:
        """
        Determine whether this cell can be traveled to based on player state.

        player_data keys (bool):
        - on_land
        - on_water
        - on_car
        - on_boat
        - on_train
        """
        # --- guard: enforce boolean values ---
        for key in ("on_land", "on_water", "on_car", "on_boat", "on_train"):
            if key in player_data and not isinstance(player_data[key], bool):
                raise TypeError(f"{key} must be a boolean")

        # 1) Train movement
        if player_data.get("on_train") and self.is_railroad():
            return True

        # 2) Car movement
        if player_data.get("on_car") and self.is_road():
            return True

        # 3) Boat movement
        if player_data.get("on_boat") and self.is_water():
            return True

        # 4) Swimming (sea only)
        if player_data.get("on_water") and self.is_sea():
            return True

        # 5) Land movement (non-water)
        if player_data.get("on_land") and not self.is_water():
            return True

        # 6) Land movement explicitly allowed on roads
        if player_data.get("on_land") and self.is_road():
            return True

        return False



    # --- status / REPL ---

    def _status_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,

            # terrain flags
            "sea": self.terrain[TERRAIN_INDEX["sea"]],
            "swamp": self.terrain[TERRAIN_INDEX["swamp"]],
            "plain": self.terrain[TERRAIN_INDEX["plain"]],
            "forest": self.terrain[TERRAIN_INDEX["forest"]],
            "road": self.terrain[TERRAIN_INDEX["road"]],
            "railroad": self.terrain[TERRAIN_INDEX["railroad"]],
            "shore": self.terrain[TERRAIN_INDEX["shore"]],

            # building
            "building_id": self.get_building_type(),

            # derived flags
            "is_water": self.is_water(),
            "is_building": self.is_building(),
            "is_buildable": self.is_buildable(),
            "is_shot_passing": self.is_shot_passing(),
        }

    def __repr__(self) -> str:
        return json.dumps(self._status_dict(), indent=2)

    def __str__(self) -> str:
        return self.__repr__()
