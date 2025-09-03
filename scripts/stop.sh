#!/bin/bash

# 服务停止脚本
# Service Stop Script

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/ubuntu/stock_services"
LOG_DIR="${PROJECT_DIR}/logs"

echo -e "${YELLOW}🛑 正在停止股票分析服务...${NC}"

# 停止API服务
stop_service() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}停止 $service_name (端口 $port)...${NC}"
        fuser -k $port/tcp
        sleep 2
        
        # 确认进程已停止
        if lsof -ti:$port > /dev/null 2>&1; then
            echo -e "${RED}强制停止 $service_name...${NC}"
            fuser -9 -k $port/tcp
            sleep 1
        fi
        
        if ! lsof -ti:$port > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name 已停止${NC}"
        else
            echo -e "${RED}❌ 无法停止 $service_name${NC}"
        fi
    else
        echo -e "${GREEN}$service_name 未在运行${NC}"
    fi
}

# 清理PID文件
cleanup_pid_files() {
    if [ -f "$LOG_DIR/stock_api.pid" ]; then
        rm -f "$LOG_DIR/stock_api.pid"
        echo -e "${GREEN}清理PID文件完成${NC}"
    fi
}

# 主函数
main() {
    # 停止各个服务
    stop_service 3003 "股票分析API"
    stop_service 3004 "美股API"
    stop_service 3005 "期货API"
    
    # 清理PID文件
    cleanup_pid_files
    
    echo -e "${GREEN}🎉 所有服务已停止${NC}"
    
    # 记录停止时间
    echo "服务停止时间: $(date)" >> "$LOG_DIR/stop.log"
}

main "$@"
