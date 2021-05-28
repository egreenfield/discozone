#!/bin/bash
# godisco.sh

#exit 0

if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
        echo "[$(date)] : godisco.sh : ssh session, exiting"
        exit 0
# many other tests omitted
else
  case $(ps -o comm= -p $PPID) in
    sshd|*/sshd) echo "[$(date)] : godisco.sh : ssh session, exiting"; exit 0
  esac
fi


for pid in $(pidof -x godisco.sh); do
    if [ $pid != $$ ]; then
        echo "[$(date)] : abc.sh : GoDisco is already running with PID $pid"
        exit 0
    fi
done

/usr/bin/python3 device_app.py >> logs/commandLineOutput.txt 2>&1 &

