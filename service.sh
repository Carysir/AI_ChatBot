#!/bin/bash
#============================================================
# 服务启停脚本
# 用法:
#   ./service.sh start    - 后台启动前后端
#   ./service.sh stop     - 停止所有服务
#   ./service.sh restart  - 重启
#   ./service.sh status   - 查看状态
#   ./service.sh logs     - 查看日志
#============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT=8001
FRONTEND_PORT=5173
BACKEND_LOG="$PROJECT_DIR/backend.log"
FRONTEND_LOG="$PROJECT_DIR/frontend.log"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

get_backend_pids()  { lsof -ti:"$BACKEND_PORT" 2>/dev/null; }
get_frontend_pids() { lsof -ti:"$FRONTEND_PORT" 2>/dev/null; }

do_start() {
    cd "$PROJECT_DIR"

    if [ -n "$(get_backend_pids)" ]; then
        echo -e "${YELLOW}[!]${NC} 后端已在运行 (端口 $BACKEND_PORT)"
    else
        nohup uv run uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" > "$BACKEND_LOG" 2>&1 &
        echo -n "    等待后端启动"
        for i in $(seq 1 15); do
            sleep 1
            echo -n "."
            if [ -n "$(get_backend_pids)" ]; then break; fi
        done
        echo ""
        if [ -n "$(get_backend_pids)" ]; then
            echo -e "${GREEN}[✓]${NC} 后端已启动 -> http://0.0.0.0:$BACKEND_PORT"
        else
            echo -e "${RED}[✗]${NC} 后端启动失败，查看日志: tail -f $BACKEND_LOG"
        fi
    fi

    if [ -n "$(get_frontend_pids)" ]; then
        echo -e "${YELLOW}[!]${NC} 前端已在运行 (端口 $FRONTEND_PORT)"
    else
        cd "$FRONTEND_DIR"
        nohup npx vite --host 0.0.0.0 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
        echo -n "    等待前端启动"
        for i in $(seq 1 10); do
            sleep 1
            echo -n "."
            if [ -n "$(get_frontend_pids)" ]; then break; fi
        done
        echo ""
        if [ -n "$(get_frontend_pids)" ]; then
            echo -e "${GREEN}[✓]${NC} 前端已启动 -> http://0.0.0.0:$FRONTEND_PORT"
        else
            echo -e "${RED}[✗]${NC} 前端启动失败，查看日志: tail -f $FRONTEND_LOG"
        fi
    fi
}

do_stop() {
    local pids

    pids=$(get_backend_pids)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        echo -e "${GREEN}[✓]${NC} 后端已停止"
    else
        echo -e "${YELLOW}[!]${NC} 后端未运行"
    fi

    pids=$(get_frontend_pids)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        echo -e "${GREEN}[✓]${NC} 前端已停止"
    else
        echo -e "${YELLOW}[!]${NC} 前端未运行"
    fi
}

do_status() {
    if [ -n "$(get_backend_pids)" ]; then
        echo -e "${GREEN}[运行中]${NC} 后端  :$BACKEND_PORT"
    else
        echo -e "${RED}[已停止]${NC} 后端  :$BACKEND_PORT"
    fi

    if [ -n "$(get_frontend_pids)" ]; then
        echo -e "${GREEN}[运行中]${NC} 前端  :$FRONTEND_PORT"
    else
        echo -e "${RED}[已停止]${NC} 前端  :$FRONTEND_PORT"
    fi
}

do_logs() {
    echo "===== 后端日志（最后 20 行）====="
    tail -20 "$BACKEND_LOG" 2>/dev/null || echo "(无日志)"
    echo ""
    echo "===== 前端日志（最后 20 行）====="
    tail -20 "$FRONTEND_LOG" 2>/dev/null || echo "(无日志)"
}

case "$1" in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_stop; sleep 1; do_start ;;
    status)  do_status ;;
    logs)    do_logs ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
