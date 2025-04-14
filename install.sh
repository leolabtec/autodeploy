#!/bin/bash

set -e

REPO_RAW="https://raw.githubusercontent.com/leolabtec/autodeploy/main"
INSTALL_DIR="/opt/autodeploy"
VENV_DIR="$INSTALL_DIR/.venv"

# ========== 0. 自动检查并静默安装依赖项 ==========
check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo "[!] 未检测到 $1，正在尝试自动安装..."

    case "$1" in
      python3) apt update && apt install -y python3 ;;
      pip) apt update && apt install -y python3-pip ;;
      docker) apt update && apt install -y docker.io ;;
      docker-compose) apt update && apt install -y docker-compose ;;
      crontab) apt update && apt install -y cron ;;
      *)
        echo "[-] 未知依赖：$1，无法自动安装"
        exit 1
        ;;
    esac

    if ! command -v "$1" &>/dev/null; then
      echo "[-] 安装 $1 失败，请手动安装后重试"
      exit 1
    fi

    echo "[✓] $1 安装成功"
  fi
}

echo "[+] 正在检查并准备系统关键依赖..."
check_dep python3
check_dep pip
check_dep docker
check_dep docker-compose
check_dep crontab

# 检查 venv 模块可用性
if ! python3 -m venv --help &>/dev/null; then
  echo "[!] 未检测到 venv 模块，正在安装 python3-venv..."
  apt update && apt install -y python3-venv
  if ! python3 -m venv --help &>/dev/null; then
    echo "[-] venv 模块安装失败，请手动安装 python3-venv 后重试"
    exit 1
  fi
  echo "[✓] venv 安装成功"
fi

# ========== 1. 初始化目录结构 ==========
echo "[+] 创建主目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ========== 2. 创建 Python 虚拟环境 ==========
echo "[+] 创建虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate

echo "[+] 拉取 requirements.txt 并安装依赖..."
curl -sS "$REPO_RAW/requirements.txt" -o requirements.txt
pip install --upgrade pip >/dev/null
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
echo "[+] 启动或重启 Caddy 容器..."

mkdir -p /home/dockerdata/docker_caddy

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

# ========== 5. 添加 Caddy 容器定时健康巡检任务 ==========
echo "[+] 设置 Caddy 容器健康巡检任务..."

CRON_JOB="*/5 * * * * $VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py >> /var/log/autodeploy_monitor.log 2>&1"

if crontab -l 2>/dev/null | grep -F "$VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py" > /dev/null; then
  echo "[i] 巡检任务已存在，跳过添加"
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "[✓] Cron 任务已添加：每 5 分钟巡检 Caddy"
fi

# ========== 6. 启动主菜单 ==========
echo "[+] 启动 AutoDeploy 主菜单..."
$VENV_DIR/bin/python main.py
