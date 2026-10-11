#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

"$DIR/stop_gui.sh"

if [ "${1:-}" = rviz ]; then
    SCREEN=1920x900x24; CONFIG=full.config
else
    SCREEN=1280x720x24; CONFIG=live.config
fi

Xvfb :99 -screen 0 "$SCREEN" > "$LAB2_LOG/xvfb.log" 2>&1 &
sleep 2
export DISPLAY=:99

setsid gz sim -v4 -g --gui-config "$LAB2_DIR/gui/$CONFIG" > "$LAB2_LOG/gui.log" 2>&1 < /dev/null &

if [ "${1:-}" = rviz ]; then
    RVIZ_CFG="$(ros2 pkg prefix ardupilot_gz_bringup)/share/ardupilot_gz_bringup/rviz/iris_with_lidar.rviz"
    LIBGL_ALWAYS_SOFTWARE=1 setsid rviz2 -d "$RVIZ_CFG" > "$LAB2_LOG/rviz.log" 2>&1 < /dev/null &
    for i in $(seq 1 40); do
        WIN=$(xdotool search --onlyvisible --name "RViz" 2>/dev/null | head -1)
        [ -n "$WIN" ] && break
        sleep 1
    done
    [ -n "$WIN" ] && xdotool windowmove "$WIN" 960 0 windowsize "$WIN" 960 900
fi

x11vnc -display :99 -rfbauth "$HOME/.vnc/passwd" -allow 192.168.64.1 \
    -forever -shared -rfbport 5900 -quiet > "$LAB2_LOG/vnc.log" 2>&1 &
sleep 2

echo "Готово. На Mac: Finder -> Перехід -> Підключення до сервера -> vnc://$(hostname -I | awk '{print $1}'):5900"
