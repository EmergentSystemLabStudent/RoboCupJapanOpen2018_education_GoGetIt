#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import os
import math
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist

class DoorOpen(object):

    def ScanCallback(self, msg):

        door_distance = 1.0
        center = len(msg.ranges)/2

        #depth判定する幅の半分の値を入れる
        rad = math.atan2(0.25,door_distance)
        #print rad

        range_i = rad / msg.angle_increment
        #print range_i

        count = 0
        mean = 0

        for i in range(int(-range_i), int(range_i)):
            mean += msg.ranges[center+i]
            count += 1
        mean /= count

        #door is open
        if mean > door_distance:
            print "true"
            self.door_open_signal.publish(True)

            r = rospy.Rate(100);
            move_cmd = Twist()
            move_cmd.linear.x = 0.2
	    i=0
            while not rospy.is_shutdown():
            	self.cmd_vel.publish(move_cmd)
            	r.sleep()
            	i=i+1
            	if i==1000:
            		break
            print "enter the arena"

            os.system('rosnode kill /em_door_open')

        #door is close
        else:
            #print "false"
            self.door_open_signal.publish(False)


    def __init__(self):
        self.door_open_signal = rospy.Publisher("/door/open", Bool, queue_size=10)
	self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=1)
        rospy.Subscriber("/scan",LaserScan,self.ScanCallback, queue_size=10)


if __name__ == '__main__':
    rospy.init_node('em_door_open', anonymous=True)
    msg = DoorOpen()
    rospy.spin()

