#!/bin/bash
# -*- coding: utf-8 -*-
# 生产环境快速部署脚本 / Production Environment Quick Deployment Script
# 服务器IP: 35.77.54.203

set -e

echo "========================================"
echo "股票服务生产环境部署 / Stock Services Production Deployment"
echo "服务器IP: 35.77.54.203"
echo "========================================"

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 停止现有进程 / Stop existing processes
log_info "停止现有服务进程 / Stopping existing service processes"
for port in 3003 3004 3005; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "停止端口 $port 上的进程 / Stopping process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# 创建虚拟环境（如果不存在）/ Create virtual environment if not exists
if [ ! -d "venv" ]; then
    log_info "创建虚拟环境 / Creating virtual environment"
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖 / Activate virtual environment and install dependencies
log_info "安装Python依赖 / Installing Python dependencies"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 设置数据库 / Setup database
log_info "设置数据库 / Setting up database"
sudo -u postgres createdb stock_services 2>/dev/null || log_warning "数据库可能已存在"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true

# 初始化数据库 / Initialize database
log_info "初始化数据库表 / Initializing database tables"
python3 -c "
import sys; sys.path.append('./api')
from database import test_database_connection, init_database
if test_database_connection():
    init_database()
    print('数据库初始化成功')
else:
    print('数据库连接失败')
    exit(1)
"

# 创建日志目录 / Create logs directory
mkdir -p logs

# 启动服务 / Start services
log_info "启动股票服务 / Starting stock services"

# 中国股票服务 / Chinese Stock Service
log_info "启动中国股票服务 (端口 3003) / Starting Chinese Stock Service (port 3003)"
nohup python3 api/chinese_stock_api.py > logs/chinese_stock.log 2>&1 &
sleep 3

# 美国股票服务 / US Stock Service  
log_info "启动美国股票服务 (端口 3004) / Starting US Stock Service (port 3004)"
nohup python3 api/us_stock_api.py > logs/us_stock.log 2>&1 &
sleep 3

# 中国期货服务 / Chinese Futures Service
log_info "启动中国期货服务 (端口 3005) / Starting Chinese Futures Service (port 3005)"
nohup python3 api/futures_api.py > logs/futures.log 2>&1 &
sleep 5

# 验证服务状态 / Verify service status
log_info "验证服务状态 / Verifying service status"
for port in 3003 3004 3005; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "端口 $port 服务正在运行 / Service on port $port is running"
    else
        log_error "端口 $port 服务启动失败 / Service on port $port failed to start"
    fi
done

# 测试API端点 / Test API endpoints
sleep 5
log_info "测试API端点 / Testing API endpoints"

services=(
    "3003:中国股票服务:Chinese Stock Service"
    "3004:美国股票服务:US Stock Service"
    "3005:中国期货服务:Chinese Futures Service"
)

for service in "${services[@]}"; do
    IFS=':' read -r port name_cn name_en <<< "$service"
    
    if curl -s --max-time 10 "http://35.77.54.203:$port/health" >/dev/null 2>&1; then
        log_success "$name_cn API响应正常 / $name_en API responding normally"
    else
        log_warning "$name_cn API无响应 / $name_en API not responding"
    fi
done

# 显示部署结果 / Show deployment results
echo ""
echo "========================================"
log_success "股票服务部署完成 / Stock Services Deployment Completed"
echo "========================================"
echo "服务访问地址 / Service URLs:"
echo "• 中国股票服务: http://35.77.54.203:3003"
echo "• 美国股票服务: http://35.77.54.203:3004"
echo "• 中国期货服务: http://35.77.54.203:3005"
echo ""
echo "API文档地址 / API Documentation:"
echo "• 中国股票API: http://35.77.54.203:3003/docs"
echo "• 美国股票API: http://35.77.54.203:3004/docs"
echo "• 中国期货API: http://35.77.54.203:3005/docs"
echo ""
echo "管理命令 / Management Commands:"
echo "• 停止服务: ./scripts/stop_services.sh"
echo "• 监控服务: ./scripts/monitor.sh"
echo "• 查看日志: tail -f logs/*.log"
echo ""
echo "数据库信息 / Database Information:"
echo "• 数据库名: stock_services"
echo "• 连接地址: postgresql://postgres:postgres@localhost/stock_services"
echo "========================================"

deactivate 2>/dev/null || true