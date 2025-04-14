#!/bin/sh

set -e

INSTALL_DIR="/opt/autodeploy"
PYTHON_BIN="python3"
VENV_DIR="$INSTALL_DIR/.venv"

echo "[+] 创建项目目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 检查 Python 是否存在
if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "[*] 未检测到 Python3，尝试自动安装..."

    if [ -f /etc/alpine-release ]; then
        echo "[*] 检测到 Alpine 系统，使用 apk 安装 Python3..."
        apk update && apk add python3 py3-pip py3-virtualenv
    elif [ -f /etc/debian_version ]; then
        echo "[*] 检测到 Debian/Ubuntu 系统，使用 apt 安装 Python3..."
        apt update && apt install -y python3 python3-venv python3-pip
    else
        echo "[-] 当前系统未支持自动安装，请手动安装 Python3"
        exit 1
    fi
fi

echo "[+] 创建虚拟环境..."
$PYTHON_BIN -m venv .venv
source .venv/bin/activate

echo "[+] 安装依赖（requirements.txt）..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

echo "[+] 启动主程序 main.py..."
$VENV_DIR/bin/python main.py
