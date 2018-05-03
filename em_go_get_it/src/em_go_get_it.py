#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int32
from geometry_msgs.msg import PoseStamped, Point
import actionlib
from actionlib_msgs.msg import GoalStatus
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import random

class Go_Get_It(object):

    #actionでゴールを与える
    def ReturnMove(self):
        cli = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        cli.wait_for_server()
        self.start_pos.header.stamp = rospy.Time.now()
        self.start_pos.header.frame_id = "map"
        goal = MoveBaseGoal()
        goal.target_pose = self.start_pos
        cli.send_goal(goal)
        cli.wait_for_result()
        action_state = cli.get_state()
        if action_state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Navigation Succeeded.")
            if self.test_count == 1:
                self.Text2Speech("I arrive at start position and can start test phase..")
                self.bring_me = True
            elif self.test_count >= 2:
                self.Text2Speech("Please give me the next command.")
                self.bring_me = True


    #音声認識結果の処理をする
    def Speech2TextCallback(self, msg):
        text = msg.data
        print '\tYou said "%s"' % text

        #小文字に変換
        text = text.lower()

        #ハイフン除去
        text = text.replace("-", " ")

        text = text.replace("the ", " ")
        text = text.replace("a ", " ")
        text = text.replace("an ", " ")

        #スペース複数個を1つにする
        text = text.replace("    ", " ")
        text = text.replace("   ", " ")
        text = text.replace("  ", " ")

        self.Speech2Text(text)


    #誤認識処理済みの音声認識結果
    def Speech2Text(self, text):
        print '\t=======> "%s"' % text

        #Traning PhaseのFollow me
        if self.follow_me == True:
            #Follow me一時停止
            if text.find("stop follow me") != -1:
                self.follow_me_pub.publish(False)
                self.Text2Speech("I stop following you.")
            #Follow me開始
            elif text.find("follow me") != -1:
                self.follow_me_pub.publish(True)
                self.Text2Speech("I'm following you.")
                self.training = True

        #Traning Phaseの場所概念学習
        if self.training == True:
            #Test Phaseの開始位置を記憶
            if text.find("start position is here") != -1:
                self.start_pos.pose.position.x = self.current_pos.pose.position.x
                self.start_pos.pose.position.y = self.current_pos.pose.position.y
                self.start_pos.pose.position.z = self.current_pos.pose.position.z
                self.start_pos.pose.orientation.x = self.current_pos.pose.orientation.x
                self.start_pos.pose.orientation.y = self.current_pos.pose.orientation.y
                self.start_pos.pose.orientation.z = self.current_pos.pose.orientation.z
                self.start_pos.pose.orientation.w = self.current_pos.pose.orientation.w
                print self.start_pos
                self.Text2Speech("OK, I remember the start position.")
            #教示された場所の名前をオペレータに確認する発話
            elif text.find("here is") != -1:
                self.vocab = text.replace("here is ", "")
                self.Text2Speech("OK, I remember the " + self.vocab + ".")
                if (self.vocab not in self.vocab_list) == True:
                    self.vocab_list.append(self.vocab)
                self.spco_vocab_pub.publish(self.vocab)
            #学習を開始
            elif text.find("learn spatial concept") != -1:
                self.spco_finish_pub.publish(1)
                #self.Text2Speech("I'm learning spatial concept now.")
            #Follow me終了、Test Phaseの開始位置に移動
            elif text.find("return to start position") != -1:
                self.training = False
                self.test = True
                self.follow_me_pub.publish(False)
                self.follow_me = False
                self.Text2Speech("I return to start position.")
                print self.start_pos
                self.ReturnMove()

        #Test Phase
        elif self.test == True:
            #未知な場所の名前を既知な名前に変換
            text = text.replace("", "")






            if self.bring_me == True and text.find("bring me") != -1:
                self.vocab_pub = False
                for i in range(len(self.vocab_list)):
                    #場所の名前リストにあれば、その場所に移動する
                    if text.find(self.vocab_list[i]) != -1:
                        self.spco_name = self.vocab_list[i]
                        self.Text2Speech("I go to " + self.spco_name + ".")
                        self.spco_name_pub.publish(self.spco_name)
                        self.vocab_pub = True
                        break
                #場所の名前リストになければ（ランダムに）ひとつずつ選んで、ここでいいかYes or Noで聞き返す(1回目)
                if self.vocab_pub == False:
                    self.random_list = random.sample(self.vocab_list, len(self.vocab_list))
                    self.check_place = 0
                    self.spco_name = self.random_list[self.check_place]
                    self.Text2Speech("Can I go to " + self.spco_name + "? Yes or No.")
                    self.bring_me = False
            #Yes or No
            elif self.bring_me == False and self.vocab_pub == False:
                if text.find("yes") != -1:
