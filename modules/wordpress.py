# modules/wordpress.py

import os
import random
import string
import shutil
import subprocess
from pathlib import Path
from rich import print
from core import utils
from core import docker_ops
from core import caddy

BASE_DIR = "/home/dockerdata/docker_web"

def generate_password(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_random_port(base=80):
    port = random.randint(30000, 39999)
    if utils.is_port_in_use(port):
        return get_random_port(base)
    return port

def create_wordpress_site():
    utils.log_info("开始部署 WordPress 站点...")

    domain = input("请输入要部署的域名（如 blog.example.com）: ").strip()
    sitename = domain.replace(".", "_")
    site_dir = Path(BASE_DIR) / sitename
    site_dir.mkdir(parents=True, exist_ok=True)

    db_name = f"db_{sitename}"
    db_user = f"user_{sitename}"
    db_pass = generate_password()
    wp_pass = generate_password()
    random_port = get_random_port()

    # 写入 .env
    env_content = f"""MYSQL_DATABASE={db_name}
MYSQL_USER={db_user}
MYSQL_PASSWORD={db_pass}
MYSQL_ROOT_PASSWORD={db_pass}
WORDPRESS_DB_HOST=db
WORDPRESS_DB_USER={db_user}
WORDPRESS_DB_PASSWORD={db_pass}
WORDPRESS_DB_NAME={db_name}
"""
    (site_dir / ".env").write_text(env_content)

    # 写入 docker-compose.yml
    compose_content = f"""
version: '3.7'
services:
  db:
    image: mariadb
    restart: always
    env_file:
      - .env
    volumes:
      - ./data/db:/var/lib/mysql

  wordpress:
    image: wordpress
    restart: always
    ports:
      - "127.0.0.1:{random_port}:80"
    env_file:
      - .env
    volumes:
      - ./data/html:/var/www/html
"""
    (site_dir / "docker-compose.yml").write_text(compose_content)

    # 启动容器
    docker_ops.compose_up(site_dir)

    # 添加 Caddy 反代配置
    utils.log_info("配置 Caddy 反向代理...")
    caddy.add_proxy(domain=domain, port=random_port)

    print(f"[green]🎉 WordPress 站点已部署并配置 HTTPS！[/green]")
    print(f"🌐 访问地址：https://{domain}")
    print(f"🔐 数据库用户：{db_user} 密码：{db_pass}")
    print(f"🔐 WordPress 后台：admin / {wp_pass}（首次安装时设置）")
