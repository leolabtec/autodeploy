# modules/wordpress.py

import os
import random
import string
import shutil
import subprocess
from pathlib import Path
from core import utils
from rich import print

BASE_DIR = "/home/dockerdata/docker_web"

def generate_password(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_random_port(base=80):
    port = random.randint(30000, 39999)
    if utils.is_port_in_use(port):
        return get_random_port(base)
    return port

def run_compose_up(directory: Path):
    if shutil.which("docker-compose"):
        cmd = ["docker-compose", "up", "-d"]
    elif shutil.which("docker"):
        cmd = ["docker", "compose", "up", "-d"]
    else:
        utils.log_error("未检测到 docker compose 或 docker-compose 命令，请先安装 Docker Compose！")
        return
    utils.log_info("启动容器中...")
    subprocess.run(cmd, cwd=directory)

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
      - "{get_random_port()}:80"
    env_file:
      - .env
    volumes:
      - ./data/html:/var/www/html
"""
    (site_dir / "docker-compose.yml").write_text(compose_content)

    # 启动容器
    run_compose_up(site_dir)

    print(f"[green]🎉 WordPress 站点已部署！[/green]")
    print(f"🌐 访问地址：http://{domain} （如无反代，使用 IP+端口）")
    print(f"🔐 数据库用户：{db_user} 密码：{db_pass}")
    print(f"🔐 WordPress 后台：admin / {wp_pass}（首次安装时设置）")
