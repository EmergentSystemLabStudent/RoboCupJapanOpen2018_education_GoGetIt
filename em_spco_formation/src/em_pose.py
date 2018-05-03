#! /usr/bin/env python

from __init__ import *

from geometry_msgs.msg import Point, PoseStamped

p = subprocess.Popen("rm -rf " + DATASET_FOLDER + TRIALNAME, shell=True)
sleep(1)
p = subprocess.Popen("mkdir -p " + DATASET_FOLDER + TRIALNAME + "/image/", shell=True)
p = subprocess.Popen("mkdir -p " + DATASET_FOLDER + TRIALNAME + "/feature_vector/", shell=True)
p = subprocess.Popen("mkdir -p " + DATASET_FOLDER + TRIALNAME + "/feature_rank/", shell=True)
p = subprocess.Popen("mkdir -p " + DATASET_FOLDER + TRIALNAME + "/position_data/", shell=True)
p = subprocess.Popen("mkdir -p " + DATASET_FOLDER + TRIALNAME + "/word/", shell=True)
print "mkdir "+ DATASET_FOLDER + TRIALNAME

class GetPose(object):

    # callback for word recognition
    def sycle_callback(self, hoge):

        fp = open(self.POSE_FOLDER + str(hoge.data) + ".txt",'w')
        fp.write(str(self.pose.x) + " " + str(self.pose.y) + "\n" + str(self.sin) + " " + str(self.cos))
        fp.close()

        print "[GetPose] " + str(self.pose.x) + " " + str(self.pose.y) + "\n" + str(self.sin) + " " + str(self.cos)

    # hold self pose
    def pose_callback(self, hoge):

        self.pose = hoge.pose.position
        orientation = hoge.pose.orientation

        self.sin = 2 * orientation.w * orientation.z
        self.cos = orientation.w * orientation.w - orientation.z * orientation.z

    def __init__(self):

        rospy.Subscriber(POSE_TOPIC, PoseStamped, self.pose_callback, queue_size=1)
        rospy.Subscriber("/em/spco_formation/sycle", Int32, self.sycle_callback, queue_size=1)

        self.POSE_FOLDER = DATASET_FOLDER + TRIALNAME + "/position_data/"
        self.count = 0

if __name__ == '__main__':

    rospy.init_node('GetPose', anonymous=True)
    hoge = GetPose()
    rospy.spin()
