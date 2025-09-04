// Stock Services Frontend Application
class StockApp {
    constructor() {
        this.apiBase = window.location.origin;
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
                    <p class="text-sm text-gray-600 mt-1">调用专业分析流程，预计需要20-30秒</p>
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
            
            // 渲染股票信息
            stockInfoDiv.innerHTML = this.stockTemplate(processedData);
            stockInfoDiv.className = '';
            
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
        // 处理n8n返回的分析数据格式
        const processed = {
            stock_code: data.stock_code,
            data_source: data.data_source || 'unknown',
            timestamp: data.timestamp || new Date().toISOString(),
            status: data.status === 'success',
            analysis: data.analysis || null,
            error: data.error || null
        };
        
        return processed;
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
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new StockApp();
});