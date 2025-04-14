import typer
from rich import print
from rich.panel import Panel
from core import utils
from modules import wordpress, halo, backup, delete, restore, uninstall, shortcut
import traceback

# 创建Typer应用实例
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

        try:
            choice = typer.prompt("请输入编号", default="0")
            # 如果输入的不是0-7之间的数字，提示重新输入
            while choice not in ["0", "1", "2", "3", "4", "5", "6", "7"]:
                print("[red]无效输入，请输入有效选项！[/red]")
                choice = typer.prompt("请输入编号", default="0")
        except (EOFError, KeyboardInterrupt) as e:
            print(f"\n[red]⚠️ 输入中断，返回主菜单。错误详情：{str(e)}[/red]")
            continue  # 如果发生异常，继续等待用户输入
        except Exception as e:
            print(f"\n[red]发生错误：{str(e)}。错误详情：{traceback.format_exc()}[/red]")
            continue

        try:
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
                    if sub_choice == "1":
                        shortcut.set_shortcut()
                except (EOFError, KeyboardInterrupt) as e:
                    print(f"\n[red]输入中断，返回主菜单。错误详情：{str(e)}[/red]")
                    continue  # 返回主菜单
            elif choice == "0":
                print("👋 再见！")
                raise typer.Exit()  # 正常退出
        except Exception as e:
            print(f"\n[red]执行过程中发生错误：{str(e)}。错误详情：{traceback.format_exc()}[/red]")

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        print(f"\n[red]程序启动失败，错误详情：{str(e)}。错误堆栈：{traceback.format_exc()}[/red]")  # 捕获主程序异常
