# RoboCupJapanOpen2018_education_GoGetIt

### Overview  

Go get it task for Ri-one&Duckers2018 in RoboCup Japan Open 

Training Phaseにおいて，ロボットがオペレータをFollow meしながら地図生成を行い，物体を検出し物体の場所を記録する.その後場所の名前情報を教示してもらうことで，マルチモーダル情報から場所のカテゴリゼーションを行う． 

Test Phaseでは，命令文から場所の名前情報を取り出し，その場所の名前が表す場所のカテゴリの尤度に基づいて場所のカテゴリを特定し，その場所のカテゴリが持つガウス分布に基づいて移動先を決定する．

### Description

darknet_ros,freenectパッケージを使用しています.

###### Start

1. `roslaunch edu_go_get_it edu_go_get_it.launch` 

2. `roslaunch freenect_launch freenect.launch` 

2. `roslaunch darknet_ros darknet_ros.launch`

2. `roslaunch kinect_yolo kinect_yolo.launch` 
