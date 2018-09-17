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
    return math.hypot(p1.y - p2.y, p1.x - p2.x)


def test_angle():
    print(math.degrees(get_angle(Position(0, 0, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(1, 0, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(0, 1, 0), Position(0, 1, 0))))
    print(math.degrees(get_angle(Position(0, 0, 0), Position(1, 0, 0))))
    print(math.degrees(get_angle(Position(0, 1, 0), Position(1, 0, 0))))
    print(math.degrees(get_angle(Position(1, 0, 0), Position(1, 0, 0))))


def get_angular_speed_from_angle(degree_angle):
    return 0.4


def heading_to_point(robot_heading):
    return Position(robot_heading.x, robot_heading.y, robot_heading.z)


def get_heading_point():
    heading = getHeading()
    return Position(heading['X'], heading['Y'], 0)


def choose_new_point_from_lookahead(current_point, robot_point, point_list, lookahead):
    point_candidate = current_point
    for point in point_list:
        if (point.timestamp > current_point.timestamp):
            if (get_distance(robot_point, point.position) < lookahead and
                        get_distance(robot_point, point.position) > get_distance(robot_point,
                                                                                 point_candidate.position)):
                point_candidate = point
    return point_candidate


if __name__ == '__main__':
    test_angle()
    point_list = myJsonParser.read_json_file_to_list("Path-around-table-and-back.json")

    target_point = point_list[0]
    while True:
        # robot_position = get_robot_position()
        target_point = choose_new_point_from_lookahead(target_point, get_heading_point(), point_list, 1)
        robot_heading = getHeading()
        robot_pos = get_robot_position()
        print("distance: {}".format(get_distance(target_point.position, robot_pos)))


        robot_vector = [robot_heading['Y'], robot_heading['X']]
        point_vector = [target_point.position.y, target_point.position.x]

        cross = np.cross(robot_vector, point_vector)
        print("cross: {}".format(cross))

        angle_to_first_point = angle_between(robot_vector, point_vector)
        degree_angle = math.degrees(angle_to_first_point)
        # print('Current heading vector: X:{X:.3}, Y:{Y:.3}'.format(**getHeading()))
        if cross < 0:
            postSpeed(-get_angular_speed_from_angle(degree_angle), 0)
        else:
            postSpeed(get_angular_speed_from_angle(degree_angle), 0)
        time.sleep(0.2)

        # try:
        #     print('Telling the robot to go straight ahead.')
        #     pos = get_robot_position()
        # except UnexpectedResponse as ex:
        #     print('Unexpected response from server when sending speed commands:', ex)
        #
        # try:
        #     laser = getLaser()
        #     laserAngles = getLaserAngles()
        #     print('The rightmost laser beam has angle %.3f deg from x-axis (streight forward) and distance %.3f meters.' % (
        #         laserAngles[0], laser['Echoes'][0]
        #     ))
        #     print('Beam 1: %.3f Beam 269: %.3f Beam 270: %.3f' % (
        #         laserAngles[0] * 180 / pi, laserAngles[269] * 180 / pi, laserAngles[270] * 180 / pi))
        # except UnexpectedResponse as ex:
        #     print('Unexpected response from server when reading laser data:', ex)
        #
        # try:
        #     pose = get_robot_position()
        #     print('Current position: ', pose['Pose']['Position'])
        #     for t in range(30):
        #         print('Current heading vector: X:{X:.3}, Y:{Y:.3}'.format(**getHeading()))
        #         laser = getLaser()
        #         print('Distance %.3f meters.' % (laser['Echoes'][135]))
        #         if (laser['Echoes'][135] < 0.3):
        #             print('Danger! Brace for impact! Hit the brakes!')
        #             response = postSpeed(0, -0.1)
        #         time.sleep(1)
        # except UnexpectedResponse as ex:
        #     print('Unexpected response from server when reading position:', ex)
