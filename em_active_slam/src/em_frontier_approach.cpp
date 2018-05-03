#include <ros/ros.h>
#include <nav_msgs/OccupancyGrid.h>
#include <geometry_msgs/PoseStamped.h>
#include <actionlib_msgs/GoalStatusArray.h>
#include <std_msgs/Bool.h>

#include <iostream>
#include <vector>

using namespace std;

#define X_SIZE 1792 //X軸セル数
#define Y_SIZE 1184 //Y軸セル数

float robot_pose_x;
float robot_pose_y;
int status = 0;
bool goal_flag = true;
bool active_flag = false;

ros::Publisher goal_pub;
ros::Publisher finish_pub;

//マップのコールバック関数 フロンティアエッジの検出、その座標をpublish
void MapCallback(const nav_msgs::OccupancyGrid::ConstPtr& msg)
{
    cout << "map callback" <<endl;
    ros::spinOnce();
    //移動中以外にマップが更新された場合に処理を行う
    if(status!=1){
    //if(status!=1 && goal_flag==true && active_flag==true){
        goal_flag = false;
        vector< vector< vector<int> > > cell;
        vector< vector<int> > map_cell;
        vector<int> cell_x;
        vector<int> cell_y;

        map_cell = vector< vector<int> >(X_SIZE, vector<int>(Y_SIZE, 0));
        for(int y=0; y<Y_SIZE; y++){
            for(int x=0; x<X_SIZE; x++){
                map_cell[x][y] = int(msg->data[X_SIZE * y + x]);
            }
        }
        //各セルの情報を3次元配列に格納
        //1次元目:x軸、2次元目:y軸、3次元目:セルの情報
        //1段目 フロンティアエッジセル:100
        //2段目 フロンティア領域のグループ番号(1~n)
        //X_SIZE * Y_SIZE * 2 で領域確保、要素を0で初期化
        cell = vector< vector< vector<int> > >(X_SIZE, vector< vector<int> >(Y_SIZE, vector<int>(2, 0)));
        for(int y=1; y<Y_SIZE-1; y++){
            for(int x=1; x<X_SIZE-1; x++){
                if(map_cell[x][y]==0
                 && (map_cell[x][y-1]==-1
                 || map_cell[x-1][y]==-1
                 || map_cell[x+1][y]==-1
                 || map_cell[x][y+1]==-1))
                    cell[x][y][0] = 100;
                else if(map_cell[x][y]==0)
                    cell[x][y][0] = 0;
                else
                    cell[x][y][0] = -1;
            }
        }

        //隣接するエッジセルをフロンティア領域にグループ化,グループ番号を付ける
        int group = 0;
        for(int y=0; y<Y_SIZE; y++){
            for(int x=0; x<X_SIZE; x++){
                if(cell[x][y][0] == 100){
                    for(int i=y-1; i<=y+1; i++){
                        if(cell[x-1][i][0]==100 && cell[x-1][i][1]!=0){
                            cell[x][y][1] = cell[x-1][i][1];
                            break;
                        }
                        else if(cell[x][i][0]==100 && i!=y && cell[x][i][1]!=0){
                            cell[x][y][1] = cell[x][i][1];
                            break;
                        }
                        else if(cell[x+1][i][0]==100 && cell[x+1][i][1]!=0){
                            cell[x][y][1] = cell[x+1][i][1];
                            break;
                        }
                        //new group
                        if(i==y+1)
                            cell[x][y][1] = ++group;
                    }
                }
            }
        }

        //各グループのエッジセルの個数を格納
        int count[group];
        //初期化
        for(int i=0; i<group; i++)
            count[i] = 0;

        //各グループのエッジセルの個数をカウント
        for(int y=0; y<Y_SIZE; y++){
            for(int x=0; x<X_SIZE; x++){
                if(cell[x][y][1]!=0)
                    count[cell[x][y][1]-1]++;
            }
        }

        //n個以上のエッジセルが含まれるグループの個数をカウント
        int group_num = 0;
        int n = 20;
        int x_sum = 0;
        int y_sum = 0;
        int cell_count = 0;
        int x_mean = 0;
        int y_mean = 0;
        int distance_temp = 0;
        int distance = (X_SIZE * X_SIZE) + (Y_SIZE * Y_SIZE);
        int x_close = 0;
        int y_close = 0;
        for(int i=0; i<group; i++){
            if(count[i] >= n){
                group_num++;
                for(int y=0; y<Y_SIZE; y++){
                    for(int x=0; x<X_SIZE; x++){
                        if(cell[x][y][1]==i+1){
                            x_sum += x;
                            y_sum += y;
                            cell_count++;
                        }
                    }
                }
                x_mean = x_sum / cell_count;
                y_mean = y_sum / cell_count;
                for(int y=0; y<Y_SIZE; y++){
                    for(int x=0; x<X_SIZE; x++){
                        if(cell[x][y][1]==i+1){
                            distance_temp = (x_mean - x) * (x_mean - x) + (y_mean - y) * (y_mean - y);
                            if(distance_temp < distance){
                                distance = distance_temp;
                                x_close = x;
                                y_close = y;
                            }
                        }
                    }
                }
//                if(x_close < 1004 && x_close > 1044 && y_close < 1004 && y_close > 1044) {
                if(x_close > 1024) {
                    cell_x.push_back(x_close);
                    cell_y.push_back(y_close);
                }
                x_sum=0;
                y_sum=0;
                cell_count=0;
                distance = (X_SIZE * X_SIZE) + (Y_SIZE * Y_SIZE);
            }
        }
        cout << "\nthe number of frontier group " << cell_x.size() << "(" << group << ") n = " << n <<endl;

        if(cell_x.size() != 0){
            vector<double> frontier_pose_x;
            vector<double> frontier_pose_y;

            for(int i=0; i<cell_x.size(); i++){
                frontier_pose_x.push_back((cell_x[i] - 900) * 0.05);
                frontier_pose_y.push_back((cell_y[i] - 600) * 0.05);
                //cout << "( x , y ) = (" << cell_x[i] << "," << cell_y[i] << ")" <<endl;
                //cout << "( x , y ) = (" << frontier_pose_x[i] << "," << frontier_pose_y[i] << ")" <<endl;
            }

            //自己位置から一番近いエッジセルを求める
            //セル→地図座標に変換してpublish
            float frontier_temp = 0;
            float frontier;
            geometry_msgs::PoseStamped goal;
            for(int i=0; i<cell_x.size(); i++){
/*                frontier_temp = (robot_pose_x - frontier_pose_x[i]) * (robot_pose_x - frontier_pose_x[i])
                              + (robot_pose_y - frontier_pose_y[i]) * (robot_pose_y - frontier_pose_y[i]);*/
                frontier_temp = (0.0 - frontier_pose_x[i]) * (0.0 - frontier_pose_x[i])
                              + (0.0 - frontier_pose_y[i]) * (0.0 - frontier_pose_y[i]);

                if(i==0 || frontier_temp < frontier){
                    frontier = frontier_temp;
                    goal.pose.position.x = frontier_pose_x[i];
                    goal.pose.position.y = frontier_pose_y[i];
                }
            }
            goal_pub.publish(goal);
            cout << "Goal Publish\n" <<endl;

            cell_x.erase(cell_x.begin(), cell_x.end());
            cell_y.erase(cell_y.begin(), cell_y.end());
            frontier_pose_x.erase(frontier_pose_x.begin(), frontier_pose_x.end());
            frontier_pose_y.erase(frontier_pose_y.begin(), frontier_pose_y.end());
        }
        else if(cell_x.size() == 0) {
            cout << "Finish!!" <<endl;
            std_msgs::Bool finish;
            finish.data = true;
            finish_pub.publish(finish);
        }

    }
}

