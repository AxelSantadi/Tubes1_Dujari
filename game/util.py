from .models import Position


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def closest_dest(current_x, current_y, dests):
    closest = None
    min_distance = float("inf")
    for dest in dests:
        distance = abs(current_x - dest.position.x) + abs(current_y - dest.position.y)
        if distance < min_distance:
            closest = dest
            min_distance = distance
    return closest

def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y
