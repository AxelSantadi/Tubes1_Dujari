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
        enemy_to_base = 0

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