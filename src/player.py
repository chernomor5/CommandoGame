import json
from typing import List, Dict, Optional, Set, Tuple
from collections import deque

from constants import BALANCE


class Player:
    # =================================================
    # Initialization
    # =================================================

    def __init__(
        self,
        *,
        x: int = -1,
        y: int = -1,
        wound: int = 0,
        money: int = 1500,
        on_land: bool = False,
        on_water: bool = False,
        on_car: bool = False,
        on_boat: bool = False,
        on_train: bool = False,
        weapons: Optional[List[str]] = None,
        parts: Optional[List[str]] = None,
        inventory: Optional[List[str]] = None,
        home: Tuple[int, int] = (-1, -1),
        home_weapons: Optional[List[str]] = None,
        home_parts: Optional[List[str]] = None,
        home_inventory: Optional[List[str]] = None,
        home_money: int = 0,
    ):
        self.x = x
        self.y = y
        self.wound = wound
        self.money = money

        self.on_land = on_land
        self.on_water = on_water
        self.on_car = on_car
        self.on_boat = on_boat
        self.on_train = on_train

        self.weapons = weapons if weapons is not None else []
        self.parts = parts if parts is not None else []
        self.inventory = inventory if inventory is not None else []

        self.home = home
        self.home_weapons = home_weapons if home_weapons is not None else []
        self.home_parts = home_parts if home_parts is not None else []
        self.home_inventory = home_inventory if home_inventory is not None else []
        self.home_money = home_money

    # =================================================
    # Basic state helpers
    # =================================================

    def is_spawned(self, board) -> bool:
        return board.is_in_bounds(self.x, self.y)

    def has_home(self) -> bool:
        return self.home != (-1, -1)

    def at_home(self) -> bool:
        return self.has_home() and (self.x, self.y) == self.home

    def movement_state(self) -> Dict[str, bool]:
        return {
            "on_land": self.on_land,
            "on_water": self.on_water,
            "on_car": self.on_car,
            "on_boat": self.on_boat,
            "on_train": self.on_train,
        }

    # =================================================
    # Health & money
    # =================================================

    def apply_damage(self, damage: int = 0) -> None:
        if damage > 0 and self.wound == 0:
            self.wound += damage
        elif damage <= 0 and self.wound > 0:
            self.wound -= 1

    # compatibility
    def modify_wound(self, damage: int = 0) -> None:
        self.apply_damage(damage)

    def change_money(self, amount: int) -> int:
        if amount < 0 and self.money + amount < 0:
            return -1
        self.money += amount
        return 0

    # compatibility
    def transact_money(self, amount: int) -> int:
        return self.change_money(amount)

    # =================================================
    # Inventory helpers (carried)
    # =================================================

    def add_part(self, part: str) -> None:
        self.parts.append(part)

    def remove_part(self) -> Optional[str]:
        return self.parts.pop() if self.parts else None

    def add_item(self, item: str) -> None:
        self.inventory.append(item)

    def remove_item(self, item: Optional[str] = None) -> Optional[str]:
        if not self.inventory:
            return None
        if item is None:
            return self.inventory.pop()
        if item in self.inventory:
            self.inventory.remove(item)
            return item
        return None

    def add_weapon(self, weapon: str) -> None:
        self.weapons.append(weapon)

    def remove_weapon(self, weapon: Optional[str] = None) -> Optional[str]:
        if not self.weapons:
            return None
        if weapon is None:
            return self.weapons.pop()
        if weapon in self.weapons:
            self.weapons.remove(weapon)
            return weapon
        return None

    # =================================================
    # Home helpers
    # =================================================

    def build_home(self, board) -> bool:
        if self.has_home():
            return False
        cell = board.get_cell(self.x, self.y)
        if not cell.is_buildable():
            return False

        self.home = (self.x, self.y)
        cell.build()
        return True

    def transfer_home_item(
        self,
        *,
        category: str,
        direction: str,
        identifier: Optional[str] = None,
        amount: Optional[int] = None,
    ) -> bool:
        if not self.has_home() or not self.at_home():
            return False

        category = category.strip().lower()
        direction = direction.strip().lower().replace(" ", "_")
        
                # 🔥 FIX: normalize identifier
        if identifier is not None:
            identifier = identifier.strip().lower()

        if category == "money":
            if not amount or amount <= 0:
                return False
            if direction == "to_home":
                if self.money < amount:
                    return False
                self.money -= amount
                self.home_money += amount
                return True
            if direction == "to_player":
                if self.home_money < amount:
                    return False
                self.home_money -= amount
                self.money += amount
                return True
            return False

        if not identifier:
            return False

        if category == "weapon":
            src, dst = (
                (self.weapons, self.home_weapons)
                if direction == "to_home"
                else (self.home_weapons, self.weapons)
            )
        elif category == "part":
            src, dst = (
                (self.parts, self.home_parts)
                if direction == "to_home"
                else (self.home_parts, self.parts)
            )
        elif category == "inventory":
            src, dst = (
                (self.inventory, self.home_inventory)
                if direction == "to_home"
                else (self.home_inventory, self.inventory)
            )
        else:
            return False

        if identifier not in src:
            return False

        src.remove(identifier)
        dst.append(identifier)
        return True

    # =================================================
    # Snapshot / debug
    # =================================================

    def snapshot(self, sections: Optional[Set[str]] = None) -> Dict:
        if sections is None:
            sections = {"state", "status", "carried_inventory", "home_inventory"}

        data: Dict[str, Dict] = {}

        if "state" in sections:
            data["state"] = {
                "x": self.x,
                "y": self.y,
                "wound": self.wound,
                "has_home": self.has_home(),
                **({"home": self.home} if self.has_home() else {}),
            }

        if "status" in sections:
            data["status"] = self.movement_state()

        if "carried_inventory" in sections:
            data["carried_inventory"] = {
                "money": self.money,
                "weapons": list(self.weapons),
                "parts": list(self.parts),
                "inventory": list(self.inventory),
            }

        if "home_inventory" in sections:
            if self.has_home():
                data["home_inventory"] = {
                    "is_at_home": self.at_home(),
                    "home_money": self.home_money,
                    "weapons": list(self.home_weapons),
                    "parts": list(self.home_parts),
                    "inventory": list(self.home_inventory),
                }
            else:
                data["home_inventory"] = {}

        return data

    def __str__(self) -> str:
        return json.dumps(self.snapshot(), indent=2, sort_keys=True)

    # =================================================
    # Movement verification
    # =================================================

    def _early_same_cell_check(
        self,
        board,
        target_x: int,
        target_y: int,
        action_points: int,
    ) -> Optional[bool]:
        # Validate AP
        if not isinstance(action_points, int) or action_points < 0:
            return False

        # Both points must be on board
        if not board.is_in_bounds(self.x, self.y):
            return False
        if not board.is_in_bounds(target_x, target_y):
            return False

        # AP==0: only allowed if already there
        if action_points == 0:
            return (self.x, self.y) == (target_x, target_y)

        # Manhattan fast-fail: can't possibly reach within AP
        manhattan = abs(self.x - target_x) + abs(self.y - target_y)
        if manhattan > action_points:
            return False

        # Continue with specific-mode validation / BFS
        return None


    def _bfs_path(
        self,
        board,
        target_x: int,
        target_y: int,
        action_points: int,
        passable,
    ) -> bool:
        visited = {(self.x, self.y)}
        q = deque([(self.x, self.y, 0)])

        while q:
            x, y, dist = q.popleft()
            if dist > action_points:
                continue
            if (x, y) == (target_x, target_y):
                return True

            for nx, ny in board.neighbors(x, y):
                if (nx, ny) in visited:
                    continue
                cell = board.get_cell(nx, ny)
                if not passable(cell):
                    continue
                visited.add((nx, ny))
                q.append((nx, ny, dist + 1))

        return False

    def can_get_by_car(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early
        if not self.on_car:
            return False

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)
        if not start.is_road() or not dest.is_road():
            return False

        return self._bfs_path(
            board, target_x, target_y, action_points,
            lambda c: c.is_road()
        )

    def can_get_by_train(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early
        if not self.on_train:
            return False

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)
        if not start.is_railroad() or not dest.is_railroad():
            return False

        return self._bfs_path(
            board, target_x, target_y, action_points,
            lambda c: c.is_railroad()
        )

    def can_get_by_boat(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early
        if not self.on_boat:
            return False

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)
        if not start.is_water() or not dest.is_water():
            return False

        return self._bfs_path(
            board, target_x, target_y, action_points,
            lambda c: c.is_water()
        )

    def can_get_by_walk(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)

        def walkable(c) -> bool:
            return (not c.is_water()) or (c.is_water() and c.is_road())

        # must be walkable at both ends
        if not walkable(start) or not walkable(dest):
            return False

        return self._bfs_path(board, target_x, target_y, action_points, walkable)


    def can_get_by_swim(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)
        if not start.is_sea() or not dest.is_sea():
            return False

        return self._bfs_path(
            board, target_x, target_y, action_points,
            lambda c: c.is_sea()
        )

    def can_get_by_changing_stance(self, board, target_x: int, target_y: int, action_points: int) -> bool:
        early = self._early_same_cell_check(board, target_x, target_y, action_points)
        if early is not None:
            return early

        if action_points <= 0:
            return False

        if abs(self.x - target_x) + abs(self.y - target_y) != 1:
            return False

        start = board.get_cell(self.x, self.y)
        dest = board.get_cell(target_x, target_y)

        return (
            (start.is_shore() and dest.is_sea())
            or (start.is_sea() and dest.is_shore())
        )

    # =================================================
    # Attack verification
    # =================================================

    def _attack_cells_or_none(self, board, target_x: int, target_y: int):
        if not board.is_in_bounds(self.x, self.y):
            return None
        if not board.is_in_bounds(target_x, target_y):
            return None

        attacker_cell = board.get_cell(self.x, self.y)
        target_cell = board.get_cell(target_x, target_y)

        if attacker_cell.is_building() or target_cell.is_building():
            return None

        return attacker_cell, target_cell

    def _axis_coords_exclusive(self, target_x: int, target_y: int) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = []

        if self.x == target_x:
            step = 1 if target_y > self.y else -1
            for y in range(self.y + step, target_y, step):
                coords.append((self.x, y))
        elif self.y == target_y:
            step = 1 if target_x > self.x else -1
            for x in range(self.x + step, target_x, step):
                coords.append((x, self.y))

        return coords

    def _los_blocked(
        self,
        board,
        coords: List[Tuple[int, int]],
        *,
        block_buildings: bool = True,
        block_forests: bool = True,
        allow_forest_on_last_scanned_cell: bool = False,
    ) -> bool:
        if not coords:
            return False

        last_index = len(coords) - 1
        for i, (x, y) in enumerate(coords):
            cell = board.get_cell(x, y)

            if block_buildings and cell.is_building():
                return True

            if block_forests and cell.is_forest():
                if allow_forest_on_last_scanned_cell and i == last_index:
                    continue
                return True

        return False

    def can_attack_hand_to_hand(self, board, target_x: int, target_y: int) -> bool:
        if self._attack_cells_or_none(board, target_x, target_y) is None:
            return False

        return (
            self.can_get_by_walk(board, target_x, target_y, BALANCE["h2h"]["walk_ap"])
            or self.can_get_by_swim(board, target_x, target_y, BALANCE["h2h"]["swim_ap"])
            or self.can_get_by_changing_stance(board, target_x, target_y, BALANCE["h2h"]["stance_ap"])
        )

    def can_attack_with_gun(self, board, target_x: int, target_y: int) -> bool:
        if self._attack_cells_or_none(board, target_x, target_y) is None:
            return False

        if "gun" not in self.weapons or "bullet" not in self.weapons:
            return False

        same_col = (self.x == target_x)
        same_row = (self.y == target_y)
        if not (same_col or same_row):
            return False

        distance = abs(target_x - self.x) + abs(target_y - self.y)
        if distance > BALANCE["gun"]["range"]:
            return False

        coords = self._axis_coords_exclusive(target_x, target_y)
        if self._los_blocked(
            board,
            coords,
            block_buildings=True,
            block_forests=True,
            allow_forest_on_last_scanned_cell=False,
        ):
            return False

        return True

    def can_attack_with_rocket(self, board, target_x: int, target_y: int) -> bool:
        if self._attack_cells_or_none(board, target_x, target_y) is None:
            return False

        if "rpg" not in self.weapons or "rocket" not in self.weapons:
            return False

        if self.x - 1 <= target_x <= self.x + 1:
            y_axis_shot = True
        elif self.y - 1 <= target_y <= self.y + 1:
            y_axis_shot = False
        else:
            return False

        if y_axis_shot:
            distance = abs(target_y - self.y)
            step_y = 1 if target_y > self.y else -1
            lane_x = target_x
        else:
            distance = abs(target_x - self.x)
            step_x = 1 if target_x > self.x else -1
            lane_y = target_y

        if (
            distance < BALANCE["rocket"]["min_range"]
            or distance > BALANCE["rocket"]["max_range"]
        ):
            return False

        steps_to_check = distance - 1
        coords: List[Tuple[int, int]] = []
        for i in range(1, steps_to_check + 1):
            if y_axis_shot:
                coords.append((lane_x, self.y + step_y * i))
            else:
                coords.append((self.x + step_x * i, lane_y))

        if self._los_blocked(
            board,
            coords,
            block_buildings=True,
            block_forests=True,
            allow_forest_on_last_scanned_cell=True,
        ):
            return False

        return True

    # =================================================
    # Transport
    # =================================================

    def activate_transport(self, mode: str) -> bool:
        """
        Activate exactly one transport mode.

        Valid modes:
        - "car"
        - "boat"
        - "train"
        - "none"  (clears all transport modes)

        Returns True on success, False if mode is invalid.
        """
        # Reset all transport flags
        self.on_car = False
        self.on_boat = False
        self.on_train = False
        
        if not isinstance(mode, str):
            return False

        mode = mode.strip().lower()

        if mode == "car":
            self.on_car = True
        elif mode == "boat":
            self.on_boat = True
        elif mode == "train":
            self.on_train = True
        elif mode == "none":
            pass  # all already set to False
        else:
            return False

        return True


    def current_transport(self) -> str:
        """
        Return the player's current transport mode.

        Priority:
        - car
        - boat
        - train
        - swim (on_water, not on_boat)
        - walk (fallback)

        Returns one of:
        "car", "boat", "train", "swim", "walk"
        """
        if self.on_car:
            return "car"
        if self.on_boat:
            return "boat"
        if self.on_train:
            return "train"
        if self.on_water:
            return "swim"
        return "walk"

    def toggle_land_water(self) -> None:
        """
        Swap on_land and on_water flags.

        No return value.
        """
        self.on_land, self.on_water = self.on_water, self.on_land
        
    def pickup_helicopter_part(self, part) -> bool:
        """
        Pick up a helicopter part if it is on the board
        and located at the player's current position.

        Returns True on success, False otherwise.
        """
        # Must be on the board
        if not part.is_played():
            return False

        # Must be at the same position
        if (part.x, part.y) != (self.x, self.y):
            return False

        # Remove from board and collect
        color = part.remove_from_board()
        self.parts.append(color)

        return True

