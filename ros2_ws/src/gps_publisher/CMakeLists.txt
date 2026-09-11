cmake_minimum_required(VERSION 3.8)
project(gps_publisher)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(gps_publisher_node src/gps_publisher_node.cpp)
ament_target_dependencies(gps_publisher_node rclcpp sensor_msgs)
target_include_directories(gps_publisher_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

# install(TARGETS / launch / config) 留到 2.6。
ament_package()
