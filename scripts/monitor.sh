#!/bin/bash

# 服务监控脚本
# Service Monitoring Script

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/ubuntu/stock_services"
LOG_DIR="${PROJECT_DIR}/logs"

# 显示标题
show_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    股票分析服务监控面板${NC}"
    echo -e "${BLUE}    Stock Analysis Service Monitor${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 检查端口状态
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name (端口 $port): 运行中${NC}"
        
        # 获取进程信息
        local pid=$(lsof -ti:$port)
        local cpu_mem=$(ps -o pid,pcpu,pmem,cmd -p $pid 2>/dev/null | tail -n 1)
        echo -e "   进程信息: $cpu_mem"
        
        # 健康检查
        if curl -s -f "http://127.0.0.1:$port/" > /dev/null 2>&1; then
            echo -e "${GREEN}   HTTP健康检查: 通过${NC}"
        else
            echo -e "${YELLOW}   HTTP健康检查: 失败${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ $service_name (端口 $port): 未运行${NC}"
        return 1
    fi
}

# 检查API端点
check_api_endpoints() {
    echo -e "${BLUE}🔗 API端点检查:${NC}"
    
    local base_url="http://127.0.0.1:3003"
    
    # 健康检查端点
    if curl -s -f "$base_url/" > /dev/null 2>&1; then
        echo -e "${GREEN}   / : 正常${NC}"
    else
        echo -e "${RED}   / : 失败${NC}"
    fi
    
    # 基本面分析端点
    if timeout 10 curl -s -f "$base_url/stocks/000001/analysis/fundamental" > /dev/null 2>&1; then
        echo -e "${GREEN}   基本面分析: 正常${NC}"
    else
        echo -e "${YELLOW}   基本面分析: 超时或失败${NC}"
    fi
    
    # 技术面分析端点
    if timeout 10 curl -s -f "$base_url/stocks/000001/analysis/technical" > /dev/null 2>&1; then
        echo -e "${GREEN}   技术面分析: 正常${NC}"
    else
        echo -e "${YELLOW}   技术面分析: 超时或失败${NC}"
    fi
    
    # 消息面分析端点
    if curl -s -f "$base_url/stocks/000001/news/announcements" > /dev/null 2>&1; then
        echo -e "${GREEN}   消息面分析: 正常${NC}"
    else
        echo -e "${YELLOW}   消息面分析: 失败（预期，占位符接口）${NC}"
    fi
}

# 显示日志信息
show_logs() {
    echo -e "${BLUE}📝 最新日志 (最后10行):${NC}"
    
    if [ -f "$LOG_DIR/stock_api.log" ]; then
        echo -e "${YELLOW}--- API服务日志 ---${NC}"
        tail -n 10 "$LOG_DIR/stock_api.log" 2>/dev/null || echo "无法读取API日志"
        echo ""
    fi
    
    if [ -f "$LOG_DIR/deploy.log" ]; then
        echo -e "${YELLOW}--- 部署日志 ---${NC}"
        tail -n 5 "$LOG_DIR/deploy.log" 2>/dev/null || echo "无法读取部署日志"
        echo ""
    fi
}

# 显示系统资源
show_system_resources() {
    echo -e "${BLUE}💻 系统资源:${NC}"
    
    # CPU使用率
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    echo -e "   CPU使用率: ${cpu_usage}%"
    
    # 内存使用
    local mem_info=$(free -h | grep "Mem:")
    echo -e "   内存使用: $mem_info"
    
    # 磁盘使用
    local disk_usage=$(df -h / | tail -n 1 | awk '{print $5}')
    echo -e "   磁盘使用: $disk_usage"
    
    echo ""
}

# 显示快捷命令
show_commands() {
    echo -e "${BLUE}🔧 管理命令:${NC}"
    echo "   启动服务: ./scripts/deploy.sh"
    echo "   停止服务: ./scripts/stop.sh"  
    echo "   重启服务: ./scripts/restart.sh"
    echo "   查看日志: tail -f logs/stock_api.log"
    echo ""
}

# 持续监控模式
continuous_monitor() {
    while true; do
        clear
        show_header
        
        # 检查服务状态
        echo -e "${BLUE}🚀 服务状态:${NC}"
        check_port 3003 "股票分析API"
        echo ""
        
        # 检查API端点
        check_api_endpoints
        echo ""
        
        # 显示系统资源
        show_system_resources
        
        # 显示时间戳
        echo -e "${BLUE}⏰ 更新时间: $(date)${NC}"
        echo -e "${YELLOW}按 Ctrl+C 退出监控模式${NC}"
        
        sleep 10
    done
}

# 自动重启模式
auto_restart() {
    echo -e "${YELLOW}🔄 启动自动重启监控...${NC}"
    
    while true; do
        if ! check_port 3003 "股票分析API" > /dev/null 2>&1; then
            echo -e "${RED}检测到服务异常，正在重启...${NC}"
            cd "$PROJECT_DIR"
            ./scripts/deploy.sh
            sleep 30
        fi
        
        sleep 60  # 每分钟检查一次
    done
}

# 主函数
main() {
    case "${1:-status}" in
        "status"|"")
            show_header
            
            # 检查服务状态
            echo -e "${BLUE}🚀 服务状态:${NC}"
            check_port 3003 "股票分析API"
            echo ""
            
            # 检查API端点
            check_api_endpoints
            echo ""
            
            # 显示系统资源
            show_system_resources
            
            # 显示管理命令
            show_commands
            ;;
            
        "watch"|"-w"|"--watch")
            continuous_monitor
            ;;
            
        "auto-restart"|"-r"|"--auto-restart")
            auto_restart
            ;;
            
        "logs"|"-l"|"--logs")
            show_logs
            ;;
            
        "help"|"-h"|"--help")
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  status, (默认)     显示服务状态"
            echo "  watch, -w          持续监控模式"
            echo "  auto-restart, -r   自动重启异常服务"
            echo "  logs, -l           显示最新日志"
            echo "  help, -h           显示帮助信息"
            ;;
            
        *)
            echo -e "${RED}未知选项: $1${NC}"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
