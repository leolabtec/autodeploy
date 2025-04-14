# modules/delete.py

import shutil
from pathlib import Path
from rich import print
from rich.prompt import Prompt, Confirm
from core import utils, docker_ops, caddy

SITE_BASE = Path("/home/dockerdata/docker_web")
CADDYFILE = Path("/home/dockerdata/docker_caddy/Caddyfile")

def list_sites():
    if not SITE_BASE.exists():
        return []
    return [p.name for p in SITE_BASE.iterdir() if p.is_dir()]

def remove_caddy_block(domain: str):
    if not CADDYFILE.exists():
        utils.log_error("找不到 Caddyfile，无法修改反代配置。")
        return

    content = CADDYFILE.read_text()
    if domain not in content:
        utils.log_info("Caddyfile 中未找到该站点配置，跳过移除。")
        return

    # 简单正则匹配并移除完整配置块
    new_content = []
    inside_block = False
    for line in content.splitlines():
        if line.strip().startswith(domain):
            inside_block = True
            continue
        if inside_block and line.strip() == "}":
            inside_block = False
            continue
        if not inside_block:
            new_content.append(line)

    CADDYFILE.write_text("\n".join(new_content))
    utils.log_success(f"Caddyfile 中已移除 {domain} 配置。")
    caddy.reload_caddy()

def delete_site():
    sites = list_sites()
    if not sites:
        print("[yellow]当前没有可删除的站点。[/yellow]")
        return

    print("[bold cyan]📦 当前已部署站点：[/bold cyan]")
    for idx, name in enumerate(sites, 1):
        print(f"{idx}. {name}")

    choice = Prompt.ask("请输入要删除的编号（或 0 取消）", default="0")
    if choice == "0":
        print("已取消操作。")
        return

    try:
        site_idx = int(choice) - 1
        sitename = sites[site_idx]
    except:
        utils.log_error("输入无效。")
        return

    full_path = SITE_BASE / sitename
    domain = sitename.replace("_", ".").replace("halo.", "").replace("wordpress.", "")

    confirm = Confirm.ask(f"是否确认删除站点 {sitename}？（该目录将被永久删除）")
    if not confirm:
        print("已取消操作。")
        return

    # 停止并删除容器
    docker_ops.compose_down(full_path)

    # 删除目录
    shutil.rmtree(full_path, ignore_errors=True)
    utils.log_success(f"已删除站点目录：{full_path}")

    # 移除反代配置
    remove_caddy_block(domain)

    print(f"[green]✅ 站点 {domain} 删除完成！[/green]")
