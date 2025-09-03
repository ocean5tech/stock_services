#!/bin/bash

# 服务重启脚本
# Service Restart Script

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/ubuntu/stock_services"

echo -e "${YELLOW}🔄 正在重启股票分析服务...${NC}"

# 确保脚本从项目根目录运行
cd "$PROJECT_DIR"

# 停止服务
echo -e "${YELLOW}步骤 1/2: 停止现有服务${NC}"
./scripts/stop.sh

# 等待服务完全停止
sleep 3

# 启动服务
echo -e "${YELLOW}步骤 2/2: 启动服务${NC}"
./scripts/deploy.sh

echo -e "${GREEN}🎉 服务重启完成!${NC}"
