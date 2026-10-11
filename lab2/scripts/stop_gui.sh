#!/bin/bash
pkill -x rviz2 2>/dev/null
pkill -x x11vnc 2>/dev/null
pkill -x Xvfb 2>/dev/null
sleep 1
pkill -9 -x rviz2 2>/dev/null
pkill -9 -x x11vnc 2>/dev/null
pkill -9 -x Xvfb 2>/dev/null
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
exit 0
