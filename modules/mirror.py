# modules/mirror.py

import json
import os
from pathlib import Path
from rich import print
from rich.prompt import Confirm
from core import utils

DOCKER_CONFIG = Path.home() / ".docker/config.json"
PIP_CONFIG_DIR = Path.home() / ".pip"
PIP_CONFIG_FILE = PIP_CONFIG_DIR / "pip.conf"

ALIYUN_DOCKER_MIRROR = "https://registry.cn-hangzhou.aliyuncs.com"
TSINGHUA_PYPI = "https://pypi.tuna.tsinghua.edu.cn/simple"

def enable_mirrors():
    # Docker 镜像源
    DOCKER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    docker_cfg = {"registry-mirrors": [ALIYUN_DOCKER_MIRROR]}
    DOCKER_CONFIG.write_text(json.dumps(docker_cfg, indent=2))
    utils.log_success(f"✅ 已启用 Docker 国内镜像源（阿里云）")

    # pip 镜像源
    PIP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    pip_cfg = f"""[global]
index-url = {TSINGHUA_PYPI}
"""
    PIP_CONFIG_FILE.write_text(pip_cfg)
    utils.log_success(f"✅ 已启用 pip 国内镜像源（清华大学）")

    print("[green]🇨🇳 国内镜像源设置完成！[/green]")

def reset_mirrors():
    confirm = Confirm.ask("是否确认还原为官方源？")
    if not confirm:
        print("已取消操作。")
        return

    # 移除 docker 镜像配置
    if DOCKER_CONFIG.exists():
        DOCKER_CONFIG.unlink()
        utils.log_info("Docker 镜像源配置已还原。")

    # 移除 pip 配置
    if PIP_CONFIG_FILE.exists():
        PIP_CONFIG_FILE.unlink()
        utils.log_info("pip 镜像源配置已还原。")

    print("[green]🔁 官方源已恢复。[/green]")
