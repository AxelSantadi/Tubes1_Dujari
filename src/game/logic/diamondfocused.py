import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, position_equals, clamp
import math

def best_and_closest(gameObj, current_position, props, sekon):
    bestPoint = 0
    minToBase = 9999
    
    #get distance to game objects
    gameObj_with_distance = [(obj, abs(current_position.x - obj.position.x) + abs(current_position.y - obj.position.y)) for obj in gameObj]
    #sort by distance
    gameObj_with_distance = sorted(gameObj_with_distance, key=lambda x: x[1])
    closest = gameObj_with_distance[0][0] #closest game object
    min_distance = gameObj_with_distance[0][1] #distance to closest game object
    #get all game objects with the same distance
    closest_gameObjs = [gameObj for gameObj, distance in gameObj_with_distance if distance == min_distance]
    #get all diamonds
    diamonds_only = [obj for obj in gameObj if obj.type == "DiamondGameObject"]
    #get the most efficient path if there are multiple game objects with the same distance
    
    for obj in closest_gameObjs if len(closest_gameObjs) > 1 else closest_gameObjs:
        current_point = 0
        current_distance = 0
        dimon_to_base = 9999

        min_x = clamp(obj.position.x - 2, 0, 14)
        max_x = clamp(obj.position.x + 2, 0, 14)
        min_y = clamp(obj.position.y - 2, 0, 14)
        max_y = clamp(obj.position.y + 2, 0, 14)

        current_point += obj.properties.points if obj.type == "DiamondGameObject" else 0
        current_distance += min_distance
        for diamond in diamonds_only:
            current_dimon_to_base = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points
                current_distance += abs(obj.position.x - diamond.position.x) + abs(obj.position.y - diamond.position.y)
                current_dimon_to_base = abs(diamond.position.x - props.base.x) + abs(diamond.position.y - props.base.y)
            if current_dimon_to_base < dimon_to_base:
                dimon_to_base = current_dimon_to_base

        if current_distance < sekon:
            if dimon_to_base < minToBase and bestPoint < current_point:
                minToBase = dimon_to_base
                bestPoint = current_point
                closest = obj
  
    if position_equals(current_position, closest.position):
        closest = gameObj_with_distance[1][0]

    return closest

class diamondfocused(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
        self.teleport = False
        self.step = 0
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position

        gameObj = [obj for obj in board.game_objects if obj.type not in ["BotGameObject", "BaseGameObject"]]
        
        print(f"teleport: {self.teleport}")

        if self.teleport: 
            gameObj = [obj for obj in gameObj if obj.type != "TeleportGameObject"]

        gameObj = [obj for obj in gameObj if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]
        
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)
        print(f"Distance to base1: {distance_to_base}")
        print(f"seconds1: {sekon}")
        ベスト = best_and_closest(gameObj, current_position, props, sekon)
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)
        print(f"Distance to base2: {distance_to_base}")
        print(f"seconds2: {sekon}")
        
        if props.diamonds == 5 or distance_to_base == sekon and not position_equals(current_position, board_bot.properties.base):
            # Move to base:
            base = board_bot.properties.base
            self.goal_position = base
        else:
            if ベスト.type == "TeleportGameObject":
                self.teleport = True
            
            self.goal_position = ベスト.position
                
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



        return delta_x, delta_y
