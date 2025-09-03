-- PostgreSQL数据库配置脚本
-- 用于设置stock_services项目的数据库环境

-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_services;
CREATE DATABASE IF NOT EXISTS newsanalysis;

-- 创建用户
CREATE USER IF NOT EXISTS n8nuser WITH PASSWORD 'n8n123456';
ALTER USER n8nuser WITH SUPERUSER;

-- 连接到stock_services数据库
\c stock_services;

-- 创建股票相关表
CREATE TABLE IF NOT EXISTS chinese_stocks (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(10,2),
    concepts TEXT[],
    industry VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS us_stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(10,2),
    sector VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chinese_futures (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    volume BIGINT,
    open_interest BIGINT,
    settlement_price DECIMAL(10,2),
    contract_month VARCHAR(10),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time DECIMAL(10,3),
    client_ip INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chinese_stocks_code ON chinese_stocks(code);
CREATE INDEX IF NOT EXISTS idx_chinese_stocks_industry ON chinese_stocks(industry);
CREATE INDEX IF NOT EXISTS idx_us_stocks_symbol ON us_stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_us_stocks_sector ON us_stocks(sector);
CREATE INDEX IF NOT EXISTS idx_chinese_futures_code ON chinese_futures(code);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);

-- 连接到newsanalysis数据库
\c newsanalysis;

-- 创建新闻分析相关表
CREATE TABLE IF NOT EXISTS processed_news (
    id SERIAL PRIMARY KEY,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    url TEXT,
    title TEXT NOT NULL,
    author VARCHAR(255),
    news_time TIMESTAMP WITH TIME ZONE,
    generation_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    domain VARCHAR(100),
    analysis_quality_score INTEGER DEFAULT 0,
    processing_metadata JSONB,
    full_analysis JSONB,
    github_url TEXT,
    github_commit_sha VARCHAR(40),
    publication_status VARCHAR(20) DEFAULT 'pending',
    publication_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_memory (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'human',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_processed_news_content_hash ON processed_news(content_hash);
CREATE INDEX IF NOT EXISTS idx_processed_news_domain ON processed_news(domain);
CREATE INDEX IF NOT EXISTS idx_processed_news_news_time ON processed_news(news_time);
CREATE INDEX IF NOT EXISTS idx_processed_news_publication_status ON processed_news(publication_status);
CREATE INDEX IF NOT EXISTS idx_processed_news_quality ON processed_news(analysis_quality_score);
CREATE INDEX IF NOT EXISTS idx_processed_news_title_gin ON processed_news USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_processed_news_url ON processed_news(url);
CREATE INDEX IF NOT EXISTS idx_chat_memory_session_id ON chat_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_memory_type ON chat_memory(type);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER IF NOT EXISTS update_processed_news_updated_at 
    BEFORE UPDATE ON processed_news 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 授权给n8nuser
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO n8nuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO n8nuser;