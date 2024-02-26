import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, closest_dest


class RandomLogic(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        # Analyze new state
        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
        else:
            gameObj = [obj for obj in board.game_objects if obj.type not in ["BotGameObject", "BaseGameObject"]]
            gameObj = [obj for obj in gameObj if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]
            closest = closest_dest(current_position.x, current_position.y, gameObj)

            self.goal_position = closest.position

        # print(f"Current position: {current_position.x}, {current_position.y}")
        # # Print diamond positions
        # print(f"Diamonds: {len(board.diamonds)}")
        # for diamond in board.diamonds:
        #     print(f"Diamond position: {diamond.position.x}, {diamond.position.y}")
        #     print(f"Diamond points: {diamond.properties.points}")

        # for obj in board.game_objects:
        #     print(f"Object points: {obj.properties.points}")

      
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        print(f"Delta: {delta_x}, {delta_y}")

        return delta_x, delta_y
