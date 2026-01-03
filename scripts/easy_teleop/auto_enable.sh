SCRIPT_PATH=$(dirname "$(realpath "$0")")/../piper_utils/

# check if has two can port
CAN_INFOS=$(sudo bash ${SCRIPT_PATH}find_all_can_port.sh | grep Interface)
NUM_CAN=$(echo "${CAN_INFOS}" | wc -l)

# example:
# Interface can0 is connected to USB port 1-6:1.0
# Interface can1 is connected to USB port 1-8.1:1.0

# Extract: can0, 1-6:1.0
# first line 
CAN0=$(echo "${CAN_INFOS}" | head -n 1 | cut -d ' ' -f 2)
CAN1=$(echo "${CAN_INFOS}" | head -n 2 | tail -n 1 | cut -d ' ' -f 2)
CAN0_PORT=$(echo "${CAN_INFOS}" | head -n 1 | cut -d ' ' -f 8)
CAN1_PORT=$(echo "${CAN_INFOS}" | head -n 2 | tail -n 1 | cut -d ' ' -f 8)

if [ ${NUM_CAN} -ne 2 ]; then
    echo "❌错误: 只能连接到${NUM_CAN}个机械臂"
    exit 1
fi
echo "✅成功连接到${NUM_CAN}个机械臂"

echo "${SCRIPT_PATH}/can_activate.sh ${CAN0} 1000000 ${CAN0_PORT}"
bash ${SCRIPT_PATH}/can_activate.sh ${CAN0} 1000000 ${CAN0_PORT}


if [ $? -ne 0 ]; then
    echo "❌错误: 激活机械臂can0失败"
    exit 1
fi
echo "✅成功激活can0"
bash ${SCRIPT_PATH}/can_activate.sh ${CAN1} 1000000 ${CAN1_PORT}
if [ $? -ne 0 ]; then
    echo "❌错误: 激活机械臂can1失败"
    exit 1
fi
echo "✅成功激活can1"
