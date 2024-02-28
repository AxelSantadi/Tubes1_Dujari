import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, clamp, position_equals
import math

def equal(position1, position2):
    x_diff = abs(position1.x - position2.x)
    y_diff = abs(position1.y - position2.y)
    return (x_diff == 1 and y_diff == 0) or (x_diff == 0 and y_diff == 1)
    
def dimons_near_base(gameObj, props):
    basePosition = props.base
    min_x = clamp(basePosition.x - 4, 0, 14)
    max_x = clamp(basePosition.x + 4, 0, 14)
    min_y = clamp(basePosition.y - 4, 0, 14)
    max_y = clamp(basePosition.y + 4, 0, 14)

    dimons = [obj for obj in gameObj if obj.type == "DiamondGameObject" and obj.position.x >= min_x and obj.position.x <= max_x and obj.position.y >= min_y and obj.position.y <= max_y]

    return dimons

def best_and_closest(diamonds_only, gameObj, current_position, props):
    bestPoint = 0
    minToBase = 9999
    min_distance = 9999
    
    #get distance to game objects
    gameObj_with_distance = [(obj, abs(current_position.x - obj.position.x) + abs(current_position.y - obj.position.y)) for obj in gameObj]
    #sort by distance
    gameObj_with_distance = sorted(gameObj_with_distance, key=lambda x: x[1])

    for obj in gameObj_with_distance:
        print(f"type: {obj[0].type}, distance: {obj[1]}")

    closest = gameObj_with_distance[0][0] #closest game object
    min_distance = gameObj_with_distance[0][1] #distance to closest game object
    #get all game objects with the same distance
    closest_gameObjs = [gameObj for gameObj, distance in gameObj_with_distance if distance == min_distance]
    #get all diamonds#get the most efficient path if there are multiple game objects with the same distance
    for obj in closest_gameObjs if len(closest_gameObjs) > 1 else closest_gameObjs:
        current_point = 0
        current_distance = 0
        dimon_to_base = 0

        min_x = clamp(obj.position.x - 1, 0, 14)
        max_x = clamp(obj.position.x + 1, 0, 14)
        min_y = clamp(obj.position.y - 1, 0, 14)
        max_y = clamp(obj.position.y + 1, 0, 14)

        current_point += obj.properties.points if obj.type == "DiamondGameObject" else 0
        current_distance += min_distance
        for diamond in diamonds_only:
            current_dimon_to_base = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points
                current_distance += abs(obj.position.x - diamond.position.x) + abs(obj.position.y - diamond.position.y)
                current_dimon_to_base = abs(diamond.position.x - props.base.x) + abs(diamond.position.y - props.base.y)
            if current_dimon_to_base > dimon_to_base:
                dimon_to_base = current_dimon_to_base

        if dimon_to_base < minToBase and bestPoint < current_point and current_distance < min_distance:
            minToBase = dimon_to_base
            min_distance = current_distance
            bestPoint = current_point
            closest = obj

        if position_equals(current_position, closest.position):
            closest = gameObj_with_distance[1][0]

    return closest

def diamond_near_teleport(teleporters, diamondsOnly):
    most_dimon = -1
    for tele in teleporters:
        min_x = clamp(tele.position.x - 2, 0, 14)
        max_x = clamp(tele.position.x + 2, 0, 14)
        min_y = clamp(tele.position.y - 2, 0, 14)
        max_y = clamp(tele.position.y + 2, 0, 14)
        current_points = [] 
        for diamond in diamondsOnly:
            current_point = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points
            current_points.append(current_point)  # add current_point to the list
            if current_point > most_dimon:
                most_dimon = current_point
                best_tele_ID = tele.id

        if len(set(current_points)) == 1:
            most_dimon = 0

    return best_tele_ID, most_dimon
    
class DiamondOnly(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
        self.teleport = False
        self.avoid = []
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        id_bot = board_bot.id

        self.avoid = []

        teleporter = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]

        for tele in teleporter:
            if equal(current_position, tele.position):
                self.teleport = True

        bot_list = [obj for obj in board.game_objects if obj.type == "BotGameObject" and obj.id != id_bot]
        self.avoid.extend(bot_list)

        print("Avoiding: ", self.avoid)

        if self.teleport:
            self.avoid.extend(teleporter)

        # Get distance to base
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)

        # Get time left in seconds
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)

        if props.diamonds == 5 or distance_to_base == sekon and not  position_equals(current_position, board_bot.properties.base):
            # Move to base:
            base = board_bot.properties.base
            self.goal_position = base

        else:
            # Get all game objects except base and self
            gameObj_normal = [obj for obj in board.game_objects if obj.type != "BaseGameObject" and obj.id != id_bot]

            # Get diamonds that will accumulate to 5 diamonds
            gameObj_perfectScoreDimons = [obj for obj in gameObj_normal if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]

            # Diamond only game objects
            diamonds_only = [obj for obj in gameObj_perfectScoreDimons if obj.type == "DiamondGameObject"]

            diamonds_near_base = dimons_near_base(gameObj_normal, props)

            if len(diamonds_near_base) > len(diamonds_only):
                diamonds_only = diamonds_near_base

            ベスト = best_and_closest(diamonds_only, diamonds_only, current_position, props)

            if ベスト.type == "TeleportGameObject":
                
                id_tele, dimons = diamond_near_teleport(teleporter, diamonds_only)

                if id_tele == ベスト.id and dimons > 0:
                    self.teleport = True
                else:
                    gameObj = [obj for obj in gameObj if obj.type != "TeleportGameObject"]
                    ベスト = best_and_closest(diamonds_only, gameObj, current_position, props)
            
            self.goal_position = ベスト.position
                
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )
       
        tempPosition = Position(current_position.x + delta_x, current_position.y + delta_y)

        for avoid in self.avoid:
            if position_equals(tempPosition, avoid.position):
                print("Avoiding")
                # If the next position is to be avoided, try moving in a different direction
                if delta_x != 0:  # If we were moving horizontally
                    if Position(current_position.x, current_position.y + 1) not in self.avoid:
                        delta_y = 1  # Try moving up
                    elif Position(current_position.x, current_position.y - 1) not in self.avoid:
                        delta_y = -1  # Try moving down
                    delta_x = 0  # Don't move horizontally
                else:  # If we were moving vertically
                    if Position(current_position.x + 1, current_position.y) not in self.avoid:
                        delta_x = 1  # Try moving right
                    elif Position(current_position.x - 1, current_position.y) not in self.avoid:
                        delta_x = -1  # Try moving left
                    delta_y = 0  # Don't move vertically

        return delta_x, delta_y
