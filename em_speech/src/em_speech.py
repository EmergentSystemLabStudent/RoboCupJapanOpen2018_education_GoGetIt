#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
#from gtts import gTTS
#import os
import pyttsx


class Speech(object):

    def EnSpeechCallback(self, msg):
        #tts = gTTS(text=msg.data, lang='en')
        #tts.save("speech.mp3")
        #os.system("mpg321 speech.mp3")
	engine = pyttsx.init()
	engine.say(text=msg.data)
	engine.runAndWait()
        print 'robot said "%s"' % msg.data

    def __init__(self):
        rospy.Subscriber("/edu/text2speech/en", String, self.EnSpeechCallback)

if __name__ == '__main__':
    rospy.init_node('em_speech', anonymous=True)
    msg = Speech()
    rospy.spin()
