"""项目入口 - 同时启动前后端服务"""
import subprocess
import sys
import os
import signal

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


def main():
    processes = []

    try:
        # 启动后端
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--reload", "--host", "127.0.0.1", "--port", "8001"],
            cwd=PROJECT_DIR,
        )
        processes.append(backend)
        print("[✓] 后端已启动: http://127.0.0.1:8001")

        # 启动前端
        frontend = subprocess.Popen(
            ["npx", "vite", "--port", "5173", "--host", "127.0.0.1"],
            cwd=FRONTEND_DIR,
        )
        processes.append(frontend)
        print("[✓] 前端已启动: http://127.0.0.1:5173")

        print("\n按 Ctrl+C 停止所有服务\n")

        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n正在停止服务...")
        for p in processes:
            p.send_signal(signal.SIGTERM)
        for p in processes:
            p.wait()
        print("[✓] 所有服务已停止")


if __name__ == "__main__":
    main()
