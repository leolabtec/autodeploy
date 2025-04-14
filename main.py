# main.py

from core import utils
import typer
from rich import print
from rich.panel import Panel
from core import sync

app = typer.Typer()

def show_logo():
    logo = """[bold cyan]
██╗     ███████╗ ██████╗ ██╗      █████╗ ██████╗ 
██║     ██╔════╝██╔═══██╗██║     ██╔══██╗██╔══██╗
██║     █████╗  ██║   ██║██║     ███████║██████╔╝
██║     ██╔══╝  ██║   ██║██║     ██╔══██║██╔═══╝ 
███████╗███████╗╚██████╔╝███████╗██║  ██║██║     
╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     
[/bold cyan]"""

    author_info = "[green]🔧 作者：LEOLAB   📦 版本：v0.1.0[/green]"
    print(Panel.fit(f"{logo}\n{author_info}", title="AutoDeploy", subtitle="by LEOLAB", border_style="cyan"))

def startup_checks():
    show_logo()

    if utils.check_network():
        utils.log_success("网络连接正常")
    else:
        utils.log_error("⚠️ 网络连接异常，请检查是否可访问 github.com")

    try:
        if sync.check_update_available():
            print("[yellow]检测到有可用更新，可运行 `python core/sync.py` 更新脚本文件[/yellow]")
        else:
            utils.log_info("当前代码为最新版本")
    except Exception:
        utils.log_error("检查更新失败（可能网络不通）")

@app.command()
def start():
    startup_checks()

    print("\n[bold green]请选择操作：[/bold green]")
    print("1. 创建 WordPress 站点")
    print("2. 创建 Halo 博客")
    print("3. 查看备份")
    print("4. 卸载所有服务")
    print("0. 退出")

    choice = typer.prompt("输入选项编号", default="0")

    if choice == "1":
        print("👉 执行创建 WordPress（待接入）")
    elif choice == "2":
        print("👉 执行创建 Halo（待接入）")
    elif choice == "3":
        print("👉 显示备份信息（待接入）")
    elif choice == "4":
        print("🧨 正在卸载（待接入）")
    else:
        print("👋 再见！")

if __name__ == "__main__":
    app()
