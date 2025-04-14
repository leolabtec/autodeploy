# modules/backup.py

import os
import time
from pathlib import Path
from rich import print
from core import utils

DOCKERDATA = Path("/home/dockerdata")
BACKUP_DIR = Path("/home/backup")

def create_backup():
    if not DOCKERDATA.exists():
        utils.log_error("数据目录 /home/dockerdata 不存在，无法备份。")
        return

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / f"backup_{timestamp}.tar.gz"

    utils.log_info("正在停止所有容器...")
    os.system("docker ps -a -q | xargs -r docker stop")

    utils.log_info("开始打包备份...")
    os.system(f"tar -czf {backup_file} -C /home dockerdata")

    print(f"[green]✅ 备份完成：{backup_file}[/green]")
