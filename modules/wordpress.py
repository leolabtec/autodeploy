import os
import subprocess
from rich import print
from rich.prompt import Prompt
import socket

def is_domain_resolved(domain):
    try:
        ip = socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def create_wordpress_site():
    print("[bold green][INFO] 开始部署 WordPress 站点...[/bold green]")

    domain = Prompt.ask("请输入要部署的域名（如 blog.example.com）").strip().lower()

    if not is_domain_resolved(domain):
        print(f"[red]❌ 域名 {domain} 无法解析，请先配置正确的解析记录。部署已中止。[/red]")
        return

    base_dir = f"/home/dockerdata/docker_web/{domain.replace('.', '_')}"
    os.makedirs(base_dir, exist_ok=True)

    # 写入 .env
    with open(os.path.join(base_dir, ".env"), "w") as f:
        f.write(f"""MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=wordpress
MYSQL_USER=wpuser
MYSQL_PASSWORD=wppass
WORDPRESS_DB_HOST=db
WORDPRESS_DB_USER=wpuser
WORDPRESS_DB_PASSWORD=wppass
WORDPRESS_DB_NAME=wordpress
""")

    # 写入 docker-compose.yml
    with open(os.path.join(base_dir, "docker-compose.yml"), "w") as f:
        f.write(f"""version: '3.1'

services:
  db:
    image: mariadb
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass

  wordpress:
    image: wordpress
    restart: always
    ports:
      - "127.0.0.1:30{domain[-2:]}:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
""")

    # 启动容器
    print("[cyan]🚀 正在启动 WordPress 服务容器...[/cyan]")
    subprocess.run(["docker-compose", "up", "-d"], cwd=base_dir)

    # 调用 Caddy 模块配置反代（假设已实现）
    from core import caddy
    caddy.add_proxy(domain, f"127.0.0.1:30{domain[-2:]}")

    print(f"[green]✅ WordPress 站点已部署： https://{domain}[/green]")
    print(f"[blue]默认数据库用户：wpuser / wppass[/blue]")
