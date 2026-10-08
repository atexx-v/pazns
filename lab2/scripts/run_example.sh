#!/bin/bash
source "$(dirname "$0")/env.sh"
source "$HOME/fpv_labs/install/setup.bash"
exec ros2 run fpv_lab2 flight_test