//ナビゲーション完了のflagを受け取る
void GoalFlagCallback(const std_msgs::Bool::ConstPtr& msg)
{
    cout<< "\t\tgoal_flag subcribe!!" <<endl;
    goal_flag = msg->data;
}

//ActiveSLAMスタートのflagを受け取る
void ActiveStartCallback(const std_msgs::Bool::ConstPtr& msg)
{
    cout<< "\t\tactive_flag subcribe!!" <<endl;
    active_flag = msg->data;
}

//自己位置を取得
/*void PoseCallback(const geometry_msgs::PoseStamped::ConstPtr& msg)
{
    //cout << "<<PoseCallback>>" <<endl;
    robot_pose_x = msg->pose.position.x;
    robot_pose_y = msg->pose.position.y;
}*/

//statusを取得 1:移動中 3:移動完了 4:移動失敗
void StatusCallback(const actionlib_msgs::GoalStatusArray::ConstPtr& msg)
{
    //cout<< "\t\tstatus subcribe!!" <<endl;
    if(msg->status_list.empty() == false){
        status = msg->status_list[0].status;
        //cout << "Status is " << status <<endl;
    }
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "em_frontier_approach");
    ros::NodeHandle nh;

    goal_pub = nh.advertise<geometry_msgs::PoseStamped>("/active/goal",1);
    finish_pub = nh.advertise<std_msgs::Bool>("/active/finish",1);

    ros::Subscriber map_sub = nh.subscribe<nav_msgs::OccupancyGrid>("/map", 1, MapCallback);
    ros::Subscriber goal_flag = nh.subscribe<std_msgs::Bool>("/goal/flag", 1, GoalFlagCallback);
    ros::Subscriber active_start = nh.subscribe<std_msgs::Bool>("/active/start", 1, ActiveStartCallback);
    //ros::Subscriber pose_sub = nh.subscribe<geometry_msgs::PoseStamped>("/global_pose", 1, PoseCallback);
    ros::Subscriber status_sub = nh.subscribe<actionlib_msgs::GoalStatusArray>("/move_base/status", 1, StatusCallback);

    ros::spin();
    return 0;
}
