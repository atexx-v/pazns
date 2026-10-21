#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

MODE="${1:-nocam}"

"$DIR/stop_sim.sh" quiet

SITL_DIR="$LAB7_RUN/sitl"
mkdir -p "$SITL_DIR"
cd "$SITL_DIR" || exit 1

GZ_SHARE="$HOME/ros2_ws/install/ardupilot_gazebo/share/ardupilot_gazebo"
SITL_PARMS="$HOME/ros2_ws/install/ardupilot_sitl/share/ardupilot_sitl/config/default_params"
WORLD="$GZ_SHARE/worlds/iris_runway.sdf"
DEFAULTS="$SITL_PARMS/copter.parm"

if [ "$MODE" = "nocam" ]; then
    mkdir -p "$LAB7_DIR/worlds"
    sed 's#model://iris_with_gimbal#model://iris_with_ardupilot#' "$WORLD" > "$LAB7_DIR/worlds/iris_runway_nocam.sdf"
    WORLD="$LAB7_DIR/worlds/iris_runway_nocam.sdf"
    DEFAULTS="$DEFAULTS,$SITL_PARMS/gazebo-iris.parm"
else
    DEFAULTS="$DEFAULTS,$GZ_SHARE/config/gazebo-iris-gimbal.parm"
fi
DEFAULTS="$DEFAULTS,$LAB7_DIR/config/sitl_lab7.parm"

setsid gz sim -v3 -s -r "$WORLD" > "$LAB7_LOG/gazebo.log" 2>&1 < /dev/null &
echo $! > "$LAB7_RUN/gz.pid"

setsid bash -c 'arducopter --model json --speedup 1 --slave 0 --sim-address=127.0.0.1 --instance 0 --sysid 1 \
    --defaults "$0"; echo "SITL завершився з кодом $?"' "$DEFAULTS" > "$LAB7_LOG/sitl.log" 2>&1 < /dev/null &
echo $! > "$LAB7_RUN/sitl.pid"

setsid mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 \
    --out 127.0.0.1:14550 --out 127.0.0.1:14551 --non-interactive \
    > "$LAB7_LOG/mavproxy.log" 2>&1 < /dev/null &
echo $! > "$LAB7_RUN/mavproxy.pid"
echo "Запущено (режим $MODE), журнали: $LAB7_LOG/{gazebo,sitl,mavproxy}.log. Очікування готовності..."

if python3 "$DIR/wait_ready.py" 180; then
    exit 0
fi
echo "ПОМИЛКА: система не стала готовою за 180 с, див. журнали в $LAB7_LOG"
exit 1
