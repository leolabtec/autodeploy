#!/bin/bash

set -e

REPO_RAW="https://raw.githubusercontent.com/leolabtec/autodeploy/main"
INSTALL_DIR="/opt/autodeploy"

# ========== 0. 检查依赖项 ==========
check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo "[-] 缺少必要依赖：$1，请先安装后再运行本脚本。"
    exit 1
  fi
}

echo "[+] 正在检查并准备系统关键依赖..."
check_dep python3
check_dep pip
check_dep docker
check_dep crontab

# ========== 1. 初始化目录结构 ==========
echo "[+] 创建主目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ========== 2. 安装依赖 ==========
echo "[+] 安装 requirements.txt..."
curl -sS "$REPO_RAW/requirements.txt" -o requirements.txt
pip install --upgrade pip --break-system-packages >/dev/null
pip install -r requirements.txt >/dev/null

# ========== 3. 拉取主程序与模块 ==========
echo "[+] 拉取主程序 main.py..."
curl -sS "$REPO_RAW/main.py" -o main.py

mkdir -p core modules

echo "[+] 拉取核心模块 core/..."
for file in utils.py docker_ops.py caddy.py monitor.py; do
  curl -sS "$REPO_RAW/core/$file" -o "core/$file"
done

echo "[+] 拉取功能模块 modules/..."
for file in wordpress.py halo.py delete.py backup.py restore.py uninstall.py shortcut.py mirror.py; do
  curl -sS "$REPO_RAW/modules/$file" -o "modules/$file"
done

# ========== 4. 启动或重启 Caddy 容器 ==========
echo "[+] 启动 Caddy 容器..."
mkdir -p /home/dockerdata/docker_caddy

# 写入默认 Caddyfile（若不存在）
CADDYFILE="/home/dockerdata/docker_caddy/Caddyfile"
if [ ! -f "$CADDYFILE" ]; then
  echo "[+] 准备默认 Caddyfile..."
  cat <<EOF > "$CADDYFILE"
# AutoDeploy 默认反代配置（占位）
EOF
fi

docker rm -f caddy 2>/dev/null || true

docker run -d \
  --name caddy \
  --restart=unless-stopped \
  --network host \
  -v /home/dockerdata/docker_caddy/Caddyfile:/etc/caddy/Caddyfile \
  -v /home/dockerdata/docker_caddy:/data \
  -v /home/dockerdata/docker_caddy:/config \
  caddy:2.7.6

echo "[✓] Caddy 已启动 (host 模式监听 80/443)"

# ========== 5. 添加定时巡检任务 ==========
echo "[+] 设置 Caddy 巡检任务..."
CRON_JOB="*/5 * * * * python3 $INSTALL_DIR/core/monitor.py >> /var/log/autodeploy_monitor.log 2>&1"
if crontab -l 2>/dev/null | grep -F "$CRON_JOB" > /dev/null; then
  echo "[i] 巡检任务已存在"
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "[✓] 已添加 crontab 巡检任务"
fi

# ========== 6. 自动执行 main.py 启动主菜单 ==========
echo "[✓] 环境部署完成，正在启动 AutoDeploy 主菜单..."
sleep 1

# 自动运行 main.py（无需虚拟环境）
python3 /opt/autodeploy/main.py
