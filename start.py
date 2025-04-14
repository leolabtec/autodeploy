# start_autodeploy.py

import os
import subprocess

# 获取虚拟环境路径
virtualenv_dir = "/opt/autodeploy/.venv/bin/activate"
main_py = "/opt/autodeploy/main.py"

# 使用 subprocess 执行命令
subprocess.call(f"source {virtualenv_dir} && python {main_py}", shell=True, executable="/bin/bash")
