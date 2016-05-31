#!/bin/bash

#startx &
PIDFILE=$HOME/tmp/screen/.screen.pid

pushd /home/pi/tmp/screen >> /dev/null 2>&1

START=0
if [ -e "$PIDFILE" ]; then
    PID="$(cat $PIDFILE)"
    if ! ps -p $PID > /dev/null ; then
        # last process is not around
        echo "Clean up from last process [$PID]"
        rm $PIDFILE
        START=1
    else
        echo -n '.'
    fi
else
    START=1
fi

if [ "$(pidof pyscreen)" ]; then
    START=0
fi



if [ $START -eq 1 ]; then
	sleep 10
#	sudo setsid sh -c 'DISPLAY=:0 python PiTFTWeather.py <> /dev/tty0 >&0 2>&1' &
	sudo setsid sh -c 'DISPLAY=:0 python weather2.py <> /dev/tty0 >&0 2>&1' &
	echo $! > $PIDFILE
	echo 'Running....'
fi
