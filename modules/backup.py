import os
import time
from pathlib import Path
from rich import print
from core import utils
import subprocess

DOCKERDATA = Path("/home/dockerdata")
BACKUP_DIR = Path("/home/backup")

def stop_all_containers():
    """停止所有容器并返回停止的容器ID列表"""
    utils.log_info("正在停止所有容器...")
    container_ids = subprocess.check_output("docker ps -a -q", shell=True).decode("utf-8").splitlines()
    if container_ids:
        subprocess.run(f"docker stop {' '.join(container_ids)}", shell=True)
        return container_ids
    else:
        utils.log_warning("没有运行中的容器。")
        return []

def restart_containers(container_ids):
    """重新启动停止的容器"""
    if container_ids:
        utils.log_info("正在重启所有容器...")
        subprocess.run(f"docker start {' '.join(container_ids)}", shell=True)
    else:
        utils.log_warning("没有容器需要重启。")

def create_backup():
    """创建全盘备份"""
    if not DOCKERDATA.exists():
        utils.log_error("数据目录 /home/dockerdata 不存在，无法备份。")
        return

    # 提示用户备份会影响站点
    print("[bold red]⚠️ 注意：备份过程中，所有容器将被停止，直到备份完成！[/bold red]")
    confirm = input("[bold green]是否继续？[y/n]：")
    if confirm.lower() != 'y':
        print("[bold yellow]备份操作已取消。[/bold yellow]")
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / f"backup_{timestamp}.tar.gz"

    # 停止所有容器
    stopped_containers = stop_all_containers()

    try:
        utils.log_info("开始打包备份...")
        os.system(f"tar -czf {backup_file} -C /home dockerdata")
        print(f"[green]✅ 备份完成：{backup_file}[/green]")
    except Exception as e:
        utils.log_error(f"备份失败: {str(e)}")
    finally:
        # 备份完成后，重新启动之前停止的容器
        restart_containers(stopped_containers)
