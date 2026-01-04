SCRIPT_PATH=$(dirname "$(realpath "$0")")

bash ${SCRIPT_PATH}/../kill_windows.sh teleop

while true; do
    which python
    # try to start the teleop
    python ${SCRIPT_PATH}/reverse.py
done

