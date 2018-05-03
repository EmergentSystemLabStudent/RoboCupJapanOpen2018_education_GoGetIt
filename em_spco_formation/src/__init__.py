#! /usr/bin/env python

import rospy
import math
import numpy as np
from time import sleep
import sys, subprocess
import os.path
from std_msgs.msg import String
from std_msgs.msg import Int32

TRIALNAME = "trial"

IMAGE_TOPIC = "/camera/rgb/image_raw"
VOCAB_TOPIC = "/em/spco_formation/vocab"
POSE_TOPIC = "/best_pose"
FIN_TOPIC = "/em/spco_formation/finish"
LEARNED_TOPIC = "/em/spco_formation/learned"

DATASET_FOLDER = "../training_data/"
# DATASET_FOLDER = "../data/"
