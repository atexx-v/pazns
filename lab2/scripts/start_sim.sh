#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

"$DIR/stop_sim.sh" quiet

cd "$LAB2_RUN"

setsid ros2 launch ardupilot_gz_bringup iris_maze.launch.py \
    rviz:=false use_gz_sim_gui:=false > "$LAB2_LOG/sim.log" 2>&1 < /dev/null &
echo $! > "$LAB2_RUN/sim.pid"
echo "Запущено, лог: $LAB2_LOG/sim.log. Очікування готовності..."

for i in $(seq 1 60); do
    if timeout 5 ros2 service call /ap/v1/prearm_check std_srvs/srv/Trigger 2>/dev/null | grep -q "success=True"; then
        echo "Готово: дрон готовий до arm (через $((i * 3)) с)."
        exit 0
    fi
    sleep 3
done

echo "ПОМИЛКА: система не стала готовою за 180 с, див. $LAB2_LOG/sim.log"
exit 1
