#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

SIZE="${1:-1600x900}"
"$DIR/stop_qgc.sh"

Xvfb "$LAB7_DISPLAY" -screen 0 "${SIZE}x24" > "$LAB7_LOG/xvfb.log" 2>&1 &
sleep 2
export DISPLAY="$LAB7_DISPLAY"
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QUICK_BACKEND=software

cd "$LAB7_QGC/squashfs-root" || exit 1
setsid ./AppRun_glibc239 > "$LAB7_LOG/qgc.log" 2>&1 < /dev/null &
echo $! > "$LAB7_RUN/qgc.pid"

for i in $(seq 1 90); do
    WIN=$(xdotool search --onlyvisible --class "QGroundControl" 2>/dev/null | head -1)
    [ -n "$WIN" ] && break
    sleep 2
done
if [ -z "$WIN" ]; then
    echo "ПОМИЛКА: вікно QGroundControl не з'явилося, див. $LAB7_LOG/qgc.log"
    exit 1
fi
xdotool windowmove "$WIN" 0 0 windowsize "$WIN" "${SIZE%x*}" "${SIZE#*x}"

x11vnc -display "$LAB7_DISPLAY" -rfbauth "$HOME/.vnc/passwd" -allow 192.168.64.1 \
    -forever -shared -rfbport "$LAB7_VNC_PORT" -quiet > "$LAB7_LOG/vnc.log" 2>&1 &
sleep 1
echo "QGroundControl запущено (вікно $WIN). VNC: vnc://$(hostname -I | awk '{print $1}'):$LAB7_VNC_PORT"
