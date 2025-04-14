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
for file in utils.py docker_ops.py caddy.py sync.py; do
  curl -sS "$REPO_RAW/core/$file" -o "core/$file"
done

echo "[+] 拉取功能模块 modules/..."
for file in wordpress.py halo.py; do
  curl -sS "$REPO_RAW/modules/$file" -o "modules/$file"
done

# ========== 3. 启动或重启 Caddy ==========
echo "[+] 拉取并启动 Caddy 容器..."
curl -sS "$REPO_RAW/start_caddy.sh" -o start_caddy.sh
chmod +x start_caddy.sh
./start_caddy.sh

# ========== 4. 启动主程序 ==========
echo "[+] 启动 AutoDeploy 主菜单..."
$VENV_DIR/bin/python main.py
