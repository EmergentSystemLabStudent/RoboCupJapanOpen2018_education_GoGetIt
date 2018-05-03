#include "cmath"
#include "ros/ros.h"
#include "std_msgs/Int8.h"
#include "sensor_msgs/Image.h"
#include "sensor_msgs/PointCloud2.h"
#include <pcl/io/pcd_io.h>
#include "pcl/point_types.h"
#include "pcl/point_cloud.h"
#include "pcl_conversions/pcl_conversions.h"
#include "pcl/ModelCoefficients.h"
#include "pcl/filters/project_inliers.h"
#include "pcl/filters/extract_indices.h"
#include <pcl/sample_consensus/model_types.h>
#include <pcl/sample_consensus/method_types.h>
#include "pcl/segmentation/sac_segmentation.h"
#include "geometry_msgs/Pose.h"
#include "geometry_msgs/PoseWithCovarianceStamped.h"
#include "kinect_yolo/objectxyz.h"
#include "kinect_yolo/BoundingBox.h"
#include "kinect_yolo/BoundingBoxes.h"
#include <nav_msgs/OccupancyGrid.h>
using namespace std;
using namespace std_msgs;
using namespace sensor_msgs;
using namespace kinect_yolo;
using namespace geometry_msgs;
int map_cnt=0;
int cnt_get=0;
int pc_x=0,pc_y=0;
BoundingBoxes bb_get;
Pose pose_get;
pcl::PointCloud<pcl::PointXYZ>::Ptr pc_get (new pcl::PointCloud<pcl::PointXYZ>);
void bb_callback(const BoundingBoxesConstPtr& bb_sub){
  bb_get=*bb_sub;
  return;
}
void pose_callback(const PoseWithCovarianceStamped pose_sub){
  pose_get=pose_sub.pose.pose;
  return;
}
void cnt_callback(const Int8ConstPtr& cnt_sub){
  cnt_get=cnt_sub->data;
  return;
}
void pc_callback(const PointCloud2 pc_sub){
  pc_x=pc_sub.width;
  pc_y=pc_sub.height;
  pcl::fromROSMsg(pc_sub,*pc_get);
  return;
}
int main(int argc, char **argv){
  int i,x,y,cnt=0;
  objectxyz obj_pub;
  Pose pose_prc[3];
  pcl::PointCloud<pcl::PointXYZ> pc_prc[3];
  ros::init(argc, argv,"kinect_yolo");
  ros::NodeHandle nh;
  ros::Subscriber bb_sub = nh.subscribe("/darknet_ros/bounding_boxes",1,bb_callback);
  ros::Subscriber pc_sub = nh.subscribe("/camera/depth/points",1,pc_callback);
  ros::Subscriber pose_sub = nh.subscribe("/amcl_pose",1,pose_callback);
  ros::Subscriber cnt_sub = nh.subscribe("/darknet_ros/count",1,cnt_callback);
  ros::Publisher xyz_pub = nh.advertise<objectxyz>("/kinect_yolo/xyz",1);
  while (ros::ok()){
    ros::spinOnce();
    if(cnt!=cnt_get){
      for(i=0;i<bb_get.bounding_boxes.size();i++){
        x=((bb_get.bounding_boxes[i].xmin+bb_get.bounding_boxes[i].xmax)/2.0)*1.1-24;//left blank 
        y=((bb_get.bounding_boxes[i].ymin+bb_get.bounding_boxes[i].ymax)/2.0)*1.1-22;//upper blank
        if(x<pc_x&&y<=pc_y&&pc_prc[0].points.size())
	  if(!isnan(pc_prc[0].points[x+pc_x*y].x)&&!isnan(pc_prc[0].points[x+pc_x*y].y)&&!isnan(pc_prc[0].points[x+pc_x*y].z)&&pc_prc[0].points[x+pc_x*y].z>2.5){
	  obj_pub.x=pose_prc[0].position.x;//right
	  obj_pub.y=pose_prc[0].position.y;//depth
	  obj_pub.x+=pc_prc[0].points[x+pc_x*y].x*2*pose_prc[0].orientation.w*pose_prc[0].orientation.z;
	  obj_pub.x+=pc_prc[0].points[x+pc_x*y].z*(pose_prc[0].orientation.w*pose_prc[0].orientation.w-pose_prc[0].orientation.z*pose_prc[0].orientation.z);
	  obj_pub.y+=pc_prc[0].points[x+pc_x*y].z*2*pose_prc[0].orientation.w*pose_prc[0].orientation.z;
	  obj_pub.y-=pc_prc[0].points[x+pc_x*y].x*(pose_prc[0].orientation.w*pose_prc[0].orientation.w-pose_prc[0].orientation.z*pose_prc[0].orientation.z);
	  obj_pub.z=-pc_prc[0].points[x+pc_x*y].y;//down
	  obj_pub.Class=bb_get.bounding_boxes[i].Class;
	  xyz_pub.publish(obj_pub);
	  }
      }
      pc_prc[0]=pc_prc[1];
      pc_prc[1]=pc_prc[2];
      pc_prc[2]=*pc_get;
      pose_prc[0]=pose_prc[1];
      pose_prc[1]=pose_prc[2];
      pose_prc[2]=pose_get;
      cnt=cnt_get;
    }
  }
  return 0;
}
