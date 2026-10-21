#!/bin/bash
DISPLAY_NUM=":97"

pkill -f "squashfs-root/usr/bin/QGroundControl" 2>/dev/null
pkill -f "x11vnc -display $DISPLAY_NUM" 2>/dev/null
sleep 3
pkill -9 -f "squashfs-root/usr/bin/QGroundControl" 2>/dev/null
pkill -f "Xvfb $DISPLAY_NUM" 2>/dev/null
sleep 1
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 "$HOME/lab7/run/qgc.pid"
exit 0
