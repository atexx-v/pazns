#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

"$DIR/stop_sim.sh" quiet

setsid ros2 launch ardupilot_gz_bringup iris_maze.launch.py \
    rviz:=false use_gz_sim_gui:=false > "$LAB2_LOG/sim.log" 2>&1 < /dev/null &
echo $! > "$LAB2_RUN/sim.pid"
echo "Запущено, лог: $LAB2_LOG/sim.log. Очікування готовності..."

for i in $(seq 1 60); do
    if ros2 service list 2>/dev/null | grep -q "/arm_motors$"; then
        echo "Готово: сервіс arm_motors доступний (через $((i * 3)) с)."
        exit 0
    fi
    sleep 3
done

echo "ПОМИЛКА: система не стала готовою за 180 с, див. $LAB2_LOG/sim.log"
exit 1
