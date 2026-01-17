from constants import BUILDING_TYPE


class PlayerActionProvider:
    @staticmethod
    def possible_actions(player, board, helicopter_part=None) -> list[str]:
        actions: list[str] = []

        if not player.is_spawned(board):
            actions.append("spawn")
            return actions

        cell = board.get_cell(player.x, player.y)
        btype = cell.get_building_type()

        # ----------------------------------------
        # Helpers
        # ----------------------------------------

        def has_adjacent_land() -> bool:
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = player.x + dx, player.y + dy
                if 0 <= nx < board.WIDTH and 0 <= ny < board.HEIGHT:
                    if not board.get_cell(nx, ny).is_water():
                        return True
            return False

        def part_on_current_cell() -> bool:
            if hasattr(board, "has_part_at") and callable(board.has_part_at):
                return bool(board.has_part_at(player.x, player.y))

            if hasattr(board, "parts_at"):
                try:
                    return bool(board.parts_at.get((player.x, player.y)))
                except Exception:
                    return False

            return False

        # ----------------------------------------
        # Always available
        # ----------------------------------------

        actions.append("attack hand-to-hand")
        actions.append("print home inventory")
        actions.append("print current inventory")
        actions.append("print current cell")
        actions.append("print part location")
        actions.append("print other player locations")

        # ----------------------------------------
        # Pickup
        # ----------------------------------------

        if part_on_current_cell():
            actions.append("pickup part")

        if helicopter_part is not None:
            actions.append("pickup helicopter part")

        # ----------------------------------------
        # Building-based actions (SWAPPED)
        # ----------------------------------------

        if btype == BUILDING_TYPE["hospital"] and player.wound > 0:
            actions.append("heal")

        if btype == BUILDING_TYPE["bank"]:
            actions.append("work")

        if btype == BUILDING_TYPE["car_rental"]:
            actions.append("rent car")

        if btype == BUILDING_TYPE["train_station"]:
            actions.append("buy train ticket")

        if btype == BUILDING_TYPE["boat_rental"]:
            actions.append("rent boat")

        if btype == BUILDING_TYPE["shop"]:
            actions.append("buy guns")

        if btype == BUILDING_TYPE["airport"] and len(set(player.parts)) >= 3:
            actions.append("win game")

        # ----------------------------------------
        # Boat / water / shore
        # ----------------------------------------

        if player.on_boat:
            actions.append("sail on boat")
            if has_adjacent_land():
                actions.append("disembark")

        if player.on_water and not player.on_boat:
            actions.append("swim")
            if has_adjacent_land():
                actions.append("climb ashore")

        if cell.is_shore():
            actions.append("jump into sea")

        # ----------------------------------------
        # Vehicles
        # ----------------------------------------

        if player.on_car and cell.is_road():
            actions.append("drive")
            actions.append("exit car")

        if player.on_train and player.on_land:
            actions.append("exit train")

        if player.on_train and cell.is_railroad():
            actions.append("ride train")

        # ----------------------------------------
        # Movement
        # ----------------------------------------

        if player.on_land:
            actions.append("walk")

        # ----------------------------------------
        # Combat
        # ----------------------------------------

        if ("gun" in player.weapons) and ("bullets" in player.weapons):
            actions.append("gun attack")

        if ("RPG" in player.weapons) and ("rocket" in player.weapons):
            actions.append("rocket attack")

        # ----------------------------------------
        # Home
        # ----------------------------------------

        if player.home == (-1, -1) and cell.is_buildable():
            actions.append("build home")

        if player.home == (player.x, player.y):
            actions.append("inventory")

        return actions
