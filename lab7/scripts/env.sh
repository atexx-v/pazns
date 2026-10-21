#!/bin/bash

unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH \
      GZ_SIM_RESOURCE_PATH GZ_SIM_SYSTEM_PLUGIN_PATH SDF_PATH
source /opt/ros/humble/setup.bash
export GZ_VERSION=harmonic
source "$HOME/ros2_ws/install/setup.bash"
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$HOME/ros2_ws/install/ardupilot_gazebo/share"
export PATH="$PATH:$HOME/.local/bin"

export LAB7_DIR="$HOME/lab7"
export LAB7_RUN="$LAB7_DIR/run"
export LAB7_LOG="$LAB7_DIR/logs"
export LAB7_QGC="$LAB7_DIR/qgc"
export LAB7_DATA="$LAB7_DIR/logs/qgc_data"
mkdir -p "$LAB7_RUN" "$LAB7_LOG" "$LAB7_DATA"

export LAB7_DISPLAY=":97"
export LAB7_VNC_PORT=5901

source "$LAB7_DIR/variant.env"
