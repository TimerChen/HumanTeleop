在 Ubuntu（GNOME 桌面）里，**想“桌面双击 → 弹出 Terminal 跑 .sh”**，最稳的做法是：**用 `.desktop` 启动器** 去调用你的 `.sh`。直接把 `.sh` 放桌面双击有时会被“文件管理器行为设置/安全策略”影响（可能打开编辑器而不是执行）。([help.gnome.org][1])

下面给你两种方案（推荐用方案 B）。

---

## 方案 A：直接双击 `.sh`（不推荐但简单）

1. 让脚本可执行：

```bash
chmod +x /path/to/your_script.sh
```

2. 设置 Files(文件) 对可执行文本的行为：
   打开 **Files(文件管理器) → Preferences(首选项) → Behavior(行为) → Executable Text Files(可执行文本文件)**，把它改成 **“Ask each time(每次询问)”** 或 **“Run them(运行)”**。([help.gnome.org][1])

> 缺点：就算能执行，也**不一定自动弹出终端窗口**给你看输出。

---

## 方案 B（推荐）：做一个桌面图标 `.desktop`，双击弹出终端执行 `.sh`

### 1) 把脚本放到固定位置，并赋可执行权限

例如放到 `~/bin`：

```bash
mkdir -p ~/bin
mv /path/to/your_script.sh ~/bin/myjob.sh
chmod +x ~/bin/myjob.sh
```

### 2) 在桌面创建启动器 `MyJob.desktop`

桌面一般是 `~/Desktop`（中文系统可能显示为“桌面”，但路径通常仍是 `~/Desktop`）。

创建文件：

```bash
nano ~/Desktop/MyJob.desktop
```

#### 版本 1：执行完**自动关闭**终端

```ini
[Desktop Entry]
Type=Application
Name=Run MyJob (auto close)
Exec=gnome-terminal -- bash -lc "/home/$USER/bin/myjob.sh"
Terminal=false
```

#### 版本 2：执行完**保持终端不关**（方便看日志、继续敲命令）

```ini
[Desktop Entry]
Type=Application
Name=Run MyJob (keep open)
Exec=gnome-terminal -- bash -lc "/home/$USER/bin/myjob.sh; exec bash"
Terminal=false
```

#### 版本 3：执行完**询问你按回车再关闭**

```ini
[Desktop Entry]
Type=Application
Name=Run MyJob (press Enter to close)
Exec=gnome-terminal -- bash -lc "/home/$USER/bin/myjob.sh; echo; read -p 'Press Enter to close...'"
Terminal=false
```

`Terminal=true/false` 是桌面启动器标准字段之一；但这里我们已经显式用 `gnome-terminal` 打开终端，所以设 `Terminal=false` 更直观。([specifications.freedesktop.org][2])

> 注意：`.desktop` 里的路径**尽量写绝对路径**，不要用 `~`，兼容性更好。([Ask Ubuntu][3])

### 3) 让 `.desktop` 自己也可执行

```bash
chmod +x ~/Desktop/MyJob.desktop
```

### 4) 允许启动（关键一步）

在桌面上 **右键这个 `.desktop` → “Allow Launching(允许启动)”**，否则可能双击没反应或提示不安全。([Ask Ubuntu][3])

---

## 额外：用 GNOME Terminal 的全局设置控制“命令结束后是否保持打开”

如果你更喜欢**全局**控制（所有终端都这样）：
gnome-terminal → Preferences → 选 profile → “When command finishes” 选 “Keep terminal open”。([Ask Ubuntu][4])

---

如果你告诉我你是 Ubuntu 20.04 / 22.04 / 24.04 哪个版本、以及你用的是 GNOME 还是 KDE（Kubuntu），我也可以把 `.desktop` 里的 `Exec=` 写成更贴合你系统的默认终端（例如 `kgx`/`konsole`）版本。

[1]: https://help.gnome.org/gnome-help/nautilus-behavior.html?utm_source=chatgpt.com "File manager behavior preferences"
[2]: https://specifications.freedesktop.org/desktop-entry/latest/recognized-keys.html?utm_source=chatgpt.com "6 Recognized desktop entry keys"
[3]: https://askubuntu.com/questions/1237042/desktop-files-not-launching-from-desktop-in-ubuntu-20-04-lts?utm_source=chatgpt.com "desktop files not launching from desktop in Ubuntu 20.04 LTS"
[4]: https://askubuntu.com/questions/630698/how-can-i-keep-the-gnome-terminal-open-after-a-program-closes?utm_source=chatgpt.com "How can I keep the gnome-terminal open after a program ..."
