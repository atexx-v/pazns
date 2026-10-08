import math


def target_from_variant(start_xy, delta_x, delta_y):
    return (start_xy[0] - delta_x, start_xy[1] - delta_y)


def distance_and_direction(position_xy, target_xy):
    dx = target_xy[0] - position_xy[0]
    dy = target_xy[1] - position_xy[1]
    distance = math.hypot(dx, dy)
    if distance < 1e-9:
        return 0.0, (0.0, 0.0)
    return distance, (dx / distance, dy / distance)


def speed_for_distance(distance, kp, max_speed):
    # швидкість пропорційна відстані, тому дрон сповільнюється біля цілі
    return min(max_speed, kp * distance)


def velocity_command(position_xy, target_xy, kp, max_speed):
    distance, (ux, uy) = distance_and_direction(position_xy, target_xy)
    speed = speed_for_distance(distance, kp, max_speed)
    return (ux * speed, uy * speed)


def position_error(actual_xy, target_xy):
    return math.hypot(actual_xy[0] - target_xy[0], actual_xy[1] - target_xy[1])
