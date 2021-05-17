#!/bin/bash
# nodisco.sh

kill $(ps aux | grep '[p]ython3 app.py' | awk '{print $2}')

