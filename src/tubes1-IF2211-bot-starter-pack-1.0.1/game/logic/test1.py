import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, position_equals, best_and_closest
import math


class DiamondOnly(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
        self.teleport = False 
        self.step = 0
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position

        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)
        print(f"Distance to base: {distance_to_base}")
        print(f"seconds: {sekon}")

        if props.diamonds == 5 or distance_to_base == sekon and not position_equals(current_position, board_bot.properties.base):
            # Move to base:
            base = board_bot.properties.base
            self.goal_position = base

        else:
            gameObj = [obj for obj in board.game_objects if obj.type not in ["BotGameObject", "BaseGameObject", "DiamondButtonGameObject", "TeleportGameObject"]]

            if self.teleport: 
                gameObj = [obj for obj in gameObj if obj.type != "TeleportGameObject"]
                
            gameObj = [obj for obj in gameObj if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]
            
            # gameObj_with_distance = [(obj, abs(current_position.x - obj.position.x) + abs(current_position.y - obj.position.y)) for obj in gameObj]
            # gameObj_with_distance = sorted(gameObj_with_distance, key=lambda x: x[1])

            # for gameObj, distance in gameObj_with_distance:
            #     print(f"Game object type: {gameObj.type} game object distance: {distance}")

            # closest = gameObj_with_distance[0][0]
            # min_distance = gameObj_with_distance[0][1]
            # closest_gameObjs = [gameObj for gameObj, distance in gameObj_with_distance if distance == min_distance]
            # for obj in closest_gameObjs:
            #     print(f"Closest game object: {obj.type}")
            #     print(f"Closest game object distance: {min_distance}")
            # if closest.type == "TeleportGameObject":
            #     self.teleport = True

            ベスト = best_and_closest(gameObj, current_position, props, sekon)

            if ベスト.type == "TeleportGameObject":
                self.teleport = True
            
            self.goal_position = ベスト.position

            # if position_equals(current_position, self.goal_position):
            #     self.goal_position = gameObj_with_distance[1][0].position

                
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )
        
        # print(f"Current position: {current_position.x}, {current_position.y}")
        # # Print diamond positions
        # print(f"Diamonds: {len(board.diamonds)}")
        # for diamond in board.diamonds:
        #     print(f"Diamond position: {diamond.position.x}, {diamond.position.y}")
        #     print(f"Diamond points: {diamond.properties.points}")

        # for obj in board.game_objects:
        #     print(f"Object points: {obj.properties.points}")

        

        print(f"Delta: {delta_x}, {delta_y}")
        self.step += 1
        print(f"Step: {self.step}")
        return delta_x, delta_y
