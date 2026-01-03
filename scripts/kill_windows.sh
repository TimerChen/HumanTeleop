#!/usr/bin/env bash

# 设定会话名（如果你只有一个会话可以省略）
SESSION=$1   # 替换成你的会话名，或者留空使用当前会话

# 获取所有窗口的编号列表
if [ -z "$SESSION" ]; then
    # 
    echo "Run: $0 <session name>"
    exit 0
    # windows=$(tmux list-windows -F '#{window_index}')
else
    windows=$(tmux list-windows -t "$SESSION" -F '#{window_index}')
fi

# 对每个窗口发送 Ctrl-C
for w in $windows; do
    if [ -z "$SESSION" ]; then
        tmux send-keys -t "$w" C-c
    else
        tmux send-keys -t "${SESSION}:$w" C-c
    fi
done

sleep 1

tmux kill-session -t $SESSION
