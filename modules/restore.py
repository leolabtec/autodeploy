# modules/restore.py

import os
import shutil
from pathlib import Path
from rich import print
from rich.prompt import Prompt, Confirm
from core import utils, docker_ops

BACKUP_DIR = Path("/home/backup")
TARGET_DIR = Path("/home/dockerdata")

def list_backups():
    return sorted(BACKUP_DIR.glob("backup_*.tar.gz"))

def restore_backup():
    backups = list_backups()
    if not backups:
        utils.log_error("未找到任何备份文件。")
        return

    print("[bold cyan]📦 可用备份列表：[/bold cyan]")
    for idx, file in enumerate(backups, 1):
        print(f"{idx}. {file.name}")

    choice = Prompt.ask("请输入要恢复的编号（或 0 取消）", default="0")
    if choice == "0":
        print("已取消操作。")
        return

    try:
        file = backups[int(choice) - 1]
    except:
        utils.log_error("输入无效编号。")
        return

    confirm = Confirm.ask(f"是否确认恢复备份：{file.name}？（将清空当前 dockerdata）")
    if not confirm:
        print("已取消操作。")
        return

    utils.log_info("停止所有容器...")
    os.system("docker ps -a -q | xargs -r docker stop")

    utils.log_info("清空原有 dockerdata...")
    shutil.rmtree(TARGET_DIR, ignore_errors=True)

    utils.log_info("开始解压恢复...")
    os.system(f"tar -xzf {file} -C /home")

    utils.log_info("启动所有服务...")
    for compose_file in TARGET_DIR.rglob("docker-compose.yml"):
        docker_ops.compose_up(compose_file.parent)

    print(f"[green]✅ 恢复完成：{file.name}[/green]")
    print(f"📁 恢复路径：{TARGET_DIR}")
