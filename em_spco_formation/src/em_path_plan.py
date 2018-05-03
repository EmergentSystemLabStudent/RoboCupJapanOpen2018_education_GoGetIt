#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import actionlib
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Point, PoseStamped, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import Bool
import rospy
import tf.transformations
import random

class PathPlan(object):

    #actionでゴールを与える
    def MoveCallback(self, msg):
        goal_x = msg.pose.position.x
        goal_y = msg.pose.position.y
        print "Goal Subscribe\n"
        print "Move to (" + str(goal_x) + " , " + str(goal_y) + ")"

        cli = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        cli.wait_for_server()
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = "map"
        pose.pose.position = Point(goal_x, goal_y, 0)
        pose.pose.orientation.x = 0
        pose.pose.orientation.y = 0
        pose.pose.orientation.z = msg.pose.orientation.z
        pose.pose.orientation.w = msg.pose.orientation.w

        goal = MoveBaseGoal()
        goal.target_pose = pose

        cli.send_goal(goal)
        cli.wait_for_result()

        action_state = cli.get_state()
        if action_state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Navigation Succeeded.")
            self.goal_signal.publish(True)
        else:
            rospy.loginfo("Navigation Failed.")
            self.goal_signal.publish(False)

    def __init__(self):
        self.goal_signal = rospy.Publisher("/spco/goal/flag", Bool, queue_size=1)
        rospy.Subscriber("/em/spco/place_pub", PoseStamped, self.MoveCallback)

if __name__ == '__main__':
    rospy.init_node('em_spco_path_plan', anonymous=True)
    msg = PathPlan()
    rospy.spin()

