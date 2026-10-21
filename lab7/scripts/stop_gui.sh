#!/bin/bash
pkill -f "gz sim -v4 -g" 2>/dev/null
pkill -f "x11vnc -display :98" 2>/dev/null
sleep 2
pkill -9 -f "gz sim -v4 -g" 2>/dev/null
pkill -f "Xvfb :98" 2>/dev/null
sleep 1
rm -f /tmp/.X98-lock /tmp/.X11-unix/X98
exit 0
