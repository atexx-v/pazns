#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"

case "$1" in
start)
    OUT="$2"; DISP="${3:-$LAB7_DISPLAY}"; mkdir -p "$OUT"
    (
        export DISPLAY="$DISP"
        while true; do
            import -window root "$OUT/$(date +%s%3N).png" 2>/dev/null
            sleep 2
        done
    ) > /dev/null 2>&1 &
    echo $! > "$LAB7_RUN/capture.pid"
    ;;
stop)
    [ -f "$LAB7_RUN/capture.pid" ] && kill "$(cat "$LAB7_RUN/capture.pid")" 2>/dev/null
    rm -f "$LAB7_RUN/capture.pid"
    ;;
*)
    echo "Використання: $0 start <каталог> [дисплей] | stop"; exit 1
    ;;
esac
