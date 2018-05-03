cmake_minimum_required(VERSION 2.8.3)
project(kinect_yolo)

find_package(catkin REQUIRED COMPONENTS
  rospy
  roscpp
  sensor_msgs
  std_msgs
  message_generation
  pcl_ros
)

 add_message_files(
   FILES
   objectxyz.msg
   objects.msg
   BoundingBox.msg
   BoundingBoxes.msg
 )

 generate_messages(
   DEPENDENCIES
   sensor_msgs
   std_msgs
 )

catkin_package(
  #INCLUDE_DIRS include
  LIBRARIES kinect_yolo
  CATKIN_DEPENDS rospy roscpp sensor_msgs std_msgs
  DEPENDS system_lib
)

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)


add_executable(kinect_yolo src/kinect_yolo.cpp)
target_link_libraries(kinect_yolo ${catkin_LIBRARIES})
add_executable(pcl2img src/pcl2img.cpp)
target_link_libraries(pcl2img ${catkin_LIBRARIES})
