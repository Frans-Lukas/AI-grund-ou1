# !/usr/bin/env python3
"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 

Author: Erik Billing (billing@cs.umu.se)

Updated by Ola Ringdahl 2014-09-11
Updated by Lennart Jern 2016-09-06 (converted to Python 3)
Updated by Filip Allberg and Daniel Harr 2017-08-30 (actually converted to Python 3)
"""

MRDS_URL = 'localhost:50000'

import http.client, json, time, myJsonParser
from math import sin, cos, pi, atan2

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}


class UnexpectedResponse(Exception): pass


def postSpeed(angularSpeed, linearSpeed):
    """Sends a speed command to the MRDS server"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    params = json.dumps({'TargetAngularSpeed': angularSpeed, 'TargetLinearSpeed': linearSpeed})
    mrds.request('POST', '/lokarria/differentialdrive', params, HEADERS)
    response = mrds.getresponse()
    status = response.status
    # response.close()
    if status == 204:
        return response
    else:
        raise UnexpectedResponse(response)


def getLaser():
    """Requests the current laser scan from the MRDS server and parses it into a dict"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET', '/lokarria/laser/echoes')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        return json.loads(laserData.decode())
    else:
        return response


def get_robot_position():
    """Reads the current position and orientation from the MRDS"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET', '/lokarria/localization')
    response = mrds.getresponse()
    if (response.status == 200):
        poseData = response.read()
        response.close()
        array = json.loads(poseData.decode())
        position = myJsonParser.get_position(array)
        return myJsonParser.create_position(position)
    else:
        return UnexpectedResponse(response)



def getLaserAngles():
    """Requests the current laser properties from the MRDS server and parses it into a dict"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET', '/lokarria/laser/properties')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        properties = json.loads(laserData.decode())
        beamCount = int((properties['EndAngle'] - properties['StartAngle']) / properties['AngleIncrement'])
        a = properties['StartAngle']  # +properties['AngleIncrement']
        angles = []
        while a <= properties['EndAngle']:
            angles.append(a)
            a += pi / 180  # properties['AngleIncrement']
        # angles.append(properties['EndAngle']-properties['AngleIncrement']/2)
        return angles
    else:
        raise UnexpectedResponse(response)


def getPose():
    """Reads the current position and orientation from the MRDS"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET', '/lokarria/localization')
    response = mrds.getresponse()
    if (response.status == 200):
        poseData = response.read()
        response.close()
        return json.loads(poseData.decode())
    else:
        return UnexpectedResponse(response)


def heading(q):
    return rotate(q, {'X': 1.0, 'Y': 0.0, "Z": 0.0})


def rotate(q, v):
    return vector(qmult(qmult(q, quaternion(v)), conjugate(q)))


def quaternion(v):
    q = v.copy()
    q['W'] = 0.0;
    return q


def vector(q):
    v = {}
    v["X"] = q["X"]
    v["Y"] = q["Y"]
    v["Z"] = q["Z"]
    return v


def conjugate(q):
    qc = q.copy()
    qc["X"] = -q["X"]
    qc["Y"] = -q["Y"]
    qc["Z"] = -q["Z"]
    return qc


def qmult(q1, q2):
    q = {}
    q["W"] = q1["W"] * q2["W"] - q1["X"] * q2["X"] - q1["Y"] * q2["Y"] - q1["Z"] * q2["Z"]
    q["X"] = q1["W"] * q2["X"] + q1["X"] * q2["W"] + q1["Y"] * q2["Z"] - q1["Z"] * q2["Y"]
    q["Y"] = q1["W"] * q2["Y"] - q1["X"] * q2["Z"] + q1["Y"] * q2["W"] + q1["Z"] * q2["X"]
    q["Z"] = q1["W"] * q2["Z"] + q1["X"] * q2["Y"] - q1["Y"] * q2["X"] + q1["Z"] * q2["W"]
    return q


def getHeading():
    """Returns the XY Orientation as a heading unit vector"""
    return heading(getPose()['Pose']['Orientation'])


if __name__ == '__main__':
    print('Sending commands to MRDS server', MRDS_URL)
    try:
        print('Telling the robot to go straight ahead.')
        response = postSpeed(0, 0.5)
        print('Waiting for a while...')
        time.sleep(3)
        print('Telling the robot to go in a circle.')
        response = postSpeed(0.9, 0.1)
    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)

    try:
        laser = getLaser()
        laserAngles = getLaserAngles()
        print('The rightmost laser bean has angle %.3f deg from x-axis (streight forward) and distance %.3f meters.' % (
            laserAngles[0], laser['Echoes'][0]
        ))
        print('Beam 1: %.3f Beam 269: %.3f Beam 270: %.3f' % (
        laserAngles[0] * 180 / pi, laserAngles[269] * 180 / pi, laserAngles[270] * 180 / pi))
    except UnexpectedResponse as ex:
        print('Unexpected response from server when reading laser data:', ex)

    try:
        pose = getPose()
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
