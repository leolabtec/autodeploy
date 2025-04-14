#!/bin/bash

set -e

REPO_RAW="https://raw.githubusercontent.com/leolabtec/autodeploy/main"
INSTALL_DIR="/opt/autodeploy"
VENV_DIR="$INSTALL_DIR/.venv"

echo "[+] 创建主目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ========== 1. 安装 Python 虚拟环境 ==========
echo "[+] 检查 Python 安装..."
if ! command -v python3 &>/dev/null; then
  echo "[-] 未检测到 python3，请先安装 Python 3"
  exit 1
fi

echo "[+] 创建虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate

echo "[+] 拉取 requirements.txt 并安装依赖..."
curl -sS "$REPO_RAW/requirements.txt" -o requirements.txt
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# ========== 2. 拉取主程序与模块 ==========
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

# ========== 3. 启动 Caddy 容器 ==========
echo "[+] 启动或重启 Caddy 容器..."

# 自动创建 Caddy 配置目录（如果不存在）
mkdir -p /home/dockerdata/docker_caddy

# 如已有同名容器则移除
docker rm -f caddy 2>/dev/null || true

# 启动 Caddy 容器（host 模式 + 自动加载配置）
docker run -d \
  --name caddy \
  --restart=unless-stopped \
  --network host \
  -v /home/dockerdata/docker_caddy/Caddyfile:/etc/caddy/Caddyfile \
  -v /home/dockerdata/docker_caddy:/data \
  -v /home/dockerdata/docker_caddy:/config \
  caddy:2.7.6

echo "[✓] Caddy 已启动 (host 模式监听 80/443)"

# ========== 4. 设置定时巡检任务 ==========
echo "[+] 设置 Caddy 容器健康巡检任务..."
CRON_JOB="*/5 * * * * $VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py >> /var/log/autodeploy_monitor.log 2>&1"

if crontab -l 2>/dev/null | grep -F "$VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py" > /dev/null; then
  echo "[i] 巡检任务已存在，跳过添加"
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "[✓] Cron 任务已添加：每 5 分钟巡检 Caddy"
fi

# ========== 5. 启动主程序 ==========
echo "[+] 启动 AutoDeploy 主菜单..."
$VENV_DIR/bin/python main.py
