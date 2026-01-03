SCRIPT_PATH=$(dirname "$(realpath "$0")")

rm ${SCRIPT_PATH}/../../calib0.json
rm ${SCRIPT_PATH}/../../calib1.json

# try to start the teleop
bash ${SCRIPT_PATH}/../lauch_dual_arms.sh

