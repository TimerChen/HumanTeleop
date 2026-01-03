# launch script for feetech servo
# bash lauch_feetch.sh [ip] [port0] [port1] [device0]  [device1]
if [ $# -ne 5 ]; then
    echo "Usage: $0 [ip] [port0] [port1] [device0] [device1]"
    echo "Example: $0 127.0.0.1 8080 8081 /dev/ttyACM0 /dev/ttyACM1"
    exit 1
fi

ip=${1:-127.0.0.1}
port0=${2:-8080}
port1=${3:-8081}
device0=${4:-/dev/ttyACM0}
device1=${5:-/dev/ttyACM1}

# check if device0 and device1 exist
if [ ! -c $device0 ]; then
    echo "Error: $device0 does not exist"
    exit 1
fi
if [ ! -c $device1 ]; then
    echo "Error: $device1 does not exist"
    exit 1
fi

# get path of this script
SCRIPT_PATH=$(dirname "$(realpath "$0")")
# get python script path: $P/../teleop/follower/
SCRIPT_PATH="$SCRIPT_PATH/../teleop/leader/"

# feetch servo launch script
# kill existing tmux session
tmux kill-session -t teleop
# create tmux session
tmux new-session -d -s teleop
# create a window for servo
tmux new-window -t teleop:1 -n 2nd

# launch send_feetech.py
tmux send-keys -t teleop:0 "conda activate of3sp" C-m
tmux send-keys -t teleop:0 "python3 ${SCRIPT_PATH}send_feetech.py --device $device0 --calib calib0.json --ip $ip --port $port0" C-m
# launch send_feetech.py
tmux send-keys -t teleop:1 "conda activate of3sp" C-m
tmux send-keys -t teleop:1 "python3 ${SCRIPT_PATH}send_feetech.py --device $device1 --calib calib1.json --ip $ip --port $port1" C-m
