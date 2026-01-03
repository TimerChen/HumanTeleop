#!/usr/bin/env bash
set -euo pipefail

SESSION="${1:-}"

if [ -z "$SESSION" ]; then
  echo "Run: $0 <session name>"
  exit 0
fi

# 获取该 session 的所有 window index
windows=$(tmux list-windows -t "$SESSION" -F '#{window_index}')

# 对每个 window 的每个 pane 发送 Ctrl-C
for w in $windows; do
  panes=$(tmux list-panes -t "${SESSION}:${w}" -F '#{pane_id}')
  for p in $panes; do
    echo "Send Ctrl-C to pane $p (window ${SESSION}:$w)"
    tmux send-keys -t "$p" C-c
  done
done

sleep 1
tmux kill-session -t "$SESSION"
