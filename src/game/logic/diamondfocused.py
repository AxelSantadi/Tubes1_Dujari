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
        self.avoid_positions = []
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        
        # Menyimpan posisi telporter dalam self.avoid_positions
        teleporter = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
        self.avoid_positions.append(teleporter)
        # Menghitung jarak dari bot ke base dan waktu tersisa
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)
        sekon = math.floor(board_bot.properties.milliseconds_left / 1000)
        
        # Jika bot memiliki lebih dari 3 diamond atau jarak ke base sama dengan waktu tersisa, maka bot akan menuju ke base
        if props.diamonds > 3 or distance_to_base == sekon and not position_equals(current_position, board_bot.properties.base):
            # Move to base:
            base = board_bot.properties.base
            self.goal_position = base
            self.teleport = False
        else:
            # Menyimpan semua objek yang bukan merupakan BaseGameObject, BotGameObject, dan TeleportGameObject
            gameObj = [obj for obj in board.game_objects if obj.type not in ["BotGameObject", "BaseGameObject", "TeleportGameObject"]]
            # Menghapus diamond jika jumlah diamond lebih dari 5
            gameObj = [obj for obj in gameObj if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]
            # Mendapatkan objek terdekat
            ベスト = best_and_closest(gameObj, current_position, props, sekon)
            print(f"object type: {ベスト.type}")
            self.goal_position = ベスト.position
                
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )
        # Jika posisi yang akan dituju merupakan posisi yang harus dihindari, maka bot akan memilih posisi lain
        tempPosition = Position(current_position.y + delta_y, current_position.x + delta_x)

        if tempPosition in self.avoid_positions:
            # Mendapatkan semua kemungkinan gerakan
            possible_moves = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if abs(dx) != abs(dy)]
            # Memilih gerakan yang tidak ada pada self.avoid_positions
            valid_moves = [(dx, dy) for dx, dy in possible_moves if Position(current_position.y + dy, current_position.x + dx) not in self.avoid_positions ]
            # Memilih gerakan yang berada pada game board
            valid_moves = [(dx, dy) for dx, dy in valid_moves if current_position.y + dy >= 0 and current_position.y + dy <= 14 and current_position.x + dx >= 0 and current_position.x + dx <= 14]
            # Jika terdapat lebih dari 1 gerakan yang valid, maka bot akan memilih gerakan yang paling dekat dengan goal_position
            if len(valid_moves) > 1:
                valid_moves = [(dx, dy) for dx, dy in valid_moves if not (dx == -delta_x and dy == -delta_y)]
                distances = [abs(self.goal_position.x - (current_position.x + dx)) + abs(self.goal_position.y - (current_position.y + dy)) for dx, dy in valid_moves]
                min_distance_index = distances.index(min(distances))
                delta_x, delta_y = valid_moves[min_distance_index]
            else:
                delta_x, delta_y = valid_moves[0]
        
        return delta_x, delta_y
