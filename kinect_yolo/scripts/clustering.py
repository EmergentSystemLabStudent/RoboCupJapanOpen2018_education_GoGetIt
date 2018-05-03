#!/usr/bin/python
#coding:utf-8
import numpy as np
import rospy
import matplotlib.pyplot as plt
import collections
from std_msgs.msg import Bool
from kinect_yolo.msg import objectxyz
from kinect_yolo.msg import objects
from sklearn.cluster import DBSCAN
from sklearn import metrics
from mpl_toolkits.mplot3d import Axes3D
from decimal import *
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

count = 0
coordinate = np.empty((0,3), float)
object_name = []
state_bool = True

def callback(ob):
    global count
    global coordinate
    global object_name

    #Objectの座標を保存していく
    coordinate = np.append(coordinate, np.array([[ob.x, ob.y, ob.z]]), axis=0)

    #Objectの名前を保存していく
    object_name = np.append(object_name, ob.Class)

    count=count+1
    print count

def check(state):
    global coordinate
    global state_bool

    if(state.data == True and state_bool == True):
        state_bool = False
        sub.unregister()
        calc(coordinate)

def adder():
    global sub
    global sub2
    global pub
    rospy.init_node('clustering', anonymous=True)
    sub = rospy.Subscriber('kinect_yolo/xyz', objectxyz , callback)
    sub2 = rospy.Subscriber('finish', Bool , check)
    pub = rospy.Publisher('string_pub', objects ,queue_size=1)

def scale(X):
    #データ行列Xを属性ごとに標準化したデータを返す 現在調整中
    return X

def calc(coordinate):
    global object_name

    msg_len = objects()

    #標準化(現在調整中)
    X_train = scale(coordinate)

    #eps -> 同クラスタか判定の索敵円半径 min_samples -> クラスタの最低座標数
    db = DBSCAN(eps=0.3, min_samples=3).fit(X_train)

    # db.labels_と同じShapeの配列core_samples_maskを生成
    # db.labels_はクラスタの番号が入っている
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)

    # データ数のサイズでcore_samples_maskを生成、全部Trueで初期化
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    #ノイズはクラスタ数に入れないのでクラスタ数から減らす
    #set関数→同じ数が配列に含まれれば削除する
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print('Estimated number of clusters: %d' % n_clusters_)

    #unique_labels→クラスタ番号の一覧 それを利用してクラスタを塗る際の色配列を生成
    unique_labels = set(labels)

    #クラスタを描画するために色をクラスタの数だけ用意
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    cluster_object = []
    clusterInfo = []

    #ループ用の変数、クラスタ数用意する
    loop = len(unique_labels)

    for num in range(len(labels)):
        if labels[num] == -1 and loop != 0:
            loop = loop -1
            break

    #ここで物体の名前の数をカウントする
    for k in range(loop):
        for la,ob in zip(labels, object_name):
            if k == la and k != -1:
                cluster_object = np.append(cluster_object, ob)
        counter = collections.Counter(cluster_object)
        clusterInfo = np.append(clusterInfo, counter)
        cluster_object = []
        #print counter

    #print clusterInfo

    #for zip ループで複数のリストの要素を取得
    for k, col, info in zip(unique_labels, colors, clusterInfo):
        if k != -1:
            # 今、描画しようとしているクラスタに含まれる座標系を一気に習得
            # class_member_maskに代入
            class_member_mask = (labels == k)


            xyz = X_train[class_member_mask & core_samples_mask]

            sum_pro = 0.0

            for name, value in info.items():
                sum_pro = sum_pro + value
            print "Cluster: " + str(k)

            graph_text = ""

            for name, value in info.items():
                graph_text = graph_text + str(name) + " " + str(round((value / sum_pro * 100.0),2)) + " %"

            #print "-------------------------------------------"
            #print k
            #print "-------------------------------------------"

            #print "xyz[:, 0]"
            #print xyz[:, 0]
            #print "xyz[:, 1]"
            #print xyz[:, 1]
            #print "xyz[:, 2]"
            #print xyz[:, 2]
            #print "len(xyz[:, 0])"
            #print len(xyz[:, 0])
            #print "len(xyz[:, 1])"
            #print len(xyz[:, 1])
            #print "len(xyz[:, 2])"
            #print len(xyz[:, 2])
            #print "-------------------------------------------"
            #print "-------------------------------------------"

            # 平均を習得
            x = sum(xyz[:, 0]) / len(xyz[:, 0])
            y = sum(xyz[:, 1]) / len(xyz[:, 1])
            z = sum(xyz[:, 2]) / len(xyz[:, 2])

            msg = objectxyz()

            msg.x = x
            msg.y = y
            msg.z = z
            msg.Class = graph_text
            #msg.Class = "aaa"

            print msg

            msg_len.objects.append(msg)

            ax.scatter(x, y , z, 'o', s=600 , c=tuple(col), linewidths="3")
            ax.text(x, y, z, graph_text, color='black')

    while not rospy.is_shutdown():
        pub.publish(msg_len)

    print(msg_len)

        #xyz = X_train[class_member_mask & core_samples_mask]
        #ax.scatter(xyz[:, 0], xyz[:, 1] , xyz[:, 2], 'o', s=600 , c=tuple(col), linewidths="3")
        #xyz = X_train[class_member_mask & ~core_samples_mask]
        #ax.scatter(xyz[:, 0], xyz[:, 1] , xyz[:, 2], '*', s=100, c=tuple(col), linewidths="1")

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()

if __name__ == '__main__':
    adder()
    rospy.spin()
