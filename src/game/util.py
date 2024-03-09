from .models import Position


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = dest_x - current_x
    delta_y = dest_y - current_y

    if delta_x == 0 and delta_y == 0:
        return (0, 0)  # Already at the destination

    if abs(delta_x) > abs(delta_y):
        delta_x = clamp(delta_x, -1, 1)
        delta_y = 0
    else:
        delta_x = 0
        delta_y = clamp(delta_y, -1, 1)

    return (delta_x, delta_y)

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y
