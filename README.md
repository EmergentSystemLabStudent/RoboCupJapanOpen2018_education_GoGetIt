# RoboCupJapanOpen2018_education_GoGetIt

### Overview

Go get it task for Ri-one&Duckers2018 in RoboCup Japan Open

Training Phaseにおいて，DoorOpenによって競技スタート後,ロボットはPerson Tracking（Follow me）を行い，オペレータの後をついて地図生成を行い、場所の名前情報を教示してもらう．また,ロボットは物体検出を行いながら検出した物体の三次元座標を保存する.ロボットは環境内で得たマルチモーダル情報を用い，石伏らの手法[1][2]に谷口らの手法[3]を組み合わせ，場所の名前情報・位置情報・画像情報を用いて場所のカテゴリゼーションを行う．石伏らの手法は画像情報と位置情報を用いて場所のカテゴリゼーションを行った手法であり，谷口らの手法は言語情報と位置情報から場所を表す名前と場所のカテゴリを同時に獲得する手法である．

Test Phaseでは，命令文から場所の名前情報を取り出し，その場所の名前が表す場所のカテゴリの尤度に基づいて場所のカテゴリを特定し，その場所のカテゴリが持つガウス分布に基づいて移動先を決定する．

### Description

darknet_ros,freenectパッケージを使用しています.

###### Start

1. `roslaunch edu_go_get_it edu_go_get_it.launch`

2. `roslaunch freenect_launch freenect.launch`

3. `roslaunch darknet_ros darknet_ros.launch`

4. `roslaunch kinect_yolo kinect_yolo.launch`

### Paper

1. 石伏智，谷口彰，萩原良信，高野敏明，谷口忠大「自己位置と高次特徴量を用いた教師なし場所領域学習」第30回人工知能学会全国大会(JSAI2016)，2016年5月，福岡，同上論文集，2I3-4.
2. Satoshi Ishibushi, Akira Taniguchi, Toshiaki Takano, Yoshinobu Hagiwara and Tadahiro Taniguchi: “Statistical Localization Exploiting Convolutional Neural Network for an Autonomous Vehicle”, 41st Annual Conference of the IEEE Industrial Electronics Society (IECON’15), Nov. 9-12, 2015 in Yokohama (Japan). The proceedings of IECON’15, pp. 1369-1375.
3. Akira Taniguchi, Tadahiro Taniguchi, and Tetsunari Inamura: “Spatial concept acquisition for a mobile robot that integrates self-localization and unsupervised word discovery from spoken sentences,” IEEE Transactions on Cognitive and Developmental Systems, vol. 8, no. 4, pp. 285–297, 2016.
