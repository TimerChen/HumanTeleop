SCRIPT_PATH=$(dirname "$(realpath "$0")")
while true; do
    which python
    # try to start the teleop
    python ${SCRIPT_PATH}/reverse.py
done

