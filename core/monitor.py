# core/monitor.py

import subprocess
from core import utils
import time

CADDY_NAME = "caddy"

def get_container_status(name):
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", name],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except:
        return None

def get_restart_count(name):
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.RestartCount}}", name],
            capture_output=True, text=True
        )
        return int(result.stdout.strip())
    except:
        return 0

def monitor_caddy():
    status = get_container_status(CADDY_NAME)

    if status is None or status == "":
        utils.log_error(f"⚠️ 未检测到 Caddy 容器，请检查是否已部署。")
        return

    if status == "exited":
        utils.log_error(f"❌ 检测到 Caddy 容器已退出，尝试自动重启...")
        subprocess.run(["docker", "start", CADDY_NAME])
        time.sleep(2)
        # 检查是否重启成功
        if get_container_status(CADDY_NAME) == "running":
            utils.log_success("✅ Caddy 容器已成功重启")
        else:
            utils.log_error("❌ 重启失败，请手动检查日志")
        return

    if status == "running":
        restarts = get_restart_count(CADDY_NAME)
        if restarts > 3:
            utils.log_error(f"⚠️ 检测到 Caddy 容器累计重启 {restarts} 次，请检查配置是否异常")
        else:
            utils.log_info("✅ Caddy 正常运行")

if __name__ == "__main__":
    monitor_caddy()
