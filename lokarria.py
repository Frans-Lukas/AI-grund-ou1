#!/usr/bin/env python3

import myJsonParser as myJsonParser
from RestLokarria import *
MRDS_URL = 'localhost:50000'

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}


class UnexpectedResponse(Exception): pass


if __name__ == '__main__':
    point_list = myJsonParser.read_json_file_to_list("Path-around-table-and-back.json")
    first_point = point_list[0]


    print('Sending commands to MRDS server', MRDS_URL)
    try:
        print('Telling the robot to go straight ahead.')
        pos = get_robot_position()
    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)

    try:
        laser = getLaser()
        laserAngles = getLaserAngles()
        print('The rightmost laser beam has angle %.3f deg from x-axis (streight forward) and distance %.3f meters.' % (
            laserAngles[0], laser['Echoes'][0]
        ))
        print('Beam 1: %.3f Beam 269: %.3f Beam 270: %.3f' % (
            laserAngles[0] * 180 / pi, laserAngles[269] * 180 / pi, laserAngles[270] * 180 / pi))
    except UnexpectedResponse as ex:
        print('Unexpected response from server when reading laser data:', ex)

    try:
        pose = get_robot_position()
        print('Current position: ', pose['Pose']['Position'])
        for t in range(30):
            print('Current heading vector: X:{X:.3}, Y:{Y:.3}'.format(**getHeading()))
            laser = getLaser()
            print('Distance %.3f meters.' % (laser['Echoes'][135]))
            if (laser['Echoes'][135] < 0.3):
                print('Danger! Brace for impact! Hit the brakes!')
                response = postSpeed(0, -0.1)
            time.sleep(1)
    except UnexpectedResponse as ex:
        print('Unexpected response from server when reading position:', ex)
