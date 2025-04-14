# core/docker_ops.py

import subprocess
import shutil
from pathlib import Path
from core import utils

def is_docker_installed() -> bool:
    return shutil.which("docker") is not None

def list_containers():
    if not is_docker_installed():
        utils.log_error("未安装 Docker，无法列出容器。")
        return
    subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}"])

def compose_up(path: Path):
    if shutil.which("docker-compose"):
        cmd = ["docker-compose", "up", "-d"]
    elif shutil.which("docker"):
        cmd = ["docker", "compose", "up", "-d"]
    else:
        utils.log_error("找不到 Docker Compose 命令")
        return
    subprocess.run(cmd, cwd=path)

def compose_down(path: Path):
    if shutil.which("docker-compose"):
        cmd = ["docker-compose", "down"]
    elif shutil.which("docker"):
        cmd = ["docker", "compose", "down"]
    else:
        utils.log_error("找不到 Docker Compose 命令")
        return
    subprocess.run(cmd, cwd=path)

def remove_volume_named(volume_name: str):
    subprocess.run(["docker", "volume", "rm", volume_name])

def remove_network_named(network_name: str):
    subprocess.run(["docker", "network", "rm", network_name])
