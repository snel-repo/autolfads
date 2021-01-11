#!/bin/bash

MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"  # absolutized and normalized

#echo "python "$MY_PATH"/client_test.py "$1""

tmux kill-session -t $1
tmux new-session -d -s $1 "python "$MY_PATH"/client_test.py "$1""
#tmux set -t $1 remain-on-exit on
#sleep 0.1
