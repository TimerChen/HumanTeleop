

## CAN 激活

```shell
bash ./scripts/piper_utils/find_all_can_port.sh

# 可以单个激活
bash can_activate.sh can0 1000000

# 改名
bash can_activate.sh can_piper 1000000 "3-1.4:1.0"

# 修改代码后直接运行
bash ./scripts/piper_utils/can_multi_activate.sh
```

## start
```shell

bash ./scripts/lauch_feetch_leader.sh 127.0.0.1 8080 8081 /dev/ttyACM0 /dev/ttyACM1

bash ./scripts/lauch_piper_feetech_follower.sh 8080 8081 can0 can1

```