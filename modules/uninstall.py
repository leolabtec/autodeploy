# modules/uninstall.py

import os
import shutil
from pathlib import Path
from rich import print
from rich.prompt import Confirm
from core import utils

def uninstall_all():
    confirm = Confirm.ask("[red bold]⚠️ 是否确认卸载所有服务并删除所有文件？此操作不可恢复！[/red bold]")
    if not confirm:
        print("已取消操作。")
        return

    # 1. 停止所有容器
    utils.log_info("停止所有 Docker 容器...")
    os.system("docker ps -a -q | xargs -r docker stop")
    os.system("docker ps -a -q | xargs -r docker rm")

    # 2. 删除 dockerdata 和 backup 目录
    for path in ["/home/dockerdata", "/home/backup"]:
        if Path(path).exists():
            utils.log_info(f"删除目录 {path} ...")
            shutil.rmtree(path, ignore_errors=True)

    # 3. 删除 /opt/autodeploy/ 下所有 .py 和 .sh 文件
    code_dir = Path("/opt/autodeploy")
    for file in code_dir.glob("**/*.py"):
        file.unlink()
    for file in code_dir.glob("*.sh"):
        file.unlink()

    print("[green bold]✅ 系统卸载完成，所有部署数据和脚本已删除。[/green bold]")
