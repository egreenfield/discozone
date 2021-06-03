#!/bin/bash
# nodisco.sh

kill $(ps aux | grep '[p]ython3 device_app.py' | awk '{print $2}')

