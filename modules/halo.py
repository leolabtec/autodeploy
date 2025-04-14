import os
import subprocess
from rich import print
from rich.prompt import Prompt
import socket

def is_domain_resolved(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def create_halo_site():
    print("[bold green][INFO] 开始部署 Halo 博客...[/bold green]")

    domain = Prompt.ask("请输入要部署的域名（如 blog.example.com）").strip().lower()

    if not is_domain_resolved(domain):
        print(f"[red]❌ 域名 {domain} 无法解析，请先配置正确的解析记录。部署已中止。[/red]")
        return

    base_dir = f"/home/dockerdata/docker_web/{domain.replace('.', '_')}"
    os.makedirs(base_dir, exist_ok=True)

    # 写入 docker-compose.yml
    with open(os.path.join(base_dir, "docker-compose.yml"), "w") as f:
        f.write(f"""version: '3'

services:
  halo:
    image: halohub/halo:2.15
    restart: always
    ports:
      - "127.0.0.1:31{domain[-2:]}:8090"
    volumes:
      - ./halo:/root/.halo2
    environment:
      - SPRING_R2DBC_URL=r2dbc:h2:file:///root/.halo2/db/halo
""")

    print("[cyan]🚀 正在启动 Halo 服务容器...[/cyan]")
    subprocess.run(["docker-compose", "up", "-d"], cwd=base_dir)

    # 添加反代
    from core import caddy
    caddy.add_proxy(domain, f"127.0.0.1:31{domain[-2:]}")

    print(f"[green]✅ Halo 博客已部署：https://{domain}[/green]")
    print("[blue]首次打开需初始化账号[/blue]")
