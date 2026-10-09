#!/bin/bash
QUIET="${1:-}"
RUN="$HOME/lab2/run"
log() { [ "$QUIET" = quiet ] || echo "$@"; }

# comm обрізається до 15 символів, тому шукаємо за командним рядком
PATTERNS=("ardupilot_gz_bringup" "robot_state_publisher" "topic_tools/relay" \
          "ros_gz_bridge/parameter_bridge" "ros_gz_sim/create" "micro_ros_agent" \
          "arducopter --model" "mavproxy.py" "gz sim")

kill_all() {
    for p in "${PATTERNS[@]}"; do pkill "$1" -f -- "$p" 2>/dev/null; done
    pkill "$1" -x ruby 2>/dev/null
}

if [ -f "$RUN/sim.pid" ]; then
    log "SIGINT для ros2 launch (PID $(cat "$RUN/sim.pid"))"
    kill -INT "$(cat "$RUN/sim.pid")" 2>/dev/null
    rm -f "$RUN/sim.pid"
    sleep 4
fi

# після SIGINT launch лишає процеси, які тримають порти 5760 і 2019
kill_all -TERM
sleep 3
kill_all -KILL

# файли вбитих процесів Fast DDS і ROS 2 накопичуються й плутають наступні запуски
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* /tmp/launch_params_* "$RUN"/*.pid
( source /opt/ros/humble/setup.bash; ros2 daemon stop ) > /dev/null 2>&1

log "Симуляцію зупинено."
exit 0
