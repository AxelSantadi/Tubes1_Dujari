from .models import Position


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def distance_to_dest(current_x, current_y, dests):
    return [abs(current_x - dest.position.x) + abs(current_y - dest.position.y) for dest in dests]

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
        min_x = clamp(obj.position.x - 2, 0, 14)
        max_x = clamp(obj.position.x + 2, 0, 14)
        min_y = clamp(obj.position.y - 2, 0, 14)
        max_y = clamp(obj.position.y + 2, 0, 14)

        current_dest_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)
        
        current_point += obj.properties.points if obj.type == "DiamondGameObject" else 0
        current_distance += min_distance
        for diamond in diamonds_only:
            if diamond.position.x >= min_x and diamond.position.x <= max_x and diamond.position.y >= min_y and diamond.position.y <= max_y:
                current_point += diamond.properties.points
                current_distance += abs(current_position.x - diamond.position.x) + abs(current_position.y - diamond.position.y)
        
        if current_distance < sekon:
            if current_dest_base < minToBase:
                minToBase = current_dest_base
                closest = obj
  
    if position_equals(current_position, closest.position):
        closest = gameObj_with_distance[1][0].position

    return closest
    
def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y
