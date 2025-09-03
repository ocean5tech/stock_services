#!/bin/bash
# -*- coding: utf-8 -*-
# 停止股票服务脚本 / Stop Stock Services Script

set -e

echo "========================================"
echo "停止股票服务 / Stopping Stock Services"
echo "========================================"

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 停止服务函数 / Stop services function
stop_services() {
    log_info "正在停止所有股票服务 / Stopping all stock services"
    
    # 停止占用端口3003, 3004, 3005的进程 / Stop processes using ports 3003, 3004, 3005
    for port in 3003 3004 3005; do
        log_info "检查端口 $port / Checking port $port"
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            log_warning "正在停止端口 $port 上的服务 / Stopping service on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
            sleep 2
            
            # 再次检查端口是否已释放 / Check again if port is freed
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
                log_success "端口 $port 已释放 / Port $port has been freed"
            else
                log_error "端口 $port 仍被占用 / Port $port is still occupied"
            fi
        else
            log_info "端口 $port 未被占用 / Port $port is not occupied"
        fi
    done
    
    # 查找并停止可能的Python进程 / Find and stop possible Python processes
    log_info "查找并停止相关Python进程 / Finding and stopping related Python processes"
    
    pkill -f "chinese_stock_api.py" 2>/dev/null && log_info "已停止中国股票服务进程 / Stopped Chinese stock service process" || true
    pkill -f "us_stock_api.py" 2>/dev/null && log_info "已停止美国股票服务进程 / Stopped US stock service process" || true
    pkill -f "futures_api.py" 2>/dev/null && log_info "已停止中国期货服务进程 / Stopped Chinese futures service process" || true
    
    sleep 3
    
    log_success "所有股票服务已停止 / All stock services have been stopped"
}

# 显示端口状态 / Show port status
show_port_status() {
    log_info "当前端口状态 / Current port status"
    echo "========================================"
    
    for port in 3003 3004 3005; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            echo -e "${RED}端口 $port: 被占用${NC}"
            lsof -Pi :$port -sTCP:LISTEN
        else
            echo -e "${GREEN}端口 $port: 空闲${NC}"
        fi
    done
    
    echo "========================================"
}

# 清理日志文件 / Clean log files
clean_logs() {
    if [[ "$1" == "--clean-logs" ]]; then
        log_info "清理日志文件 / Cleaning log files"
        rm -f logs/*.log 2>/dev/null || true
        log_success "日志文件已清理 / Log files have been cleaned"
    fi
}

# 主函数 / Main function
main() {
    stop_services
    show_port_status
    clean_logs "$1"
    
    echo "========================================"
    log_success "股票服务停止完成 / Stock services stop completed"
    echo "如需重新启动服务，请运行: ./deploy.sh"
    echo "To restart services, run: ./deploy.sh"
    echo "========================================"
}

# 执行主函数 / Execute main function
main "$1"