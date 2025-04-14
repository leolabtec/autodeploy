import os
import sys

def exit_virtualenv():
    """退出虚拟环境"""
    if "VIRTUAL_ENV" in os.environ:
        print("[✓] 退出虚拟环境...")

        # 清除虚拟环境环境变量
        os.environ["VIRTUAL_ENV"] = ""
        # 移除虚拟环境的路径
        sys.path = [p for p in sys.path if not p.startswith(os.environ["VIRTUAL_ENV"])]
        
        # 手动调用 deactivate 脚本
        deactivate_script = os.path.join(os.environ["VIRTUAL_ENV"], "bin", "deactivate")
        if os.path.exists(deactivate_script):
            try:
                exec(open(deactivate_script).read())  # 执行 deactivate 脚本
            except Exception as e:
                print(f"[!] 错误：无法执行 deactivate 脚本: {e}")
        else:
            print("[!] 没有找到 deactivate 脚本，虚拟环境可能已被退出。")
    else:
        print("[✓] 没有激活虚拟环境，跳过退出。")

def main():
    exit_virtualenv()
    sys.exit(0)  # 退出脚本，回到宿主机终端

if __name__ == "__main__":
    main()
