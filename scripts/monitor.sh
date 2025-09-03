#!/bin/bash
# -*- coding: utf-8 -*-
# 股票服务监控脚本 / Stock Services Monitoring Script

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

# 显示标题 / Display title
show_title() {
    echo -e "${CYAN}========================================"
    echo "股票服务监控面板 / Stock Services Monitor"
    echo "服务器IP: 35.77.54.203"
    echo "监控时间: $(date)"
    echo -e "========================================${NC}"
}

# 检查服务状态 / Check service status
check_service_status() {
    log_info "检查服务状态 / Checking service status"
    echo "----------------------------------------"
    
    services=(
        "3003:中国股票服务:Chinese Stock Service"
        "3004:美国股票服务:US Stock Service"  
        "3005:中国期货服务:Chinese Futures Service"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r port name_cn name_en <<< "$service"
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            pid=$(lsof -ti:$port)
            cpu_usage=$(ps -p $pid -o %cpu --no-headers 2>/dev/null | tr -d ' ' || echo "N/A")
            mem_usage=$(ps -p $pid -o %mem --no-headers 2>/dev/null | tr -d ' ' || echo "N/A")
            
            echo -e "${GREEN}✓${NC} 端口 $port ($name_cn) - ${GREEN}运行中${NC}"
            echo "  PID: $pid | CPU: ${cpu_usage}% | 内存: ${mem_usage}%"
            
            # 测试API响应 / Test API response
            if curl -s --max-time 5 "http://35.77.54.203:$port/health" > /dev/null 2>&1; then
                echo -e "  API状态: ${GREEN}正常${NC}"
            else
                echo -e "  API状态: ${RED}异常${NC}"
            fi
        else
            echo -e "${RED}✗${NC} 端口 $port ($name_cn) - ${RED}未运行${NC}"
        fi
        echo
    done
}

# 检查数据库状态 / Check database status
check_database_status() {
    log_info "检查数据库状态 / Checking database status"
    echo "----------------------------------------"
    
    if sudo systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✓${NC} PostgreSQL服务: ${GREEN}运行中${NC}"
        
        # 检查数据库连接 / Check database connection
        if python3 -c "from database import test_database_connection; exit(0 if test_database_connection() else 1)" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} 数据库连接: ${GREEN}正常${NC}"
        else
            echo -e "${RED}✗${NC} 数据库连接: ${RED}异常${NC}"
        fi
        
        # 显示数据库统计 / Show database statistics
        python3 -c "
from database import SessionLocal, ChineseStock, USStock, ChineseFutures
try:
    db = SessionLocal()
    chinese_stocks = db.query(ChineseStock).filter(ChineseStock.is_active == True).count()
    us_stocks = db.query(USStock).filter(USStock.is_active == True).count()  
    futures = db.query(ChineseFutures).filter(ChineseFutures.is_active == True).count()
    db.close()
    print(f'  中国股票: {chinese_stocks} 条记录')
    print(f'  美国股票: {us_stocks} 条记录')
    print(f'  中国期货: {futures} 条记录')
except Exception as e:
    print(f'  数据统计获取失败: {str(e)}')
" 2>/dev/null || echo "  无法获取数据库统计信息"
    else
        echo -e "${RED}✗${NC} PostgreSQL服务: ${RED}未运行${NC}"
    fi
    echo
}

# 显示系统资源使用情况 / Show system resource usage
show_system_resources() {
    log_info "系统资源使用情况 / System resource usage"
    echo "----------------------------------------"
    
    # CPU使用率 / CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    echo "CPU使用率: ${cpu_usage}%"
    
    # 内存使用情况 / Memory usage
    mem_info=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
    echo "内存使用率: $mem_info"
    
    # 磁盘使用情况 / Disk usage
    disk_usage=$(df -h . | awk 'NR==2 {print $5}')
    echo "磁盘使用率: $disk_usage"
    
    # 网络连接数 / Network connections
    connections=$(netstat -an | grep -c ESTABLISHED)
    echo "网络连接数: $connections"
    echo
}

