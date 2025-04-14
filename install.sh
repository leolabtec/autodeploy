#!/bin/bash

set -e
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

# ========== 1. 创建目录结构 ==========
echo "[+] 创建目录 $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ========== 2. 智能创建虚拟环境 ==========
echo "[+] 创建虚拟环境（首选 python3 -m venv）..."

if python3 -m venv "$VENV_DIR" 2>/dev/null; then
  echo "[✓] 成功创建虚拟环境（venv）"
else
  echo "[!] venv 创建失败，尝试 fallback 修复..."

  if grep -qi "alpine" /etc/os-release; then
    echo "[i] Alpine 系统，使用 apk 安装 py3-virtualenv"
    apk update
    apk add python3 py3-pip py3-virtualenv py3-setuptools
    python3 -m venv "$VENV_DIR"
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
      echo "[-] 修复失败，请手动检查 Alpine 环境"
      exit 1
    fi
  else
    echo "[i] 非 Alpine 系统，使用 virtualenv fallback 方式"
    apt update && apt install -y python3-pip python3-setuptools
    python3 -m pip install --upgrade pip setuptools virtualenv --break-system-packages
    python3 -m virtualenv "$VENV_DIR"
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
      echo "[-] virtualenv 创建失败，请检查 Python 安装状态"
      exit 1
    fi
  fi
fi

source "$VENV_DIR/bin/activate"

# ========== 3. 安装 Python requirements ==========
echo "[+] 安装 requirements.txt..."
curl -sS "$REPO_RAW/requirements.txt" -o requirements.txt
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# ========== 4. 拉取主程序与模块 ==========
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

# ========== 5. 准备默认 Caddyfile ==========
echo "[+] 准备默认 Caddyfile 配置..."
mkdir -p /home/dockerdata/docker_caddy

# 如果不是普通文件就删除（可能是目录、链接、挂载点等）
if [ ! -f /home/dockerdata/docker_caddy/Caddyfile ]; then
  echo "[!] 检测到 Caddyfile 非正常文件类型，强制重建..."
  rm -rf /home/dockerdata/docker_caddy/Caddyfile

  cat <<EOF > /home/dockerdata/docker_caddy/Caddyfile
:80 {
    respond "Caddy is running"
}
EOF
  echo "[✓] 已生成默认 Caddyfile"
fi

# ========== 6. 启动 Caddy ==========
echo "[+] 启动 Caddy 容器..."
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

# ========== 7. 添加定时巡检任务 ==========
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
