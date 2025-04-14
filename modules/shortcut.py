import os
import re
from rich import print
from rich.prompt import Prompt

def is_valid_alias(name):
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name)

def set_shortcut():
    print("[bold green]🚀 设置快捷方式，快速启动 AutoDeploy[/bold green]\n")

    # 默认推荐 alias 名称
    default_alias = "g"
    alias_name = Prompt.ask("请输入你想使用的快捷键 alias 名称", default=default_alias).strip()

    if not is_valid_alias(alias_name):
        print("[red]❌ 非法 alias 名称，只允许使用字母、数字、下划线，且不能以数字开头[/red]")
        return

    # 判断 shell 类型
    shell = os.environ.get("SHELL", "/bin/bash")
    rc_file = os.path.expanduser("~/.zshrc" if "zsh" in shell else "~/.bashrc")

    target_cmd = "cd /opt/autodeploy && source .venv/bin/activate && python main.py"
    alias_cmd = f"alias {alias_name}='{target_cmd}'"

    # 清理旧的 AutoDeploy alias（以注释为标识）
    if os.path.exists(rc_file):
        with open(rc_file, "r") as f:
            lines = f.readlines()
        with open(rc_file, "w") as f:
            skip = False
            for line in lines:
                if line.strip() == "# AutoDeploy 快捷键":
                    skip = True
                    continue
                if skip and line.strip().startswith("alias "):
                    skip = False
                    continue
                f.write(line)

    # 添加新的 alias
    with open(rc_file, "a") as f:
        f.write(f"\n# AutoDeploy 快捷键\n{alias_cmd}\n")

    print(f"[green]✅ 快捷命令已设置：[/green] [bold cyan]{alias_name}[/bold cyan] → {target_cmd}")
    print(f"[blue]📄 写入文件：{rc_file}[/blue]")

    # 尝试使 alias 立即生效
    try:
        os.system(alias_cmd)
        print(f"[green]⚡ 当前终端已立即支持 alias：{alias_name}[/green]")
    except Exception:
        print(f"[yellow]⚠️ 当前 session 未生效，请手动运行： source {rc_file}[/yellow]")

    print(f"🔄 若仍未生效，请关闭重开终端，或运行： [bold blue]source {rc_file}[/bold blue]")
