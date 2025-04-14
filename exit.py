import os
import sys

def exit_virtualenv():
    """退出虚拟环境"""
    if "VIRTUAL_ENV" in os.environ:
        print("[✓] 退出虚拟环境...")
        os.environ["VIRTUAL_ENV"] = ""
        sys.path = [p for p in sys.path if not p.startswith(os.environ["VIRTUAL_ENV"])]
        # 手动调用 deactivate 脚本
        deactivate_script = os.path.join(os.environ["VIRTUAL_ENV"], "bin", "deactivate")
        if os.path.exists(deactivate_script):
            exec(open(deactivate_script).read())
    else:
        print("[✓] 没有激活虚拟环境，跳过退出。")

def main():
    exit_virtualenv()
    sys.exit(0)  # 退出脚本，回到宿主机终端

if __name__ == "__main__":
    main()
