import os
from rich import print
from rich.prompt import Prompt

def set_shortcut():
    print("[bold green]🚀 设置快捷方式，快速启动 AutoDeploy[/bold green]\n")

    # 默认推荐 alias 名称
    default_alias = "g"
    alias_name = Prompt.ask(f"请输入你想使用的快捷键 alias 名称", default=default_alias)

    # 检测用户 shell 类型
    user_shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in user_shell:
        rc_file = os.path.expanduser("~/.zshrc")
    else:
        rc_file = os.path.expanduser("~/.bashrc")

    target_cmd = "cd /opt/autodeploy && source .venv/bin/activate && python main.py"
    alias_cmd = f"alias {alias_name}='{target_cmd}'"

    # 检查是否已存在相同 alias 设置
    if os.path.exists(rc_file):
        with open(rc_file, "r") as f:
            lines = f.read()
            if alias_name in lines and target_cmd in lines:
                print(f"[yellow]⚠️ alias {alias_name} 已存在于 {rc_file}，无需重复添加[/yellow]")
                return

    # 写入配置文件
    with open(rc_file, "a") as f:
        f.write(f"\n# AutoDeploy 快捷键\n{alias_cmd}\n")

    print(f"[green]✅ 快捷命令已添加到 {rc_file}：[/green] [bold cyan]{alias_name}[/bold cyan]")
    print("🔄 请执行以下命令或重新打开终端使其生效：")
    print(f"[blue]source {rc_file}[/blue]")
