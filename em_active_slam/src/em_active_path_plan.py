#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point, PoseStamped, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import Bool
import rospy
from geometry_msgs.msg import Twist
import tf.transformations
import random
import os

class PathPlan(object):

    #actionでゴールを与える
    def MoveCallback(self, msg):
        goal_x = msg.pose.position.x
        goal_y = msg.pose.position.y
        #rad = math.atan2(goal_y,goal_x)
        rad = random.uniform(-(math.pi),(math.pi))
        print "Goal Subscribe\n"
        print "Move to (" + str(goal_x) + " , " + str(goal_y) + " , " + str(rad*180/math.pi) + ")"

        cli = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        cli.wait_for_server()
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = "map"
        pose.pose.position = Point(goal_x, goal_y, 0)
        quat = tf.transformations.quaternion_from_euler(0, 0, rad)
        pose.pose.orientation = Quaternion(*quat)

        goal = MoveBaseGoal()
        goal.target_pose = pose

        cli.send_goal(goal)
        cli.wait_for_result()

        action_state = cli.get_state()
        if action_state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Navigation Succeeded.")
            self.goal_signal.publish(True)

    #ActiveSLAM終了、(2,0)に戻ってnode kill
    def FinishCallback(self, msg):
        if msg.data == True:
            """
            cli = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
            cli.wait_for_server()
            pose = PoseStamped()
            pose.header.stamp = rospy.Time.now()
            pose.header.frame_id = "map"
            pose.pose.position = Point(2, 0, 0)
            quat = tf.transformations.quaternion_from_euler(0, 0, 0)
            pose.pose.orientation = Quaternion(*quat)

            goal = MoveBaseGoal()
            goal.target_pose = pose

            cli.send_goal(goal)
            cli.wait_for_result()

            action_state = cli.get_state()
            if action_state == GoalStatus.SUCCEEDED:
                rospy.loginfo("Navigation Succeeded.")
                self.goal_signal.publish(True)
            """

            os.system('rosnode kill /em_frontier_approach')
            os.system('rosnode kill /em_active_path_plan')

    #Door Open後2.0[m]前進
    def DoorOpenCallback(self, msg):
        if msg.data == True:
            print "door_open"
            #os.system('rosnode kill /hector_mapping') #ActiveSLAM再起動
            #rospy.sleep(10)
            #omni_base.go_rel(2.0, 0.0, 0.0, 100.0)
            self.active_signal.publish(True)
            r = rospy.Rate(100);
            move_cmd = Twist()
            move_cmd.linear.x = 0.2
	    i=0
            while not rospy.is_shutdown():
            	self.cmd_vel.publish(move_cmd)
            	r.sleep()
            	i=i+1
            	if i==500:
            		break
            print "enter the arena"

    def __init__(self):
        self.goal_signal = rospy.Publisher("/goal/flag", Bool, queue_size=1)
        self.active_signal = rospy.Publisher("/active/start", Bool, queue_size=1)
	self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=1)
        rospy.Subscriber("/active/goal", PoseStamped, self.MoveCallback)
        rospy.Subscriber("/active/finish", Bool, self.FinishCallback)
        rospy.Subscriber("/door/open", Bool, self.DoorOpenCallback)

if __name__ == '__main__':
    rospy.init_node('em_active_path_plan', anonymous=True)
    msg = PathPlan()
    rospy.spin()