#                    self.spco_name = self.random_list[self.check_place]
                    self.Text2Speech("I go to " + self.spco_name + ".")
                    self.spco_name_pub.publish(self.spco_name)
                elif text.find("no") != -1:
                    self.check_place += 1
                    self.spco_name = self.random_list[self.check_place]
                    self.Text2Speech("Can I go to " + self.spco_name + "? Yes or No.")
                    self.bring_me = False


    #発話（英語）
    def Text2Speech(self, text):
        print '\trobot said "%s"' % text
        msg = String()
        msg.data = text
        rospy.sleep(2.0)
        self.edu_en_pub.publish(msg)

    #DoorOpen後,前進
    def DoorOpenCallback(self, msg):
        if msg.data == True:
            self.Text2Speech("I enter the arena.")
            self.follow_me = True

    #Test Phaseで物体の場所まで移動完了、start positionまで戻る
    def SpcoGoalCallback(self, msg):
        #Test Phaseで物体の場所まで移動完了、start positionまで戻る
        if msg.data == True and self.test == True:
            self.move_count = 0
            self.Text2Speech("I arrive at the " + self.spco_name + ".")
            rospy.sleep(1.0)
            self.Text2Speech("I cannot take the object, so I return to start position.")
            self.test_count += 1
            self.ReturnMove()
        #Test Phaseで移動失敗、再度移動命令を出す
        elif msg.data == False and self.test == True:
            if self.move_count < 3:
                self.move_count += 1
                self.Text2Speech("I failed to create the route to " + self.spco_name + ". So I create it again.")
                self.spco_name_pub.publish(self.spco_name)
            elif self.move_count == 3:
                self.move_count = 0
                self.Text2Speech("I cannnot arrive at " + self.spco_name)
                self.ReturnMove()

    #自己位置を取得
    def GlobalPoseCallback(self, msg):
        self.current_pos.pose = msg.pose

    #場所概念学習終了
    def LearnedCallback(self, msg):
        self.Text2Speech("I finish learning spatial concept. Number of spatial concept is " + str(msg.data) + ".")

    def __init__(self):
        self.follow_me = False
        self.training = False
        self.vocab_list = []
        self.test = False
        self.bring_me = False
        self.move_count = 0
        self.vocab_pub = False
        self.check_place = 0
        self.test_count = 1
        self.start_pos = PoseStamped()
        self.current_pos = PoseStamped()

        #self.edu_en_pub = rospy.Publisher("/rospeex/text2speech/en", String, queue_size=1)
        self.edu_en_pub = rospy.Publisher("/edu/text2speech/en", String, queue_size=1)
        self.follow_me_pub = rospy.Publisher("/em/follow_me", Bool, queue_size=1)
        self.spco_finish_pub = rospy.Publisher("/em/spco_formation/finish", Int32, queue_size=1)
        self.spco_vocab_pub = rospy.Publisher("/em/spco_formation/vocab", String, queue_size=1)
        self.spco_name_pub = rospy.Publisher("/em/spco/name_sub", String, queue_size=1)

        #rospy.Subscriber("/rospeex/speech2text/en", String, self.Speech2TextCallback)
        rospy.Subscriber("/julius/speech2text/en", String, self.Speech2TextCallback)
        rospy.Subscriber("/door/open", Bool, self.DoorOpenCallback)
        rospy.Subscriber("/spco/goal/flag", Bool, self.SpcoGoalCallback)
        rospy.Subscriber("/best_pose", PoseStamped, self.GlobalPoseCallback)
        rospy.Subscriber("/em/spco_formation/learned", Int32, self.LearnedCallback)

if __name__ == '__main__':
    rospy.init_node('em_go_get_it_main', anonymous=True)
    msg = Go_Get_It()
    rospy.spin()
