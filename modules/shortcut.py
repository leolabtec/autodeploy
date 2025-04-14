import os
import re
from rich import print
from rich.prompt import Prompt, Confirm

def is_valid_alias(name):
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name)

def set_shortcut():
    print("[bold green]🚀 设置快捷方式，快速启动 AutoDeploy[/bold green]\n")

    default_alias = "g"
    alias_name = Prompt.ask("请输入你想使用的快捷键 alias 名称", default=default_alias).strip()

    if not is_valid_alias(alias_name):
        print("[red]❌ 非法 alias 名称，仅允许字母、数字、下划线，且不能以数字开头[/red]")
        return

    shell = os.environ.get("SHELL", "/bin/bash")
    rc_file = os.path.expanduser("~/.zshrc" if "zsh" in shell else "~/.bashrc")

    target_cmd = "cd /opt/autodeploy && source .venv/bin/activate && python main.py"
    alias_cmd = f"alias {alias_name}='{target_cmd}'"

    # 清除旧的 AutoDeploy alias 块
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

    # 写入新的 alias
    with open(rc_file, "a") as f:
        f.write(f"\n# AutoDeploy 快捷键\n{alias_cmd}\n")

    print(f"[green]✅ 快捷命令已设置：[/green] [bold cyan]{alias_name}[/bold cyan] → {target_cmd}")
    print(f"[blue]📄 写入文件：{rc_file}[/blue]")

    # 当前 session 尝试生效 alias
    os.system(alias_cmd)

    # 询问是否立即 source
    if Confirm.ask(f"是否立即执行 [bold]source {rc_file}[/bold] 让快捷键生效？"):
        os.system(f"source {rc_file}")  # 该行在 shell 中无效，仅提示好看
        print(f"[green]✅ 请手动执行：[bold]source {rc_file}[/bold]，或重启终端使用 alias[/green]")
    else:
        print(f"[yellow]⚠️ 你可以稍后执行：[bold]source {rc_file}[/bold] 使 alias 生效[/yellow]")

    print(f"[green]🎉 设置完成！下次可使用：[bold cyan]{alias_name}[/bold cyan] 启动 AutoDeploy[/green]")
