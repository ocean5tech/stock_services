#!/bin/bash
# -*- coding: utf-8 -*-
# 股票服务部署脚本 / Stock Services Deployment Script
# 服务器IP: 35.77.54.203

set -e  # 遇到错误立即退出 / Exit immediately on error

echo "========================================"
echo "股票服务部署开始 / Stock Services Deployment Starting"
echo "服务器IP: 35.77.54.203"
echo "部署时间: $(date)"
echo "========================================"

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数 / Logging functions
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

# 检查是否以root用户运行 / Check if running as root user
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "检测到以root用户运行，建议使用普通用户 / Running as root user detected, recommend using normal user"
    fi
}

# 检查系统依赖 / Check system dependencies
check_dependencies() {
    log_info "检查系统依赖 / Checking system dependencies"
    
    # 检查Python / Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装 / Python3 not installed"
        exit 1
    fi
    log_success "Python3: $(python3 --version)"
    
    # 检查pip / Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3未安装 / pip3 not installed"
        exit 1
    fi
    log_success "pip3: $(pip3 --version)"
    
    # 检查PostgreSQL / Check PostgreSQL
    if ! sudo systemctl is-active --quiet postgresql; then
        log_warning "PostgreSQL服务未运行，正在启动 / PostgreSQL service not running, starting..."
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi
    log_success "PostgreSQL服务正在运行 / PostgreSQL service is running"
}

# 停止现有服务 / Stop existing services
stop_existing_services() {
    log_info "停止现有服务进程 / Stopping existing service processes"
    
    # 查找并终止占用端口的进程 / Find and kill processes using the ports
    for port in 3003 3004 3005; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            log_warning "端口 $port 被占用，正在终止进程 / Port $port is occupied, terminating process"
            sudo lsof -ti:$port | sudo xargs kill -9 2>/dev/null || true
            sleep 2
        fi
    done
    
    log_success "所有端口已释放 / All ports have been freed"
}

# 创建数据库 / Create database
setup_database() {
    log_info "设置数据库 / Setting up database"
    
    # 创建数据库用户和数据库 / Create database user and database
    sudo -u postgres psql -c "CREATE DATABASE stock_services;" 2>/dev/null || log_warning "数据库stock_services可能已存在 / Database stock_services may already exist"
    sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || log_warning "用户postgres可能已存在 / User postgres may already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stock_services TO postgres;" 2>/dev/null || true
    
    log_success "数据库设置完成 / Database setup completed"
}

# 安装Python依赖 / Install Python dependencies
install_dependencies() {
    log_info "安装Python依赖 / Installing Python dependencies"
    
    # 升级pip / Upgrade pip
    python3 -m pip install --upgrade pip
    
    # 安装依赖 / Install dependencies
    pip3 install -r requirements.txt
    
    log_success "Python依赖安装完成 / Python dependencies installed"
}

# 初始化数据库表 / Initialize database tables
init_database() {
    log_info "初始化数据库表 / Initializing database tables"
    
    python3 -c "
import sys; sys.path.append('./api')
from database import init_database, test_database_connection
if test_database_connection():
    print('数据库连接成功 / Database connection successful')
    if init_database():
        print('数据库表初始化成功 / Database tables initialized successfully')
    else:
        print('数据库表初始化失败 / Database tables initialization failed')
        exit(1)
else:
    print('数据库连接失败 / Database connection failed')
    exit(1)
"
    
    log_success "数据库初始化完成 / Database initialization completed"
}

# 启动服务 / Start services
start_services() {
    log_info "启动服务 / Starting services"
    
    # 创建日志目录 / Create log directory
    mkdir -p logs
    
    # 启动中国股票服务 / Start Chinese stock service
    log_info "启动中国股票服务 (端口 3003) / Starting Chinese stock service (port 3003)"
    nohup python3 api/chinese_stock_api.py > logs/chinese_stock.log 2>&1 &
    sleep 3
    
    # 启动美国股票服务 / Start US stock service
    log_info "启动美国股票服务 (端口 3004) / Starting US stock service (port 3004)"
    nohup python3 api/us_stock_api.py > logs/us_stock.log 2>&1 &
    sleep 3
    
    # 启动中国期货服务 / Start Chinese futures service
    log_info "启动中国期货服务 (端口 3005) / Starting Chinese futures service (port 3005)"
    nohup python3 api/futures_api.py > logs/futures.log 2>&1 &
    sleep 3
    
    log_success "所有服务启动完成 / All services started"
}

# 验证服务状态 / Verify service status
verify_services() {
    log_info "验证服务状态 / Verifying service status"
    
    # 检查服务端口 / Check service ports
    for port in 3003 3004 3005; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            log_success "端口 $port 服务正在运行 / Service on port $port is running"
        else
            log_error "端口 $port 服务未运行 / Service on port $port is not running"
            return 1
        fi
    done
    
    # 测试API端点 / Test API endpoints
    sleep 10  # 等待服务完全启动 / Wait for services to fully start
    
    log_info "测试API端点 / Testing API endpoints"
    
    # 测试中国股票服务 / Test Chinese stock service
    if curl -s "http://35.77.54.203:3003/" > /dev/null; then
        log_success "中国股票服务API响应正常 / Chinese stock service API responding normally"
    else
        log_error "中国股票服务API无响应 / Chinese stock service API not responding"
    fi
    
    # 测试美国股票服务 / Test US stock service
    if curl -s "http://35.77.54.203:3004/" > /dev/null; then
        log_success "美国股票服务API响应正常 / US stock service API responding normally"
    else
        log_error "美国股票服务API无响应 / US stock service API not responding"
    fi
    
    # 测试中国期货服务 / Test Chinese futures service
    if curl -s "http://35.77.54.203:3005/" > /dev/null; then
        log_success "中国期货服务API响应正常 / Chinese futures service API responding normally"
    else
        log_error "中国期货服务API无响应 / Chinese futures service API not responding"
    fi
}

# 显示服务信息 / Display service information
show_service_info() {
    log_info "服务信息 / Service Information"
    echo "========================================"
    echo "服务器IP: 35.77.54.203"
    echo "中国股票服务: http://35.77.54.203:3003"
    echo "美国股票服务: http://35.77.54.203:3004" 
    echo "中国期货服务: http://35.77.54.203:3005"
    echo "========================================"
    echo "API文档地址 / API Documentation URLs:"
    echo "中国股票API文档: http://35.77.54.203:3003/docs"
    echo "美国股票API文档: http://35.77.54.203:3004/docs"
    echo "中国期货API文档: http://35.77.54.203:3005/docs"
    echo "========================================"
    echo "日志文件位置 / Log file locations:"
    echo "中国股票服务日志: ./logs/chinese_stock.log"
    echo "美国股票服务日志: ./logs/us_stock.log"
    echo "中国期货服务日志: ./logs/futures.log"
    echo "========================================"
}

# 主函数 / Main function
main() {
    check_root
    check_dependencies
    stop_existing_services
    setup_database
    install_dependencies
    init_database
    start_services
    verify_services
    show_service_info
    
    log_success "股票服务部署完成 / Stock services deployment completed successfully!"
}

# 错误处理 / Error handling
trap 'log_error "部署过程中发生错误 / Error occurred during deployment"; exit 1' ERR

# 执行主函数 / Execute main function
main