#!/usr/bin/env python3

import myJsonParser as myJsonParser
from math import sin, cos, radians, degrees, hypot, atan2
from RestLokarria import *
from Point import *
import numpy as np
import time


MRDS_URL = 'localhost:50000'
HEADERS = {"Content-type": "application/json", "Accept": "text/json"}


class UnexpectedResponse(Exception): pass


def angle_between(v1, v2):
    x1 = v1[0]
    x2 = v2[0]
    y1 = v1[1]
    y2 = v2[1]
    dot = x1 * x2 + y1 * y2
    det = x1 * y2 - y1 * x2
    return atan2(det, dot)


def get_distance(p1, p2):
    return hypot(p1.x - p2.x, p1.y - p2.y)


def get_heading_position():
    h = getHeading()
    return Position(h['X'], h['Y'], 0)


def get_index_for_next_lookahead(i, robot_pos, plist, lookahead, length):
    point_candidate = plist[i]
    for x in range(i, length):
        point = plist[x]
        if point.timestamp > point_candidate.timestamp:
            d1 = get_distance(point.position, robot_pos)
            if lookahead < d1:
                return x
    return i


def testing_get_first_position(plist, length, lookahead):
    first_position = plist[0]
    for x in range(length):
        second_position = plist[x]
        if get_distance(first_position.position, second_position.position) > lookahead:
            return x


def points_to_vector(p1, p2):
    return [p2.x - p1.x, p2.y - p1.y]


def position_to_vector(position):
    return [position.x, position.y]


def normalize_vector(v):
    return [x / np.linalg.norm(v) for x in v]


def rotate_point(point, a, center_point=(0, 0)):
    angle_rad = radians(a % 360)
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                 new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point


def get_angular_speed(degree_angle):
    return 2 * (degree_angle / 35)


def get_speed(degree_angle):
    return 1

'''
BEST SPECS HITTILS: 
lookahead : 1
min_distance < 0.95
angular_speed : return 2 * (degree_angle / 30)
speed : 1.65 - (get_angular_speed(degree_angle)/2)
'''
if __name__ == '__main__':
    print('Waiting for robot to start the race...')
    point_list = myJsonParser.read_json_file_to_list("Path-around-table-and-back.json")
    point_list.sort(key=lambda x: x.timestamp)

    list_length = len(point_list)
    lookahead = 1.05
    target_point = point_list[testing_get_first_position(point_list, list_length, lookahead)]
    index = 0
    start = time.time()
    print("Go")
    while True:

        heading_vector = position_to_vector(get_heading_position())
        robot_position = get_robot_position()

        if get_distance(target_point.position, robot_position) < 1:
            index = get_index_for_next_lookahead(index, robot_position, point_list, lookahead, list_length)
            target_point = point_list[index]
            if get_distance(target_point.position, robot_position) <= 1:
                end = time.time()
                postSpeed(0, 0)
                print("Time: " + str((end - start)))
                exit()

        to_point_vector = points_to_vector(robot_position, target_point.position)
        heading_vector = normalize_vector(heading_vector)
        to_point_vector = normalize_vector(to_point_vector)
        angle = degrees(angle_between(heading_vector, [1, 0]))
        to_point_vector = rotate_point(to_point_vector, angle, center_point=(0, 0))
        angle = degrees(np.arccos(to_point_vector[0]))

        if np.arcsin(to_point_vector[1]) > 0:
            postSpeed(get_angular_speed(angle), get_speed(angle))
        else:
            postSpeed(-get_angular_speed(angle), get_speed(angle))
        time.sleep(0.05)
