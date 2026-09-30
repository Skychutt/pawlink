"""已弃用：请直接用项目 .venv 运行 run.py。

Windows 上 os.execv 会让 PyCharm 误判进程已结束，导致一点运行就立刻结束。
"""

raise SystemExit(
    "请不要再运行 pycharm_launcher.py。\n"
    "在 PyCharm 运行配置里把 Script path 改成项目里的 run.py，\n"
    "并把解释器选成 .venv\\Scripts\\python.exe。"
)
