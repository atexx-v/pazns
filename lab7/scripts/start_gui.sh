#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

"$DIR/stop_gui.sh"

Xvfb :98 -screen 0 1280x720x24 > "$LAB7_LOG/xvfb_gz.log" 2>&1 &
sleep 2
export DISPLAY=:98
setsid gz sim -v4 -g --gui-config "$LAB7_DIR/gui/live.config" > "$LAB7_LOG/gui.log" 2>&1 < /dev/null &

MODEL=""
for i in $(seq 1 60); do
    MODEL=$(gz model --list 2>/dev/null | grep -o "iris_with[A-Za-z_]*" | head -1)
    [ -n "$MODEL" ] && break
    sleep 2
done
if [ -n "$MODEL" ]; then
    sleep 5
    gz service -s /gui/move_to --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 5000 --req "data: \"$MODEL\"" > /dev/null
fi

x11vnc -display :98 -rfbauth "$HOME/.vnc/passwd" -allow 192.168.64.1 \
    -forever -shared -rfbport 5902 -quiet > "$LAB7_LOG/vnc_gz.log" 2>&1 &
sleep 1
echo "Gazebo GUI запущено (модель: ${MODEL:-не знайдено}). VNC: vnc://$(hostname -I | awk '{print $1}'):5902"
