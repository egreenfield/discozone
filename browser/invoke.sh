#!/bin/bash
# nodisco.sh

sam local invoke --env-vars config.json $1 | jsonpp | less
