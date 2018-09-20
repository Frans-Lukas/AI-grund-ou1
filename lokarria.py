#!/usr/bin/env python3

import myJsonParser as myJsonParser
import math
from RestLokarria import *
from Point import *
import numpy as np

MRDS_URL = 'localhost:50000'

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}


class UnexpectedResponse(Exception): pass


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return 0.2


def angle_between(v1, v2):
    x1 = v1[0]
    x2 = v2[0]
    y1 = v1[1]
    y2 = v2[1]

    dot = x1 * x2 + y1 * y2  # dot product
    det = x1 * y2 - y1 * x2  # determinant
    angle = atan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
    return angle


def get_angle(p1, p2):
    return math.atan2(p1.x - p2.x, p1.y - p2.y)


def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def test_angle():
    print("000 and 010")
    print(math.degrees(angle_between([0, 0, 0], [0, 1, 0])))
    print(math.degrees(angle_between([1, 0, 0], [0, 1, 0])))
    print(math.degrees(angle_between([0, 1, 0], [0, 1, 0])))
    print(math.degrees(angle_between([0, 0, 0], [1, 0, 0])))
    print(math.degrees(angle_between([0, 1, 0], [1, 0, 0])))
    print(math.degrees(angle_between([1, 0, 0], [1, 0, 0])))


def get_angular_speed_from_angle(degree_angle):
    return 0.2


def heading_to_point(robot_heading):
    return Position(robot_heading.x, robot_heading.y, robot_heading.z)


def get_heading_position():
    heading = getHeading()
    return Position(heading['X'], heading['Y'], 0)


def choose_new_point_from_lookahead(current_point, robot_position, point_list, lookahead):
    point_candidate = current_point
    for point in point_list:
        if point.timestamp > current_point.timestamp:
            d1 = get_distance(point.position, robot_position)
            d2 = get_distance(point_candidate.position, robot_position)
            if lookahead > d1 > d2:
                point_candidate = point
    return point_candidate


# 1. Ta ut heading vector A
# 2. Ta ut vector vi ska till B
# 3. Normalisera vektorerna A och B ( Längden ska vara 1 )
# 4. Ta reda på hur många grader man behöver vända vektor A för att den ska lägga sig på X-axel.
# 5. Rotera även vektor B med lika många grader
# 6. arcsin(By) ger om det är + lr -
# 7. arcos(Bx) ger vinkel

def points_to_vector(p1, p2):
    return [p2.x - p1.x, p2.y - p1.y]


def vector_to_position(v):
    return Position(v[0], v[1], 0)


def position_to_vector(position):
    return [position.x, position.y]


def normalize_vector(v):
    return [x / np.linalg.norm(v) for x in v]


def rad_to_rotation_matrix(rad):
    c, s = np.cos(rad), np.sin(rad)
    return np.array(((c, -s), (s, c)))


if __name__ == '__main__':
    test_angle()
    point_list = myJsonParser.read_json_file_to_list("Path-to-bed.json")
    point_list.sort(key=lambda x: x.timestamp, reverse=False)

    target_point = point_list[0]
    lookahead = 1
    while True:
        heading_vector = position_to_vector(get_heading_position())

        robot_position = get_robot_position()

        target_point = choose_new_point_from_lookahead(target_point, robot_position, point_list, lookahead)

        target_vector = points_to_vector(target_point.position, robot_position)

        target_normalized_vector = normalize_vector(target_vector)

        angle_between_heading_and_x = angle_between([1, 0, 0], [heading_vector[0], heading_vector[1], 0])

        angle_between_heading_and_x = math.radians(math.degrees(angle_between_heading_and_x) + 90)

        rotation_matrix = rad_to_rotation_matrix(angle_between_heading_and_x)

        target_normalized_and_rotated_vector = np.matmul(rotation_matrix, target_normalized_vector)

        left_or_right = np.arcsin(target_normalized_and_rotated_vector[1])

        rotation_angle = np.arccos(target_normalized_and_rotated_vector[0])

        print(math.degrees(rotation_angle))

        speed = 0.2
        if left_or_right > 0:
            postSpeed(get_angular_speed_from_angle(math.degrees(rotation_angle)), speed)
        else:
            postSpeed(-get_angular_speed_from_angle(math.degrees(rotation_angle)), speed)
        time.sleep(0.1)
