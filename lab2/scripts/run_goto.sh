#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/env.sh"
source "$HOME/fpv_labs/install/setup.bash"
source "$HOME/lab2/variant.env"

RUN="$LAB2_LOG/run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN"
echo "Варіант $VARIANT: delta_x=$DELTA_X delta_y=$DELTA_Y frame_sign=$FRAME_SIGN, результати в $RUN"

ros2 run fpv_lab2 goto_target --ros-args \
    -p delta_x:="$DELTA_X" -p delta_y:="$DELTA_Y" -p frame_sign:="$FRAME_SIGN" \
    -p trajectory_file:="$RUN/trajectory.csv" \
    -p result_file:="$RUN/result.json" 2>&1 | tee "$RUN/flight.log"
