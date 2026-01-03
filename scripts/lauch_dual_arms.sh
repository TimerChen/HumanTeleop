# if [ $# -lt 2 ]; then
#     echo "Usage: $0 [inverse_arm] [inverse_calib]"
#     echo "Example: $0 0 0"
#     exit 1
# fi

# ip=${1:-127.0.0.1}

# device0=${1:-/dev/ttyACM0}
# device1=${2:-/dev/ttyACM1}
# port0=${3:-8080}
# port1=${4:-8081}

inverse_arm=0
inverse_calib=0
# 是否反转操作臂 y/n
read -p "是否反转操作臂 (y/n): " inverse_arm_input
if [ "$inverse_arm_input" == "y" ]; then
    inverse_arm=1
fi

# 是否反转校准 y/n
read -p "是否反转校准 (y/n): " inverse_calib_input
if [ "$inverse_calib_input" == "y" ]; then
    inverse_calib=1
fi

# inverse_arm=${1:-0}
# inverse_calib=${2:-0}

device0='/dev/ttyACM0'
device1='/dev/ttyACM1'
port0='8080'
port1='8081'

tele_port0='8080'
tele_port1='8081'

ip="127.0.0.1"
device_piper0='can0'
device_piper1='can1'
msg_mode0='custom_so101'
msg_mode1='custom_so101'
calib0='calib0.json'
calib1='calib1.json'

if [ "$inverse_arm" -eq 1 ]; then
    echo "------反转操作臂"
    tele_port0='8081'
    tele_port1='8080'
fi

if [ "$inverse_calib" -eq 1 ]; then
    echo "------反转校准"
    calib0='calib1.json'
    calib1='calib0.json'
fi

left_gello=0

if [ "$left_gello" -eq 1 ]; then
    echo "left side use gello"
    msg_model0='gello'
else
    echo 123
fi

# check if device0 and device1 exist
if [ ! -c $device0 ]; then
    echo "Error: $device0 does not exist"
    exit 1
fi
if [ ! -c $device1 ]; then
    echo "Error: $device1 does not exist"
    exit 1
fi

SCRIPT_PATH=$(dirname "$(realpath "$0")")
# get python script path: $P/../teleop/follower/
SCRIPT_PATH_L="$SCRIPT_PATH/../teleop/leader/"
SCRIPT_PATH_F="$SCRIPT_PATH/../teleop/follower/"

# kill existing tmux session
# tmux kill-session -t teleop
bash ${SCRIPT_PATH}/kill_windows.sh teleop
# create tmux session
tmux new-session -d -s teleop

tmux source-file ~/.tmux.conf

tmux new-window -t teleop:1 -n 2nd \
    \; split-window -h \
    \; split-window -v -t 0 \
    \; split-window -v -t 1 \
    \; select-layout tiled

tmux send-keys -t teleop:1.0 "conda activate of3sp" C-m
tmux send-keys -t teleop:1.1 "conda activate of3sp" C-m
tmux send-keys -t teleop:1.2 "conda activate of3sp" C-m
tmux send-keys -t teleop:1.3 "conda activate of3sp" C-m

if [ "$left_gello" -eq 1 ]; then
    tmux send-keys -t teleop:1.0 "python3 ${SCRIPT_PATH_L}send.py --device $device0 --calib calib_cjx.json --ip $ip --port $port0" C-m
    tmux send-keys -t teleop:1.2 "python3 ${SCRIPT_PATH_F}receive_and_control.py --port $port0 --can $device_piper0 --msg-mode $msg_mode0 " C-m
else
    tmux send-keys -t teleop:1.0 "python3 ${SCRIPT_PATH_L}send_feetech.py --device $device0 --calib ${calib0} --ip $ip --port $port0" C-m
    tmux send-keys -t teleop:1.2 "python3 ${SCRIPT_PATH_F}receive_and_control.py --port $tele_port0 --can $device_piper0 --msg-mode $msg_mode0" C-m
fi


tmux send-keys -t teleop:1.1 "python3 ${SCRIPT_PATH_L}send_feetech.py --device $device1 --calib ${calib1} --ip $ip --port $port1" C-m
tmux send-keys -t teleop:1.3 "python3 ${SCRIPT_PATH_F}receive_and_control.py --port $tele_port1 --can $device_piper1 --msg-mode $msg_mode1" C-m

tmux at -t teleop:1