// Stock Services Frontend Application
class StockApp {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentTaskId = null;
        this.currentStockCode = null;
        this.init();
    }

    init() {
        // 编译Handlebars模板
        this.compileTemplates();
        
        // 绑定事件
        this.bindEvents();
        
        // 检查API状态
        this.checkApiStatus();
        
        // 初始化主题
        this.initTheme();
    }

    compileTemplates() {
        // 编译股票信息模板
        const stockTemplateSource = document.getElementById('stock-template').innerHTML;
        this.stockTemplate = Handlebars.compile(stockTemplateSource);
        
        // 编译API状态模板
        const apiStatusTemplateSource = document.getElementById('api-status-template').innerHTML;
        this.apiStatusTemplate = Handlebars.compile(apiStatusTemplateSource);
        
        // 注册Handlebars helpers
        Handlebars.registerHelper('formatTime', function(timestamp) {
            return new Date(timestamp).toLocaleString('zh-CN');
        });
        
        Handlebars.registerHelper('formatAnalysis', function(text) {
            if (!text) return '';
            // 将文本转换为HTML，保持段落格式
            return new Handlebars.SafeString(
                text.replace(/\n\n/g, '</p><p>')
                    .replace(/\n/g, '<br>')
                    .replace(/^/, '<p>')
                    .replace(/$/, '</p>')
            );
        });
        
        Handlebars.registerHelper('stringify', function(obj) {
            return JSON.stringify(obj, null, 2);
        });
        
        Handlebars.registerHelper('eq', function(a, b) {
            return a === b;
        });
    }

    bindEvents() {
        // 搜索按钮点击事件
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchStock();
        });
        
        // 输入框回车事件
        document.getElementById('stock-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchStock();
            }
        });
        
        // 主题切换事件
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    async searchStock() {
        const stockCode = document.getElementById('stock-input').value.trim();
        if (!stockCode) {
            alert('请输入股票代码');
            return;
        }

        // 显示加载状态
        const stockInfoDiv = document.getElementById('stock-info');
        stockInfoDiv.className = 'stock-card';
        stockInfoDiv.innerHTML = `
            <div class="flex items-center justify-center py-12">
                <div class="loading-spinner mr-2"></div>
                <div>
                    <p class="font-semibold">正在分析股票 ${stockCode}...</p>
                    <p class="text-sm text-gray-600 mt-1">调用n8n专业分析，请等待...</p>
                </div>
            </div>
        `;

        try {
            // 调用Vercel API
            const response = await fetch(`${this.apiBase}/api/vercel/stock-analysis?code=${stockCode}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // 处理数据格式
            const processedData = this.processStockData(data);
            
            // 保存股票代码用于检查结果
            this.currentStockCode = processedData.stock_code;
            
            // 渲染股票信息
            stockInfoDiv.innerHTML = this.stockTemplate(processedData);
            stockInfoDiv.className = '';
            
            // 绑定检查结果按钮
            this.bindCheckResultButton();
            
        } catch (error) {
            console.error('查询股票信息失败:', error);
            stockInfoDiv.innerHTML = `
                <div class="stock-card">
                    <div class="text-center py-8 text-stock-red">
                        <p>❌ 查询失败: ${error.message}</p>
                        <p class="text-sm text-gray-600 mt-2">请检查股票代码是否正确</p>
                    </div>
                </div>
            `;
        }
    }

    processStockData(data) {
        // 简单处理n8n返回的分析数据
        return {
            stock_code: data.stock_code,
            data_source: data.data_source || 'n8n_workflow',
            timestamp: data.timestamp || new Date().toISOString(),
            status: data.status || 'completed',
            analysis: data.analysis || null,
            error: data.error || null
        };
    }

    async checkApiStatus() {
        const apiEndpoints = [
            { name: 'Vercel股票分析API', url: '/api/vercel/stock-analysis?code=000001', online: false }
        ];

        for (const endpoint of apiEndpoints) {
            try {
                const response = await fetch(`${this.apiBase}${endpoint.url}`, { 
                    timeout: 5000,
                    signal: AbortSignal.timeout(5000)
                });
                endpoint.online = response.ok;
            } catch (error) {
                console.log(`API检查失败: ${endpoint.name}`, error);
                endpoint.online = false;
            }
        }

        // 渲染API状态
        const apiStatusDiv = document.getElementById('api-status');
        apiStatusDiv.innerHTML = this.apiStatusTemplate({ endpoints: apiEndpoints });
    }

    initTheme() {
        // 检查本地存储的主题设置
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.body.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        const themeToggle = document.getElementById('theme-toggle');
        
        if (theme === 'dark') {
            document.body.classList.add('dark', 'bg-bg-dark', 'text-white');
            document.body.classList.remove('bg-bg-light');
            themeToggle.textContent = '☀️ 亮色模式';
        } else {
            document.body.classList.remove('dark', 'bg-bg-dark', 'text-white');
            document.body.classList.add('bg-bg-light');
            themeToggle.textContent = '🌙 暗色模式';
        }
        
        localStorage.setItem('theme', theme);
    }

    bindRefreshButton() {
        // 绑定刷新按钮事件（动态添加的元素）
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.checkAnalysisResult();
            });
        }
    }

    startPolling() {
        // 已禁用自动轮询 - 完全由用户手动控制
        console.log('⚠️ 自动轮询已禁用，请使用手动检查按钮');
        return;
        
        // 以下代码已注释掉避免自动执行
        /*
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        let pollCount = 0;
        let failureCount = 0;
        const maxPolls = 8;
        const maxFailures = 1;
        
        console.log(`开始自动检查，最多检查${maxPolls}次，允许${maxFailures}次失败`);
        
        this.pollingInterval = setInterval(async () => {
            pollCount++;
            console.log(`自动检查分析结果 (${pollCount}/${maxPolls})`);
            
            try {
                const hasResult = await this.checkAnalysisResult(true);
                
                if (hasResult) {
                    console.log('✅ 获得分析结果，停止轮询');
                    clearInterval(this.pollingInterval);
                    this.pollingInterval = null;
                    return;
                }
                
                failureCount = 0;
                
            } catch (error) {
                failureCount++;
                console.error(`检查失败 (${failureCount}/${maxFailures}):`, error);
                
                if (failureCount >= maxFailures) {
                    console.log('❌ 检查失败，立即停止自动检查');
                    this.showPollingFailure('检查失败，已停止自动重试以保护token');
                    clearInterval(this.pollingInterval);
                    this.pollingInterval = null;
                    return;
                }
            }
            
            if (pollCount >= maxPolls) {
                console.log('⏰ 达到最大检查次数，停止轮询');
                this.showPollingTimeout();
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;
            }
        }, 30000);
        */
    }

    async checkAnalysisResult(isAutoCheck = false) {
        if (!this.currentStockCode) {
            if (!isAutoCheck) {
                alert('没有正在进行的分析任务');
            }
            return false;
        }

        try {
            if (!isAutoCheck) {
                // 手动检查时显示加载状态
                const stockInfoDiv = document.getElementById('stock-info');
                const loadingHtml = stockInfoDiv.innerHTML.replace(
                    '🔄 检查分析结果',
                    '⏳ 检查中...'
                );
                stockInfoDiv.innerHTML = loadingHtml;
            }

            // 重新调用API检查结果
            const response = await fetch(`${this.apiBase}/api/vercel/stock-analysis?code=${this.currentStockCode}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // 检查是否有分析结果
            const hasAnalysis = data.analysis && (
                data.analysis.professional_analysis || 
                data.analysis.dark_analysis
            );

            if (hasAnalysis || data.status === 'completed') {
                // 有结果了，更新显示
                const processedData = this.processStockData(data);
                const stockInfoDiv = document.getElementById('stock-info');
                stockInfoDiv.innerHTML = this.stockTemplate(processedData);
                return true;
            } else {
                // 还没有结果
                if (!isAutoCheck) {
                    const stockInfoDiv = document.getElementById('stock-info');
                    const updatedHtml = stockInfoDiv.innerHTML.replace(
                        '⏳ 检查中...',
                        '🔄 检查分析结果'
                    );
                    stockInfoDiv.innerHTML = updatedHtml;
                    this.bindRefreshButton();
                }
                return false;
            }

        } catch (error) {
            console.error('检查分析结果失败:', error);
            if (!isAutoCheck) {
                alert(`检查结果失败: ${error.message}`);
            }
            return false;
        }
    }

    showPollingTimeout() {
        // 显示轮询超时信息
        const stockInfoDiv = document.getElementById('stock-info');
        if (stockInfoDiv) {
            const timeoutHtml = `
                <div class="stock-card">
                    <div class="text-center py-8">
                        <div class="text-6xl mb-4">⏰</div>
                        <h3 class="text-xl font-semibold text-orange-600 mb-4">分析时间较长</h3>
                        <p class="text-gray-600 mb-4">已等待约4分钟，n8n workflow可能需要更多时间完成</p>
                        <p class="text-sm text-gray-500 mb-6">任务ID: ${this.currentTaskId || 'N/A'}</p>
                        
                        <div class="space-y-3">
                            <button id="refresh-btn" class="btn-primary">
                                🔄 手动检查结果
                            </button>
                            <button id="new-analysis-btn" class="btn-secondary">
                                🆕 开始新的分析
                            </button>
                        </div>
                        
                        <div class="mt-4 text-xs text-gray-400">
                            💡 提示: 已停止自动检查以节省token
                        </div>
                    </div>
                </div>
            `;
            stockInfoDiv.innerHTML = timeoutHtml;
            this.bindRefreshButton();
            this.bindNewAnalysisButton();
        }
    }

    showPollingFailure(message) {
        // 显示轮询失败信息
        const stockInfoDiv = document.getElementById('stock-info');
        if (stockInfoDiv) {
            const failureHtml = `
                <div class="stock-card">
                    <div class="text-center py-8">
                        <div class="text-6xl mb-4">❌</div>
                        <h3 class="text-xl font-semibold text-red-600 mb-4">检查失败</h3>
                        <p class="text-gray-600 mb-4">${message}</p>
                        <p class="text-sm text-gray-500 mb-6">任务ID: ${this.currentTaskId || 'N/A'}</p>
                        
                        <div class="space-y-3">
                            <button id="refresh-btn" class="btn-primary">
                                🔄 重新检查
                            </button>
                            <button id="new-analysis-btn" class="btn-secondary">
                                🆕 开始新的分析
                            </button>
                        </div>
                        
                        <div class="mt-4 text-xs text-gray-400">
                            💡 已停止自动重试以节省token
                        </div>
                    </div>
                </div>
            `;
            stockInfoDiv.innerHTML = failureHtml;
            this.bindRefreshButton();
            this.bindNewAnalysisButton();
        }
    }

    bindCheckResultButton() {
        // 绑定检查结果按钮
        const checkResultBtn = document.getElementById('check-result-btn');
        if (checkResultBtn) {
            checkResultBtn.addEventListener('click', () => {
                this.checkAnalysisResult();
            });
        }
    }

    async checkAnalysisResult() {
        if (!this.currentStockCode) {
            alert('没有正在进行的分析任务');
            return;
        }

        // 显示检查中状态
        const checkBtn = document.getElementById('check-result-btn');
        if (checkBtn) {
            checkBtn.innerHTML = '⏳ 检查中...';
            checkBtn.disabled = true;
        }

        try {
            // 调用专门的结果检查API，不会触发新的workflow
            const response = await fetch(`${this.apiBase}/api/vercel/stock-analysis?code=${this.currentStockCode}&check_result=1`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // 处理结果
            const processedData = this.processStockData(data);
            
            // 检查是否有真正的分析结果
            if (processedData.analysis && 
                (processedData.analysis.professional_analysis || 
                 processedData.analysis.dark_analysis)) {
                // 有分析结果，显示文章
                const stockInfoDiv = document.getElementById('stock-info');
                stockInfoDiv.innerHTML = this.stockTemplate(processedData);
            } else {
                // 还没有结果，恢复按钮状态
                if (checkBtn) {
                    checkBtn.innerHTML = '🔍 检查分析结果';
                    checkBtn.disabled = false;
                }
                alert('分析还在进行中，请稍后再试');
            }

        } catch (error) {
            console.error('检查分析结果失败:', error);
            alert(`检查失败: ${error.message}`);
            
            // 恢复按钮状态
            if (checkBtn) {
                checkBtn.innerHTML = '🔍 检查分析结果';
                checkBtn.disabled = false;
            }
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new StockApp();
});