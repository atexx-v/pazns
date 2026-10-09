#!/bin/bash
# у довго відкритому терміналі лишаються шляхи інших просторів (~/ardu_ws, старий ardupilot_gazebo)
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH \
      GZ_SIM_RESOURCE_PATH GZ_SIM_SYSTEM_PLUGIN_PATH SDF_PATH
source /opt/ros/humble/setup.bash
export GZ_VERSION=harmonic
source "$HOME/ros2_ws/install/setup.bash"
# sdformat_urdf шукає package://ardupilot_gazebo/... у каталогах з SDF_PATH, тому потрібен батьківський каталог пакета
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$HOME/ros2_ws/install/ardupilot_gazebo/share"
# mavproxy.py встановлений через pip --user
export PATH="$PATH:$HOME/.local/bin"

export LAB2_DIR="$HOME/lab2"
export LAB2_RUN="$LAB2_DIR/run"
export LAB2_LOG="$LAB2_DIR/logs"
mkdir -p "$LAB2_RUN" "$LAB2_LOG"
