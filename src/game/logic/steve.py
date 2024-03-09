from typing import Optional
import random

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, clamp, position_equals
import math

def distance_to_goal(current, goal):
    return abs(current.x - goal.x) + abs(current.y - goal.y)

# Mengambil semua diamon yang berada di area 3x3 dari base
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
    sekon = math.floor(props.milliseconds_left / 1000)
    
    diamonds_near_base, pointNearBase = dimons_near_base(gameObj, props)

    if diamonds_near_base: # Jika terdapat diamond di area 3x3 dari base
        sorted_diamonds = sorted([(diamond, distance_to_goal(current_position, diamond.position)) for diamond in diamonds_near_base], key=lambda x: x[1])
        closestDistance_nearBase = sorted_diamonds[0][1]

    # Menyimpan objek bersama jaraknya ke posisi saat ini dan mengurutkannya
    gameObj_with_distance = [(obj, distance_to_goal(current_position, obj.position)) for obj in gameObj]
    gameObj_with_distance = sorted([obj for obj in gameObj_with_distance if obj[1] != 0], key=lambda x: x[1])
    # Meyimpan objek terdekat dan jaraknya
    closest = gameObj_with_distance[0][0]
    closest_distance = gameObj_with_distance[0][1]

    # Jika diamond dekat base dan diamond simpanan lebih dari 5 dan jarak diamond lain lebih jauh
    if pointNearBase + props.diamonds >= 4 and closest_distance > closestDistance_nearBase:
        gameObj_with_distance = sorted_diamonds
        closest_distance = closestDistance_nearBase

    closest_gameObjs = [gameObj for gameObj, distance in gameObj_with_distance if distance == closest_distance]

    for obj in closest_gameObjs if len(closest_gameObjs) > 1 else closest_gameObjs:
        current_point = 0
        current_distance = 0
        dimon_to_base = 0

        min_x = clamp(obj.position.x - 3, 0, 14)
        max_x = clamp(obj.position.x + 3, 0, 14)
        min_y = clamp(obj.position.y - 3, 0, 14)
        max_y = clamp(obj.position.y + 3, 0, 14)

        current_point += obj.properties.points if obj.type == "DiamondGameObject" else 0
        current_distance += closest_distance
        for diamond in diamonds_only:
            current_dimon_to_base = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points if diamond.type == "DiamondGameObject" else 0
                current_distance += distance_to_goal(obj.position, diamond.position)
                current_dimon_to_base = distance_to_goal(diamond.position, props.base)
            if current_dimon_to_base > dimon_to_base:
                dimon_to_base = current_dimon_to_base

        if current_distance < sekon:
            if bestPoint < current_point and dimon_to_base < minToBase:
                minToBase = dimon_to_base
                bestPoint = current_point
                closest = obj

    return closest

# Mendapatkan diamond dekat dengan telporter
def diamond_near_teleport(teleporters, diamondsOnly):
    most_dimon = -1
    for tele in teleporters:
        min_x = clamp(tele.position.x - 4, 0, 14)
        max_x = clamp(tele.position.x + 4, 0, 14)
        min_y = clamp(tele.position.y - 4, 0, 14)
        max_y = clamp(tele.position.y + 4, 0, 14)
        current_points = [] 
        for diamond in diamondsOnly:
            current_point = 0
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points
        current_points.append(current_point) 
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
        self.avoid_positions = [] # Mengosongkan list avoid_positions setiap move

        # Set self.teleport menjadi False jika bot berada di base
        if position_equals(current_position, props.base):
            self.teleport = False

        # Menyimpan teleporter lalu jika bot berada di teleporter, set self.teleport menjadi True
        teleporter = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]
        for tele in teleporter:
            if position_equals(current_position, tele.position):
                self.teleport = True

        # Menambahkan posisi teleporter ke list avoid_positions jika self.teleport bernilai True
        if self.teleport:
            self.avoid_positions.extend([tele.position for tele in teleporter])

        # Mengukur jarak antara posisi saat ini dengan posisi base dan waktu tersisa
        distance_to_base = distance_to_goal(current_position, props.base)
        sekon = math.floor(props.milliseconds_left / 1000) 
        print("Sekon: ", sekon)
        print("Distance to base: ", distance_to_base)

        # Jika bot memiliki lebih dari 3 diamond atau jarak ke base sama dengan waktu tersisa, maka bot akan menuju ke base
        if distance_to_base == sekon and not position_equals(current_position, props.base):
            base = props.base
            self.goal_position = base
            print("go BACKKK")
        elif props.diamonds > 3:
            base = props.base
            self.goal_position = base
            
            # sort teleporter dengan jarak sesaat
            sorted_teleporters = sorted(teleporter, key=lambda x: distance_to_goal(current_position, x.position))
            # mengukur jarak antara bot dengan teleporter terdekat dan teleporter keluar dengan base
            bot_tele = distance_to_goal(current_position, sorted_teleporters[0].position)
            tele_base = distance_to_goal(sorted_teleporters[1].position, base)

            # Jika jarak ke base lebih besar daripada jarak lewat teleporter
            if distance_to_base > bot_tele + tele_base:
                self.goal_position = sorted_teleporters[0].position
                self.teleport = False
            else:
                self.teleport = True
            
        else:

            # Menyimpan objek yang bukan base dan bot
            gameObj_normal = [obj for obj in board.game_objects if obj.type not in ["BaseGameObject", "BotGameObject"]]
            
            # Menghapus diamond jika dekat dengan bot lain
            other_bots = [bot for bot in board.bots if bot.id != id_bot]
            for bot in other_bots:
                for obj in gameObj_normal:
                    if math.sqrt((obj.position.x - bot.position.x)**2 + (obj.position.y - bot.position.y)**2) < 3:
                        gameObj_normal.remove(obj)
            
            # Menghapus diamond button jika score bot lebih kecil dari 7
            if props.score < 7:
                gameObj_normal = [obj for obj in gameObj_normal if obj.type != "DiamondButtonGameObject"]                   

            # Mendapatkan diamon dengan score pas
            gameObj = [obj for obj in gameObj_normal if not (obj.type == "DiamondGameObject" and obj.properties.points + props.diamonds > 5)]

            diamonds_only = [obj for obj in gameObj if obj.type == "DiamondGameObject"]

            if gameObj:
                ベスト = best_and_closest(diamonds_only, gameObj, current_position, props)
            else:
                possible_moves = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if abs(dx) != abs(dy)]
                random_move = random.choice(possible_moves)
                return random_move  

            if ベスト.type == "TeleportGameObject":
                # Mengukur apakah worth it untuk melewati teleporter
                id_tele, dimons = diamond_near_teleport(teleporter, diamonds_only)

                if id_tele == ベスト.id and dimons > 0:
                    self.goal_position = ベスト.position
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
