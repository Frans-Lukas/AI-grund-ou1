import json
from Point import *


def read_json_file_to_list(file):
    with open(file, 'r') as f:
        array = json.load(f)

    point_list = []

    for element in array:
        orientation = get_orientation(element)
        position = get_position(element)
        timestamp = get_time_stamp(element)
        point = create_point(orientation, position, timestamp)
        point_list.append(point)

    return point_list


def get_time_stamp(element):
    return element["Timestamp"]


def get_position(element):
    return element["Pose"]["Position"]


def get_orientation(element):
    return element["Pose"]["Orientation"]


def create_point(orientation, position, timestamp):
    return Point(create_orientation(orientation), create_position(position), timestamp)


def create_orientation(orientation):
    return Orientation(orientation["W"], orientation["X"], orientation["Y"], orientation["Z"])


def create_position(position):
    return Position(position["X"], position["Y"], position["Z"])
