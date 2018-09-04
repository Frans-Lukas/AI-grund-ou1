#!/usr/bin/env python3

MRDS_URL = 'localhost:50000'

from lokarriaexample3 import *;
from Point import *;

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}


class UnexpectedResponse(Exception): pass


def readJsonFileToList(file):
    orientation = Orientation(1,2,3,4)
    position = Position(0,0,0)
    point = Point(orientation, position, 0)
    print('{0} and {1} and {2}'.format(point.orientation.x, point.orientation.z, point.position.x))
    return 0

if __name__ == '__main__':
    readJsonFileToList(0)
    # print('Sending commands to MRDS server', MRDS_URL)
    # try:
    #     print('Telling the robot to go straight ahead.')
    #     response = postSpeed(0, 0.5)
    #     print('Waiting for a while...')
    #     time.sleep(3)
    #     print('Telling the robot to go in a circle.')
    #     response = postSpeed(0.9, 0.1)
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
    #     pose = getPose()
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
