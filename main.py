import typer
from rich import print
from rich.panel import Panel
from core import utils
from modules import wordpress, halo, backup, delete, restore, uninstall, shortcut

app = typer.Typer()

def show_logo():
    logo = """[bold cyan]
██╗     ███████╗ ██████╗ ██╗      █████╗ ██████╗ 
██║     ██╔════╝██╔═══██╗██║     ██╔══██╗██╔══██╗
██║     █████╗  ██║   ██║██║     ███████║██████╔╝
██║     ██╔══╝  ██║   ██║██║     ██╔══██║██║     
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

    utils.log_info("如需更新项目，请重新运行 install.sh")

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

        # 捕获输入错误，避免未检测到输入时退出
        try:
            choice = typer.prompt("请输入编号", default="0")
            if not choice.strip():  # 输入为空时，重新提示
                raise ValueError("无效输入，请输入有效编号")
        except (EOFError, KeyboardInterrupt, ValueError) as e:
            print(f"\n[red]⚠️ 错误：{e}，已返回主菜单[/red]")
            continue

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
            print("\n[bold green]📦 配置系统：[/bold green]")
            print("1. 设置启动快捷键")
            print("0. 返回主菜单")
            try:
                sub_choice = typer.prompt("请输入编号", default="0")
            except (EOFError, KeyboardInterrupt):
                print("\n[red]⚠️ 未检测到输入，已返回主菜单[/red]")
                continue

            if sub_choice == "1":
                shortcut.set_shortcut()
        elif choice == "0":
            print("[✓] 退出 AutoDeploy...")
            break  # 用户选择退出时退出循环
        else:
            print("[red]无效的选择，请重新输入！[/red]")