# 显示最近的日志 / Show recent logs
show_recent_logs() {
    log_info "最近的服务日志 / Recent service logs"
    echo "----------------------------------------"
    
    log_files=("chinese_stock.log" "us_stock.log" "futures.log")
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "logs/$log_file" ]]; then
            echo -e "${CYAN}=== $log_file (最近5行) ===${NC}"
            tail -5 "logs/$log_file" | sed 's/^/  /' || echo "  无法读取日志文件"
            echo
        fi
    done
}

# 显示API端点信息 / Show API endpoints
show_api_endpoints() {
    log_info "API端点信息 / API endpoints"
    echo "----------------------------------------"
    echo "中国股票服务 (端口 3003):"
    echo "  - 服务状态: http://35.77.54.203:3003/"
    echo "  - API文档: http://35.77.54.203:3003/docs"
    echo "  - 健康检查: http://35.77.54.203:3003/health"
    echo
    echo "美国股票服务 (端口 3004):"
    echo "  - 服务状态: http://35.77.54.203:3004/"
    echo "  - API文档: http://35.77.54.203:3004/docs"
    echo "  - 健康检查: http://35.77.54.203:3004/health"
    echo
    echo "中国期货服务 (端口 3005):"
    echo "  - 服务状态: http://35.77.54.203:3005/"
    echo "  - API文档: http://35.77.54.203:3005/docs"
    echo "  - 健康检查: http://35.77.54.203:3005/health"
    echo
}

# 自动重启异常服务 / Auto restart failed services
auto_restart_services() {
    if [[ "$1" == "--auto-restart" ]]; then
        log_info "检查并自动重启异常服务 / Checking and auto-restarting failed services"
        
        services_to_restart=()
        
        # 检查各服务状态 / Check service status
        if ! lsof -Pi :3003 -sTCP:LISTEN -t >/dev/null; then
            services_to_restart+=("chinese_stock_api.py")
        fi
        
        if ! lsof -Pi :3004 -sTCP:LISTEN -t >/dev/null; then
            services_to_restart+=("us_stock_api.py")
        fi
        
        if ! lsof -Pi :3005 -sTCP:LISTEN -t >/dev/null; then
            services_to_restart+=("futures_api.py")
        fi
        
        # 重启异常服务 / Restart failed services
        if [[ ${#services_to_restart[@]} -gt 0 ]]; then
            log_warning "发现 ${#services_to_restart[@]} 个服务异常，正在重启 / Found ${#services_to_restart[@]} failed services, restarting"
            
            for service in "${services_to_restart[@]}"; do
                log_info "正在重启 $service / Restarting $service"
                nohup python3 "$service" > "logs/${service%.*}.log" 2>&1 &
                sleep 3
            done
            
            log_success "服务重启完成 / Service restart completed"
        else
            log_success "所有服务运行正常 / All services running normally"
        fi
    fi
}

# 连续监控模式 / Continuous monitoring mode
continuous_monitor() {
    if [[ "$1" == "--watch" ]]; then
        while true; do
            clear
            show_title
            check_service_status
            check_database_status
            show_system_resources
            
            echo "----------------------------------------"
            echo "按 Ctrl+C 退出监控 / Press Ctrl+C to exit monitoring"
            echo "下次更新: $(date -d '+30 seconds')"
            
            sleep 30
        done
    fi
}

# 显示帮助信息 / Show help information
show_help() {
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "股票服务监控脚本使用说明 / Stock Services Monitor Usage"
        echo "----------------------------------------"
        echo "./monitor.sh                 - 执行一次性监控检查"
        echo "./monitor.sh --watch         - 连续监控模式（30秒刷新）"
        echo "./monitor.sh --auto-restart  - 检查并自动重启异常服务"
        echo "./monitor.sh --help          - 显示此帮助信息"
        echo "----------------------------------------"
        exit 0
    fi
}

# 主函数 / Main function
main() {
    show_help "$1"
    continuous_monitor "$1"
    
    show_title
    check_service_status
    check_database_status
    show_system_resources
    
    if [[ "$1" != "--simple" ]]; then
        show_recent_logs
        show_api_endpoints
    fi
    
    auto_restart_services "$1"
    
    echo -e "${CYAN}========================================${NC}"
    log_success "监控检查完成 / Monitoring check completed"
}

# 执行主函数 / Execute main function
main "$1"