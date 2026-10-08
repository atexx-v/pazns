#!/bin/bash
QUIET="${1:-}"
RUN="$HOME/lab2/run"
log() { [ "$QUIET" = quiet ] || echo "$@"; }

NAMES="arducopter micro_ros_agent parameter_bridge gz ruby"

if [ -f "$RUN/sim.pid" ]; then
    log "SIGINT для ros2 launch (PID $(cat "$RUN/sim.pid"))"
    kill -INT "$(cat "$RUN/sim.pid")" 2>/dev/null
    rm -f "$RUN/sim.pid"
    sleep 4
fi

# після SIGINT launch лишає процеси, які тримають порти 5760 і 2019
for n in $NAMES; do pkill -x "$n" 2>/dev/null; done
pkill -f "mavproxy.py" 2>/dev/null
sleep 2

for n in $NAMES; do pkill -9 -x "$n" 2>/dev/null; done
pkill -9 -f "mavproxy.py" 2>/dev/null
rm -f "$RUN"/*.pid

log "Симуляцію зупинено."
exit 0
