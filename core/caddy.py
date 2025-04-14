# core/caddy.py

import time
from pathlib import Path
from rich import print
import subprocess
from core import utils

CADDYFILE_PATH = Path("/home/dockerdata/docker_caddy/Caddyfile")
CADDY_CONTAINER_NAME = "caddy"
CERT_BASE_PATH = Path("/home/dockerdata/docker_caddy/cert")

def generate_proxy_block(domain: str, internal_port: int = 80) -> str:
    return f"""
{domain} {{
    reverse_proxy 127.0.0.1:{internal_port}
}}
"""

def add_proxy(domain: str, port: int):
    if not CADDYFILE_PATH.exists():
        utils.log_error("找不到 Caddyfile，请确保 Caddy 已正确安装并运行。")
        return

    caddyfile_content = CADDYFILE_PATH.read_text()
    if domain in caddyfile_content:
        utils.log_info(f"{domain} 已存在于 Caddyfile 中，跳过添加。")
    else:
        utils.log_info(f"正在添加反代配置至 Caddyfile...")
        block = generate_proxy_block(domain, port)
        with open(CADDYFILE_PATH, "a") as f:
            f.write("\n" + block + "\n")
        utils.log_success(f"{domain} 配置已写入。")

    reload_caddy()
    wait_for_cert(domain)

def reload_caddy():
    utils.log_info("尝试热更新 Caddy 配置...")
    result = subprocess.run(
        ["docker", "exec", CADDY_CONTAINER_NAME, "caddy", "reload"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        utils.log_success("Caddy 热更新成功 ✅")
    else:
        utils.log_error("Caddy 热更新失败 ❌")
        print(result.stderr)

def wait_for_cert(domain: str, timeout=30):
    cert_path = CERT_BASE_PATH / domain / "cert.pem"
    print(f"📡 正在等待 TLS 证书签发（{domain}）...")
    for i in range(timeout):
        if cert_path.exists():
            utils.log_success("证书已签发，HTTPS 生效！")
            return
        time.sleep(1)
    utils.log_error("证书未在预期时间内签发，可能是 DNS 未解析或限频。")
