# launch script for feetech servo
# bash lauch_feetch.sh [ip] [port0] [port1] [device0]  [device1]
if [ $# -ne 4 ]; then
    echo "Usage: $0 [port0] [port1] [device0] [device1]"
    echo "Example: $0 8080 8081 can0 can1"
    exit 1
fi

port0=${1:-8080}
port1=${2:-8081}
device0=${3:-can0}
device1=${4:-can1}


# get path of this script
SCRIPT_PATH=$(dirname "$(realpath "$0")")
# get python script path: $P/../teleop/follower/
SCRIPT_PATH="$SCRIPT_PATH/../teleop/follower/"


# feetch servo launch script
# kill existing tmux session
tmux kill-session -t piper
# create tmux session
tmux new-session -d -s piper
# create a window for servo
tmux new-window -t piper:1 -n 2nd

# launch receive_and_control.py
tmux send-keys -t piper:0 "conda activate of3sp" C-m
tmux send-keys -t piper:0 "python3 ${SCRIPT_PATH}receive_and_control.py --port $port0 --can $device0 " C-m
# launch send_feetech.py
tmux send-keys -t piper:1 "conda activate of3sp" C-m
tmux send-keys -t piper:1 "python3 ${SCRIPT_PATH}receive_and_control.py --port $port1 --can $device1 " C-m
