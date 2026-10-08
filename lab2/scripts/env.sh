#!/bin/bash
source /opt/ros/humble/setup.bash
export GZ_VERSION=harmonic
# шляхи зі старого ardupilot_gazebo з ~/.bashrc конфліктують з моделями ros2_ws
unset GZ_SIM_RESOURCE_PATH GZ_SIM_SYSTEM_PLUGIN_PATH
source "$HOME/ros2_ws/install/setup.bash"
# mavproxy.py встановлений через pip --user
export PATH="$PATH:$HOME/.local/bin"

export LAB2_DIR="$HOME/lab2"
export LAB2_RUN="$LAB2_DIR/run"
export LAB2_LOG="$LAB2_DIR/logs"
mkdir -p "$LAB2_RUN" "$LAB2_LOG"
