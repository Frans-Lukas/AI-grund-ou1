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
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def get_angle(p1, p2):
    return math.atan2(p1.x - p2.x, p1.y - p2.y)


def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def test_angle():
    print(math.degrees(get_angle(Position(0, 0, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(1, 0, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(0, 1, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(0, 0, 0), Position(1, 0, 0))))
    print(math.degrees(get_angle(Position(0, 1, 0), Position(1, 0, 0))))
    print(math.degrees(get_angle(Position(1, 0, 0), Position(1, 0, 0))))


def get_angular_speed_from_angle(degree_angle):
    return degree_angle / 180


def heading_to_point(robot_heading):
    return Position(robot_heading.x, robot_heading.y, robot_heading.z)


def get_heading_position():
    heading = getHeading()
    return Position(heading['X'], heading['Y'], 0)


def choose_new_point_from_lookahead(current_point, robot_position, point_list, lookahead):
    point_candidate = current_point
    for point in point_list:
        if point.timestamp > current_point.timestamp:
            dist_between_robot_and_new_point = get_distance(robot_position, point.position)
            dist_between_robot_and_candidate = get_distance(robot_position, point_candidate.position)
            if dist_between_robot_and_new_point > lookahead and dist_between_robot_and_new_point > dist_between_robot_and_candidate:
                point_candidate = point
    return point_candidate


# 1. Ta ut heading vector A
# 2. Ta ut vector vi ska till B
# 3. Normalisera vektorerna A och B ( Längden ska vara 1 )
# 4. Ta reda på hur många grader man behöver vända vektor A för att den ska lägga sig på X-axel.
# 5. Rotera även vektor B med lika många grader
# 6. arcsin(By) ger om det är + lr -
# 7. arcos(Bx) ger vinkel

def position_to_vector(position):
    return [position.x, position.y]


def vector_to_position(v):
    return Position(v[0], v[1], 0)


def normalize_vector(v):
    return [x / np.linalg.norm(v) for x in v]


def rad_to_rotation_matrix(rad):
    c, s = np.cos(rad), np.sin(rad)
    R = np.array(((c, -s), (s, c)))
    return R


if __name__ == '__main__':
    test_angle()
    point_list = myJsonParser.read_json_file_to_list("Path-around-table-and-back.json")

    target_point = point_list[len(point_list) - 1]
    target_vector = target_point.position
    lookahead = 0.1
    while True:
        heading_vector = position_to_vector(get_heading_position())
        robot_position = get_robot_position()
        #target_point = choose_new_point_from_lookahead(target_point, robot_position, point_list, lookahead  )
        print("x: {} y: {}".format(target_point.position.x, target_point.position.y))
        target_vector = position_to_vector(target_point.position)

        target_normalized_vector = normalize_vector(target_vector)
        robot_normalized_vector = normalize_vector(heading_vector)
        angle_between_heading_and_x = get_angle(vector_to_position(robot_normalized_vector),
                                                vector_to_position([1, 0, 0]))
        rotation_matrix = rad_to_rotation_matrix(angle_between_heading_and_x)
        target_normalized_and_rotated_vector = np.matmul(rotation_matrix, target_normalized_vector)
        left_or_right = np.arcsin(target_normalized_and_rotated_vector[1])
        rotation_angle = np.arccos(target_normalized_and_rotated_vector[0])
        if left_or_right < 0:
            postSpeed(get_angular_speed_from_angle(math.degrees(rotation_angle)), 0)
        else:
            postSpeed(-get_angular_speed_from_angle(math.degrees(rotation_angle)), 0)
        time.sleep(0.1)
