#!/bin/bash

set -e

REPO_RAW="https://raw.githubusercontent.com/leolabtec/autodeploy/main"
INSTALL_DIR="/opt/autodeploy"
VENV_DIR="$INSTALL_DIR/.venv"

# ========== 0. 检查依赖项 ==========
check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo "[-] 缺少必要依赖：$1，请先安装后再运行本脚本。"
    exit 1
  fi
}

echo "[+] 正在检查系统关键依赖..."
check_dep python3
check_dep pip
check_dep docker
check_dep crontab

# 检查 venv 模块可用性
if ! python3 -m venv --help &>/dev/null; then
  echo "[-] 当前 python3 缺少 venv 模块，请运行：sudo apt install python3-venv"
  exit 1
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

# ========== 4. 拉取 start.py 和 exit.py 启动脚本 ==========
echo "[+] 拉取 start.py 和 exit.py 启动脚本..."
for file in start.py exit.py; do
  curl -sS "$REPO_RAW/$file" -o "$INSTALL_DIR/$file"
done

# 不需要赋予执行权限，Python 脚本不需要赋权
echo "[✓] start.py 和 exit.py 拉取成功"

# ========== 5. 启动 AutoDeploy 主菜单 ==========
echo "[✓] 环境部署完成，正在启动 AutoDeploy 主菜单..."
sleep 1

# 自动运行 start.py 脚本，进入虚拟环境并启动 main.py
python3 /opt/autodeploy/start.py
