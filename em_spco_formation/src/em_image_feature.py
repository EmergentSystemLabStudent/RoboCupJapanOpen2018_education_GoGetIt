#! /usr/bin/env python

from __init__ import *

import glob
from sensor_msgs.msg import Image
class GetImageFeature(object):

    # callback for word recognition
    def sycle_callback(self, hoge):
        fw = open(self.IMAGE_FOLDER + "/feature_vector/" + str(hoge.data) + ".txt",'w')
        for rank in xrange(1000):
            fw.write('%d %d\n' % (rank, 0))
        fw.close()
    def __init__(self):

        rospy.Subscriber("/em/spco_formation/sycle", Int32, self.sycle_callback, queue_size=1)

        self.IMAGE_FOLDER = DATASET_FOLDER + TRIALNAME
        self.layer = 'prob' #'fc6wi'

if __name__ == '__main__':

    rospy.init_node('GetImageFeature', anonymous=True)
    hoge = GetImageFeature()
    rospy.spin()
