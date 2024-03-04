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

def distance_to_goal(current, goal):
    return abs(current.x - goal.x) + abs(current.y - goal.y)

def dimons_near_base(gameObj, props):
    basePosition = props.base
    min_x = clamp(basePosition.x - 3, 0, 14)
    max_x = clamp(basePosition.x + 3, 0, 14)
    min_y = clamp(basePosition.y - 3, 0, 14)
    max_y = clamp(basePosition.y + 3, 0, 14)

    dimons = [obj for obj in gameObj if obj.type == "DiamondGameObject" and obj.position.x >= min_x and obj.position.x <= max_x and obj.position.y >= min_y and obj.position.y <= max_y]
    total_points = sum([dimon.properties.points for dimon in dimons])
    return dimons, total_points

def best_and_closest(diamonds_only, gameObj, current_position, props):
    bestPoint = 0
    minToBase = 9999
    min_distance = 9999
    sekon = math.floor(props.milliseconds_left / 1000)
    
    #get distance to game objects
    gameObj_with_distance = [(obj, distance_to_goal(current_position, obj.position)) for obj in gameObj]
    #sort by distance
    gameObj_with_distance = sorted([obj for obj in gameObj_with_distance if obj[1] != 0], key=lambda x: x[1])
    
    # for obj in gameObj_with_distance:
    #     print(f"type: {obj[0].type}, distance: {obj[1]}")

    closest = gameObj_with_distance[0][0] #closest game object
    
    closest_distance = gameObj_with_distance[0][1] #distance to closest game object

    #get all game objects with the same distance
    closest_gameObjs = [gameObj for gameObj, distance in gameObj_with_distance if distance == closest_distance]
    #get all diamonds#get the most efficient path if there are multiple game objects with the same distance
    for obj in closest_gameObjs if len(closest_gameObjs) > 1 else closest_gameObjs:
        current_point = 0
        current_distance = 0
        dimon_to_base = 0

        min_x = clamp(obj.position.x - 2, 0, 14)
        max_x = clamp(obj.position.x + 2, 0, 14)
        min_y = clamp(obj.position.y - 2, 0, 14)
        max_y = clamp(obj.position.y + 2, 0, 14)

        current_point += obj.properties.points if obj.type == "DiamondGameObject" else 0
        current_distance += closest_distance
        for diamond in diamonds_only:
            current_dimon_to_base = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points if diamond.type == "DiamondGameObject" else 0
                current_distance += abs(obj.position.x - diamond.position.x) + abs(obj.position.y - diamond.position.y)
                current_dimon_to_base = abs(diamond.position.x - props.base.x) + abs(diamond.position.y - props.base.y)
            if current_dimon_to_base > dimon_to_base:
                dimon_to_base = current_dimon_to_base

        if current_distance < sekon:
            if dimon_to_base < minToBase and bestPoint < current_point:
                minToBase = dimon_to_base
                bestPoint = current_point
                closest = obj

        # if position_equals(current_position, closest.position):
        #     closest = gameObj_with_distance[1][0]

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
        self.avoid_positions = []
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        id_bot = board_bot.id

        # print(f"base: {props.base}")

        self.avoid_positions = []

        teleporter = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]

        for tele in teleporter:
            if equal(current_position, tele.position):
                self.teleport = True

        if self.teleport:
            self.avoid_positions.extend([tele.position for tele in teleporter])

        # Get all other bots
        other_bots = [bot for bot in board.bots if bot.id != id_bot]

        # for obj in self.avoid_positions:
        #     print(obj)

        # Get distance to base
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)

        # Get time left in seconds
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)

        if props.diamonds == 5 or distance_to_base == sekon and not  position_equals(current_position, props.base):
            # Move to base:
            base = board_bot.properties.base

            self.goal_position = base
            sorted_teleporters = sorted(teleporter, key=lambda x: abs(x.position.x - base.x) + abs(x.position.y - base.y))
            
            bot_tele = distance_to_goal(current_position, sorted_teleporters[0].position)
            tele_base = distance_to_goal(sorted_teleporters[1].position, base)

            if position_equals(current_position, sorted_teleporters[0].position) or position_equals(current_position, props.base):
                self.teleport = True
            elif distance_to_base > bot_tele + tele_base:
                self.goal_position = sorted_teleporters[0].position
                self.teleport = False
            
        else:
            # Get all game objects except base and self
            gameObj_normal = [obj for obj in board.game_objects if obj.type != "BaseGameObject" and obj.id != id_bot]
            
            for bot in other_bots:
                min_x = clamp(bot.position.x - 2, 0, 14)
                max_x = clamp(bot.position.x + 2, 0, 14)
                min_y = clamp(bot.position.y - 2, 0, 14)
                max_y = clamp(bot.position.y + 2, 0, 14)
                for obj in gameObj_normal:
                    if obj.position.x >= min_x and obj.position.x <= max_x and obj.position.y >= min_y and obj.position.y <= max_y:
                        enemy_to_dimon = distance_to_goal(bot.position, obj.position)
                        bot_to_dimon = distance_to_goal(current_position, obj.position)   
                        if bot_to_dimon > enemy_to_dimon:
                            gameObj_normal.remove(obj)                     

            if props.score < 7:
                gameObj_normal = [obj for obj in gameObj_normal if obj.type != "DiamondButtonGameObject"]

            # Get diamonds that will accumulate to 5 diamonds
            gameObj = [obj for obj in gameObj_normal if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]

            diamonds_near_base, pointNearBase = dimons_near_base(gameObj, props)
            diamonds_only = [obj for obj in gameObj if obj.type == "DiamondGameObject"]
            print(f"points near base: {pointNearBase}")
            print(len(diamonds_near_base))
            if pointNearBase + props.diamonds >= 5 and len(diamonds_near_base) != 1:
                gameObj = [dimon for dimon in diamonds_near_base if not (dimon.type == "DiamondGameObject" and dimon.properties.points + props.diamonds > 5)]

            ベスト = best_and_closest(diamonds_only, gameObj, current_position, props)

            if ベスト.type == "TeleportGameObject":
                
                id_tele, dimons = diamond_near_teleport(teleporter, diamonds_only)

                if id_tele == ベスト.id and dimons > 0:
                    self.teleport = True
                else:
                    self.avoid_positions.append(ベスト.position)
                    gameObj = [obj for obj in gameObj if obj.type != "TeleportGameObject"]
                    ベスト = best_and_closest(diamonds_only, gameObj, current_position, props)
            
            self.goal_position = ベスト.position
                
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )
       
        tempPosition = Position(current_position.y + delta_y, current_position.x + delta_x) 

        print(f"curent: {current_position}")
        print(f"temp: {tempPosition}") 

        print(f"deltax: {delta_x}, deltay: {delta_y}")

        if tempPosition in self.avoid_positions:
            print("Avoiding")
            # Calculate all possible moves
            possible_moves = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if abs(dx) != abs(dy)]

            # print("valid moves")
            # for move in possible_moves:
            #     print(move)
            # print("f")
            # Filter out moves that would lead to an avoided position
            valid_moves = [(dx, dy) for dx, dy in possible_moves if Position(current_position.y + dy, current_position.x + dx) not in self.avoid_positions ]
            
            valid_moves = [(dx, dy) for dx, dy in valid_moves if current_position.y + dy >= 0 and current_position.y + dy <= 14 and current_position.x + dx >= 0 and current_position.x + dx <= 14]
            # print("valid moves")
            # for move in valid_moves:
            #     print(move)
            # print("f")
            if len(valid_moves) > 1:
                valid_moves = [(dx, dy) for dx, dy in valid_moves if not (dx == -delta_x and dy == -delta_y)]
                # Calculate the distance for each valid move to the goal
                distances = [abs(self.goal_position.x - (current_position.x + dx)) + abs(self.goal_position.y - (current_position.y + dy)) for dx, dy in valid_moves]
                # Get the index of the move with the minimum distance
                min_distance_index = distances.index(min(distances))
                delta_x, delta_y = valid_moves[min_distance_index]
            else:
                delta_x, delta_y = valid_moves[0]

        print(f"deltax: {delta_x}, deltay: {delta_y}")
        
        return delta_x, delta_y
