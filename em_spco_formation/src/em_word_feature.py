#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import *

class GetWordFeature(object):

    # callback for word recognition
    def speech_callback(self, hoge):

        self.count += 1
        fp = open(self.WORD_FOLDER + "/word/" + str(self.count) + ".txt",'w')
        fp.write(hoge.data + '\n')
        fp.close()

        # publish sycle
        self.pub_sycle.publish(self.count)
        print "[GetWordFeature] write to txt : " + hoge.data

        if hoge.data not in self.word_list:
            self.word_list.append(hoge.data)

    # callback for finish topic
    def finish_callback(self, hoge):

        fp = open(self.WORD_FOLDER + "/space_name.txt",'w')
        for x in xrange(len(self.word_list)):
            fp.write(self.word_list[x] + '\n')
        fp.close()

        fp = open(self.WORD_FOLDER + "/Environment_parameter.txt",'w')
        fp.write('Max_x_value_of_map 10\n')
        fp.write('Max_y_value_of_map 10\n')
        fp.write('Min_x_value_of_map -10\n')
        fp.write('Min_y_value_of_map -10\n')
        fp.write('Number_of_place %d\n' % len(self.word_list))
        fp.write('Initial_data_number 1\n')
        fp.write('Last_data_number %d\n' % self.count)
        fp.close()

        # learning
        if hoge.data == 1:
            p = subprocess.Popen("python em_spcof_learning_orig.py", shell=True)

    def __init__(self):

        self.pub_sycle = rospy.Publisher("/em/spco_formation/sycle", Int32, queue_size=1)
        rospy.Subscriber(VOCAB_TOPIC, String, self.speech_callback, queue_size=1)
        rospy.Subscriber(FIN_TOPIC, Int32, self.finish_callback, queue_size=1)

        self.count = 0
        self.WORD_FOLDER = DATASET_FOLDER + TRIALNAME

        self.word_list = []

if __name__ == '__main__':

    rospy.init_node('GetWordFeature', anonymous=True)
    hoge = GetWordFeature()
    rospy.spin()
