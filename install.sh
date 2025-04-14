#!/bin/bash

set -e

# 防止弹窗
export DEBIAN_FRONTEND=noninteractive

REPO_RAW="https://raw.githubusercontent.com/leolabtec/autodeploy/main"
INSTALL_DIR="/opt/autodeploy"
VENV_DIR="$INSTALL_DIR/.venv"

# ========== 0. 自动检查并安装依赖 ==========
check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo "[!] 未检测到 $1，正在自动安装..."
    case "$1" in
      python3) apt update && apt install -y python3 ;;
      pip) apt install -y python3-pip ;;
      docker) apt install -y docker.io ;;
      docker-compose) apt install -y docker-compose ;;
      crontab) apt install -y cron ;;
      *) echo "[-] 未知依赖：$1" && exit 1 ;;
    esac
    command -v "$1" &>/dev/null || { echo "[-] $1 安装失败"; exit 1; }
    echo "[✓] $1 安装成功"
  fi
}

echo "[+] 检查关键依赖..."
check_dep python3
check_dep pip
check_dep docker
check_dep docker-compose
check_dep crontab

# ========== 1. 处理 venv 模块 & fallback ==========
PYVER=$(python3 -V 2>&1 | cut -d " " -f2 | cut -d "." -f1,2)
if ! python3 -m venv --help &>/dev/null; then
  echo "[!] venv 不可用，安装 python${PYVER}-venv..."
  apt install -y "python${PYVER}-venv"
fi

if ! python3 -m venv --help &>/dev/null; then
  echo "[!] 修复 ensurepip..."
  apt install -y python3-ensurepip
  python3 -m ensurepip --upgrade
fi

# ========== 2. 初始化目录结构 ==========
echo "[+] 创建目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ========== 3. 创建虚拟环境（含 fallback）==========
echo "[+] 创建虚拟环境..."
if ! python3 -m venv .venv 2>/dev/null; then
  echo "[!] venv 创建失败，使用 virtualenv fallback..."
  python3 -m pip install --upgrade pip setuptools virtualenv
  virtualenv .venv
  if [ ! -f ".venv/bin/activate" ]; then
    echo "[-] fallback 虚拟环境创建失败，请检查 Python 配置"
    exit 1
  fi
fi
source .venv/bin/activate

# ========== 4. 安装 Python 依赖 ==========
echo "[+] 安装 requirements..."
curl -sS "$REPO_RAW/requirements.txt" -o requirements.txt
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# ========== 5. 拉取主程序与模块 ==========
echo "[+] 拉取主程序..."
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

# ========== 6. 启动 Caddy 容器 ==========
echo "[+] 启动 Caddy..."
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

# ========== 7. 设置定时巡检 ==========
echo "[+] 设置 Caddy 巡检任务..."
CRON_JOB="*/5 * * * * $VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py >> /var/log/autodeploy_monitor.log 2>&1"
if crontab -l 2>/dev/null | grep -F "$VENV_DIR/bin/python $INSTALL_DIR/core/monitor.py" > /dev/null; then
  echo "[i] 巡检任务已存在"
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "[✓] 已添加 crontab 巡检任务"
fi

# ========== 8. 启动主菜单 ==========
echo "[+] 启动 AutoDeploy 主菜单..."
$VENV_DIR/bin/python main.py
