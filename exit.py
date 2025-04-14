import subprocess

def exit_virtualenv():
    """模拟用户在虚拟环境中直接输入 deactivate"""
    try:
        # 使用 subprocess 调用 deactivate 命令，模拟用户输入并退出虚拟环境
        subprocess.run(["deactivate"], check=True, shell=True)
        print("[✓] 已退出虚拟环境。")
    except subprocess.CalledProcessError as e:
        print(f"[!] 退出虚拟环境失败: {e}")

def main():
    exit_virtualenv()

if __name__ == "__main__":
    main()
