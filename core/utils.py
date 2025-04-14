# core/utils.py

import socket
import requests
from rich import print

def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_public_ip() -> str:
    """获取公网 IP"""
    try:
        res = requests.get("https://api.ipify.org", timeout=5)
        return res.text
    except Exception:
        return "无法获取"

def check_network(url="https://github.com") -> bool:
    """检测网络连通性"""
    try:
        res = requests.get(url, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

# 日志输出（带颜色）
def log_info(msg: str):
    print(f"[cyan][INFO][/cyan] {msg}")

def log_success(msg: str):
    print(f"[green][SUCCESS][/green] {msg}")

def log_error(msg: str):
    print(f"[red][ERROR][/red] {msg}")
