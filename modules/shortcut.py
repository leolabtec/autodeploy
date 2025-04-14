# modules/shortcut.py

import os
import re
from pathlib import Path
from rich import print
from rich.prompt import Prompt, Confirm

ALIAS_TARGET = "python /opt/autodeploy/main.py"

def get_shell_config_file():
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return Path.home() / ".zshrc"
    elif "bash" in shell:
        return Path.home() / ".bashrc"
    else:
        return None

def is_valid_alias(alias):
    # 仅允许 a-z, A-Z, 0-9 和 _
    return re.match(r"^[a-zA-Z0-9_]+$", alias)

def set_alias():
    config_file = get_shell_config_file()
    if not config_file or not config_file.exists():
        print("[red]未检测到合法的 shell 启动文件（.bashrc 或 .zshrc），无法设置快捷方式。[/red]")
        return

    alias_name = Prompt.ask("请输入要设置的快捷键（如 g）").strip()
    if not is_valid_alias(alias_name):
        print("[red]输入无效！快捷键只能包含字母、数字、下划线，不允许命令注入。[/red]")
        return

    alias_line = f"alias {alias_name}='{ALIAS_TARGET}'"
    config_content = config_file.read_text()

    # 检查是否已有 alias 定义
    if f"alias {alias_name}=" in config_content:
        confirm = Confirm.ask(f"[yellow]alias {alias_name} 已存在，是否覆盖？[/yellow]")
        if not confirm:
            print("已取消设置。")
            return

    # 移除原 alias 行（如存在）
    new_lines = []
    for line in config_content.splitlines():
        if not line.strip().startswith(f"alias {alias_name}="):
            new_lines.append(line)
    new_lines.append(alias_line)

    config_file.write_text("\n".join(new_lines) + "\n")
    print(f"[green]✅ 快捷方式设置成功！请运行 `source {config_file}` 或重新打开终端生效。[/green]")

def remove_alias():
    config_file = get_shell_config_file()
    if not config_file or not config_file.exists():
        print("[red]未检测到合法的 shell 启动文件，无法清除。[/red]")
        return

    alias_name = Prompt.ask("请输入要清除的 alias 名称").strip()
    config_content = config_file.read_text()
    if f"alias {alias_name}=" not in config_content:
        print("[yellow]未找到该 alias，无需清除。[/yellow]")
        return

    new_lines = []
    for line in config_content.splitlines():
        if not line.strip().startswith(f"alias {alias_name}="):
            new_lines.append(line)

    config_file.write_text("\n".join(new_lines) + "\n")
    print(f"[green]✅ alias {alias_name} 已移除。[/green]")
