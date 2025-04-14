# main.py

import typer
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from core import utils
from modules import wordpress, halo, backup, delete, restore, uninstall, shortcut

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
    print(Panel.fit(f"{logo}\n[green]🔧 作者：LEOLAB   📦 版本：v1.0.0[/green]", title="AutoDeploy", subtitle="Powered by Python", border_style="cyan"))

def startup_checks():
    show_logo()

    if utils.check_network():
        utils.log_success("网络连接正常")
    else:
        utils.log_error("⚠️ 网络连接异常，无法访问 github.com")

@app.command()
def start():
    while True:
        startup_checks()

        print("\n[bold green]📋 请选择操作：[/bold green]")
        print("1. 创建 WordPress 站点")
        print("2. 创建 Halo 博客")
        print("3. 备份所有站点数据")
        print("4. 删除已部署站点")
        print("5. 恢复备份环境")
        print("6. 卸载部署系统")
        print("7. 配置系统")
        print("0. 退出")

        choice = typer.prompt("请输入编号", default="0")

        if choice == "1":
            wordpress.create_wordpress_site()
        elif choice == "2":
            halo.create_halo_site()
        elif choice == "3":
            backup.create_backup()
        elif choice == "4":
            delete.delete_site()
        elif choice == "5":
            restore.restore_backup()
        elif choice == "6":
            uninstall.uninstall_all()
        elif choice == "7":
            while True:
                print("\n[bold cyan]🔧 配置系统菜单[/bold cyan]")
                print("1. 设置启动快捷键")
                print("2. 清除已有快捷键")
                print("0. 返回主菜单")
                sub_choice = Prompt.ask("请输入编号", default="0")

                if sub_choice == "1":
                    shortcut.set_alias()
                elif sub_choice == "2":
                    shortcut.remove_alias()
                elif sub_choice == "0":
                    break
                else:
                    print("[yellow]⚠️ 无效输入，请重新选择。[/yellow]")
        else:
            print("👋 再见！")
            raise typer.Exit()

if __name__ == "__main__":
    app()
