cmake_minimum_required(VERSION 3.8)
project(group29_assignment_1_kalman)

# Default warnings
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(apriltag_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)


install(
  PROGRAMS
    src/april_tag_node.py
    src/navigation_node.py
    src/table_detector.py 
  DESTINATION lib/${PROJECT_NAME}
)


install(
  DIRECTORY
    launch
    cfg
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
