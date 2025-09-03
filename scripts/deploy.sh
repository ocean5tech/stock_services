#!/bin/bash

# 股票分析服务部署脚本
# Stock Analysis Service Deployment Script

set -e  # 遇到错误立即退出

echo "🚀 开始部署股票分析服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="/home/ubuntu/stock_services"
LOG_DIR="${PROJECT_DIR}/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 --version | awk '{print $2}')
    log_info "Python版本: $python_version"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
}

# 停止现有服务
stop_existing_services() {
    log_info "停止现有服务..."
    
    # 停止端口3003上的进程
    if lsof -ti:3003 2>/dev/null; then
        log_warn "发现端口3003上的进程，正在停止..."
        fuser -k 3003/tcp || true
        sleep 2
    fi
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$PROJECT_DIR"
    
    # 安装核心依赖
    pip3 install fastapi==0.104.1 --break-system-packages || {
        log_error "安装FastAPI失败"
        exit 1
    }
    
    pip3 install uvicorn==0.24.0 --break-system-packages || {
        log_error "安装Uvicorn失败" 
        exit 1
    }
    
    pip3 install akshare==1.17.42 --break-system-packages || {
        log_error "安装AKShare失败"
        exit 1
    }
    
    log_info "Python依赖安装完成"
}

# 验证API文件
validate_api_files() {
    log_info "验证API文件..."
    
    if [ ! -f "$PROJECT_DIR/api/stock_analysis_api.py" ]; then
        log_error "股票分析API文件不存在: api/stock_analysis_api.py"
        exit 1
    fi
    
    # 语法检查
    if ! python3 -m py_compile "$PROJECT_DIR/api/stock_analysis_api.py"; then
        log_error "API文件语法错误"
        exit 1
    fi
    
    log_info "API文件验证通过"
}

# 启动服务
start_services() {
    log_info "启动股票分析API服务..."
    
    cd "$PROJECT_DIR"
    
    # 启动股票分析API (端口3003)
    nohup python3 -m uvicorn api.stock_analysis_api:app --host 0.0.0.0 --port 3003 \
        > "$LOG_DIR/stock_api.log" 2>&1 &
    
    API_PID=$!
    echo $API_PID > "$LOG_DIR/stock_api.pid"
    
    log_info "股票分析API启动完成，PID: $API_PID"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查股票分析API
    if curl -s -f "http://127.0.0.1:3003/" > /dev/null; then
        log_info "✅ 股票分析API (端口3003) 健康检查通过"
        return 0
    else
        log_error "❌ 股票分析API (端口3003) 健康检查失败"
        return 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info "📊 部署信息汇总"
    echo "==========================================="
    echo "🚀 服务状态:"
    echo "   - 股票分析API: http://35.77.54.203:3003"
    echo ""
    echo "📖 API文档:"
    echo "   - Swagger UI: http://35.77.54.203:3003/docs"
    echo "   - ReDoc: http://35.77.54.203:3003/redoc"
    echo ""
    echo "📝 日志文件:"
    echo "   - API日志: $LOG_DIR/stock_api.log"
    echo "   - 部署日志: $LOG_DIR/deploy.log"
    echo "==========================================="
}

# 主函数
main() {
    echo "开始时间: $(date)" >> "$LOG_DIR/deploy.log"
    
    check_dependencies
    stop_existing_services
    install_python_dependencies
    validate_api_files
    start_services
    
    # 等待服务稳定
    sleep 3
    
    if health_check; then
        log_info "🎉 部署成功完成!"
        show_deployment_info
    else
        log_error "⚠️ 部署完成但健康检查失败，请检查日志"
        exit 1
    fi
    
    echo "结束时间: $(date)" >> "$LOG_DIR/deploy.log"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
