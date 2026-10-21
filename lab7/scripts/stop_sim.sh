#!/bin/bash
QUIET="${1:-}"
RUN="$HOME/lab7/run"
log() { [ "$QUIET" = quiet ] || echo "$@"; }

PATTERNS=("ardupilot_gz_bringup" "robot_state_publisher" "topic_tools/relay" \
          "ros_gz_bridge/parameter_bridge" "ros_gz_sim/create" "micro_ros_agent" \
          "arducopter --model" "mavproxy.py" "gz sim")

kill_all() {
    for p in "${PATTERNS[@]}"; do pkill "$1" -f -- "$p" 2>/dev/null; done
    pkill "$1" -x ruby 2>/dev/null
}

kill_all -TERM
sleep 3
kill_all -KILL

rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* /tmp/launch_params_* "$RUN"/*.pid
( source /opt/ros/humble/setup.bash; ros2 daemon stop ) > /dev/null 2>&1

log "Симуляцію зупинено."
exit 0
