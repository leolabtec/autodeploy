# modules/halo.py

import random
import string
from pathlib import Path
from rich import print
from core import utils
from core import docker_ops
from core import caddy

BASE_DIR = "/home/dockerdata/docker_web"

def get_random_port(base=8090):
    port = random.randint(30000, 39999)
    if utils.is_port_in_use(port):
        return get_random_port(base)
    return port

def create_halo_site():
    utils.log_info("开始部署 Halo 博客...")

    domain = input("请输入要部署的域名（如 halo.example.com）: ").strip()
    sitename = "halo_" + domain.replace(".", "_")
    site_dir = Path(BASE_DIR) / sitename
    site_dir.mkdir(parents=True, exist_ok=True)

    halo_port = get_random_port()

    compose_content = f"""
version: '3'
services:
  halo:
    image: halohub/halo:2.11
    container_name: {sitename}
    restart: always
    ports:
      - "{halo_port}:8090"
    volumes:
      - ./data:/root/.halo2
"""
    (site_dir / "docker-compose.yml").write_text(compose_content)

    # 启动容器
    docker_ops.compose_up(site_dir)

    # 添加反代配置
    utils.log_info("配置 Caddy 反向代理...")
    caddy.add_proxy(domain=domain, port=halo_port)

    print(f"[green]🎉 Halo 博客已部署并配置 HTTPS！[/green]")
    print(f"🌐 访问地址：https://{domain}")
    print(f"📁 数据目录：{site_dir}/data")
