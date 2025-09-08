# -*- coding: utf-8 -*-
"""
akshare数据获取服务模块
akshare data fetching service module
"""
import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any, List
import time
from datetime import datetime
import logging
try:
    from config import Config
except ImportError:
    # 如果无法导入Config，使用默认配置
    class Config:
        AKSHARE_CACHE_ENABLED = True
        AKSHARE_CACHE_TTL = 300

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AkshareService:
    """akshare数据获取服务类 / akshare data fetching service class"""
    
    def __init__(self):
        self.timeout = Config.AKSHARE_TIMEOUT
        self.max_retries = Config.MAX_RETRY_ATTEMPTS
    
    def _retry_request(self, func, *args, **kwargs):
        """重试机制装饰器 / Retry mechanism decorator"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"尝试第{attempt + 1}次请求失败 / Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # 指数退避 / Exponential backoff
        return None
    
    def get_chinese_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取中国股票信息 / Get Chinese stock information"""
        try:
            # 直接获取股票实时行情和基本信息 / Directly get stock real-time quotes and basic info
            def get_bid_ask_data():
                return ak.stock_bid_ask_em(symbol=stock_code)
            
            def get_basic_info():
                return ak.stock_individual_info_em(symbol=stock_code)
                
            def get_basic_info_xq():
                return ak.stock_individual_basic_info_xq(symbol=stock_code)
            
            bid_ask_data = self._retry_request(get_bid_ask_data)
            basic_info = self._retry_request(get_basic_info)
            
            if bid_ask_data is None or bid_ask_data.empty:
                logger.warning(f"无法获取股票 {stock_code} 的实时行情数据 / Cannot get real-time data for stock {stock_code}")
                return None
            
            # 从bid_ask_data中提取价格信息 / Extract price info from bid_ask_data
            price_data = {}
            for _, row in bid_ask_data.iterrows():
                price_data[row['item']] = row['value']
            
            # 从basic_info中提取基本信息 / Extract basic info
            basic_data = {}
            if basic_info is not None and not basic_info.empty:
                for _, row in basic_info.iterrows():
                    basic_data[row['item']] = row['value']
            
            # 获取股票名称 / Get stock name
            stock_name = ''
            if basic_info is not None and not basic_info.empty:
                # First try to get from basic_info
                for _, row in basic_info.iterrows():
                    if row['item'] == '股票简称':
                        stock_name = str(row['value'])
                        break
            
            # If still no name, try spot data as fallback
            if not stock_name:
                try:
                    def get_spot_data():
                        return ak.stock_zh_a_spot_em()
                    spot_data = self._retry_request(get_spot_data)
                    if spot_data is not None and not spot_data.empty:
                        stock_info = spot_data[spot_data['代码'] == stock_code]
                        if not stock_info.empty:
                            stock_name = stock_info.iloc[0].get('名称', '')
                except:
                    pass
            
            result = {
                'stock_code': stock_code,
                'stock_name_cn': stock_name,
                'stock_name_en': self._get_english_name(stock_name),
                'current_price': float(price_data.get('最新', 0)),
                'price_change': float(price_data.get('涨跌', 0)),
                'price_change_pct': float(price_data.get('涨幅', 0)),
                'open_price': float(price_data.get('今开', 0)),
                'close_price': float(price_data.get('昨收', 0)),
                'high_price': float(price_data.get('最高', 0)),
                'low_price': float(price_data.get('最低', 0)),
                'volume': float(price_data.get('总手', 0)),
                'turnover': float(price_data.get('金额', 0)),
                'pe_ratio': None,  # PE ratio not available in basic bid_ask data
                'pb_ratio': None,  # PB ratio not available in basic bid_ask data
                'market_cap': float(basic_data.get('总市值', 0)) if basic_data.get('总市值') else None,
                'company_background': self._get_enhanced_company_background(stock_code, basic_info, stock_name),
                'last_updated': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取中国股票信息失败 / Failed to get Chinese stock info: {str(e)}")
            return None
    
    def get_us_stock_info(self, stock_symbol: str) -> Optional[Dict[str, Any]]:
        """获取美国股票信息 / Get US stock information"""
        try:
            # 获取美股实时数据 / Get US stock real-time data
            def get_us_realtime_data():
                return ak.stock_us_spot_em()
            
            stock_data = self._retry_request(get_us_realtime_data)
            
            if stock_data is None or stock_data.empty:
                return None
            
            # 查找指定股票 / Find specified stock
            stock_info = stock_data[stock_data['代码'] == stock_symbol]
            if stock_info.empty:
                return None
            
            stock_row = stock_info.iloc[0]
            
            # 获取个股详细信息 / Get individual stock details
            def get_us_individual_info():
                return ak.stock_us_fundamental(symbol=stock_symbol)
            
            fundamental_info = self._retry_request(get_us_individual_info)
            
            result = {
                'stock_symbol': stock_symbol,
                'stock_name_en': stock_row.get('名称', ''),
                'stock_name_cn': self._get_chinese_name(stock_row.get('名称', '')),
                'current_price': float(stock_row.get('最新价', 0)),
                'price_change': float(stock_row.get('涨跌额', 0)),
                'price_change_pct': float(stock_row.get('涨跌幅', 0)),
                'open_price': float(stock_row.get('开盘价', 0)),
                'close_price': float(stock_row.get('昨收价', 0)),
                'high_price': float(stock_row.get('最高价', 0)),
                'low_price': float(stock_row.get('最低价', 0)),
                'volume': float(stock_row.get('成交量', 0)),
                'turnover': float(stock_row.get('成交额', 0)),
                'market_cap': float(stock_row.get('市值', 0)) if stock_row.get('市值') else None,
                'pe_ratio': self._extract_pe_ratio(fundamental_info) if fundamental_info is not None else None,
                'pb_ratio': self._extract_pb_ratio(fundamental_info) if fundamental_info is not None else None,
                'sector': self._extract_sector(fundamental_info) if fundamental_info is not None else '',
                'exchange': self._get_exchange_from_symbol(stock_symbol),
                'company_background': self._get_us_company_background(stock_symbol),
                'last_updated': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取美国股票信息失败 / Failed to get US stock info: {str(e)}")
            return None
    
    def get_chinese_futures_info(self, futures_code: str) -> Optional[Dict[str, Any]]:
        """获取中国期货信息 / Get Chinese futures information"""
        try:
            # 获取期货实时数据 / Get futures real-time data
            def get_futures_data():
                return ak.futures_zh_spot()
            
            futures_data = self._retry_request(get_futures_data)
            
            if futures_data is None or futures_data.empty:
                return None
            
            # 查找指定期货 / Find specified futures
            futures_info = futures_data[futures_data['symbol'] == futures_code]
            if futures_info.empty:
                return None
            
            futures_row = futures_info.iloc[0]
            
            # 获取期货合约详细信息 / Get futures contract details
            def get_contract_info():
                return ak.futures_contract_detail(symbol=futures_code)
            
            contract_info = self._retry_request(get_contract_info)
            
            result = {
                'futures_code': futures_code,
                'futures_name': futures_row.get('name', ''),
                'current_price': float(futures_row.get('price', 0)),
                'price_change': float(futures_row.get('change', 0)),
                'price_change_pct': float(futures_row.get('change_pct', 0)),
                'open_price': float(futures_row.get('open', 0)),
                'close_price': float(futures_row.get('preclose', 0)),
                'high_price': float(futures_row.get('high', 0)),
                'low_price': float(futures_row.get('low', 0)),
                'volume': float(futures_row.get('volume', 0)),
                'open_interest': float(futures_row.get('hold', 0)),
                'settlement_price': float(futures_row.get('settle', 0)),
                'contract_month': self._extract_contract_month(futures_code),
                'exchange': self._get_futures_exchange(futures_code),
                'underlying_asset': self._get_underlying_asset(futures_code),
                'contract_size': self._get_contract_size(contract_info) if contract_info is not None else None,
                'tick_size': self._get_tick_size(contract_info) if contract_info is not None else None,
                'trading_unit': self._get_trading_unit(contract_info) if contract_info is not None else '',
                'delivery_month': self._get_delivery_month(contract_info) if contract_info is not None else '',
                'last_updated': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取中国期货信息失败 / Failed to get Chinese futures info: {str(e)}")
            return None
    
    def get_chinese_stock_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取中国股票列表 / Get Chinese stock list"""
        try:
            def get_stock_list():
                return ak.stock_zh_a_spot_em()
            
            stock_data = self._retry_request(get_stock_list)
            
            if stock_data is None or stock_data.empty:
                return []
            
            # 限制返回数量 / Limit return quantity
            stock_data = stock_data.head(limit)
            
            result = []
            for _, row in stock_data.iterrows():
                result.append({
                    'stock_code': row.get('代码', ''),
                    'stock_name_cn': row.get('名称', ''),
                    'current_price': float(row.get('最新价', 0)),
                    'price_change_pct': float(row.get('涨跌幅', 0))
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取中国股票列表失败 / Failed to get Chinese stock list: {str(e)}")
            return []
    
    def _get_english_name(self, chinese_name: str) -> str:
        """获取股票英文名称 / Get stock English name"""
        # 简单的中英文映射，实际应用中可以使用更复杂的翻译服务
        # Simple Chinese-English mapping, more complex translation service can be used in practice
        name_mappings = {
            '中国平安': 'Ping An Insurance',
            '招商银行': 'China Merchants Bank',
            '贵州茅台': 'Kweichow Moutai',
            '比亚迪': 'BYD Company',
            '腾讯控股': 'Tencent Holdings'
        }
        return name_mappings.get(chinese_name, chinese_name)
    
    def _get_chinese_name(self, english_name: str) -> str:
        """获取股票中文名称 / Get stock Chinese name"""
        name_mappings = {
            'Apple Inc.': '苹果公司',
            'Microsoft Corporation': '微软公司',
            'Amazon.com Inc.': '亚马逊',
            'Tesla, Inc.': '特斯拉',
            'Meta Platforms, Inc.': '脸书'
        }
        return name_mappings.get(english_name, '')
    
    def _get_company_background(self, company_info) -> str:
        """提取公司背景信息 / Extract company background information"""
        if company_info is None or company_info.empty:
            return ''
        try:
            # 从公司信息中提取背景描述
            if '公司简介' in company_info.columns:
                return str(company_info['公司简介'].iloc[0]) if not company_info['公司简介'].empty else ''
            return ''
        except:
            return ''
    
    def _get_company_background_simple(self, stock_name: str) -> str:
        """获取简单的公司背景信息 / Get simple company background information"""
        # 简单的公司背景映射，实际应用中可以使用更复杂的数据源
        backgrounds = {
            '华友钴业': '浙江华友钴业股份有限公司是一家主要从事钴、镍、铜有色金属采、选、冶及钴新材料产品的深加工与销售的公司。',
            '贵州茅台': '贵州茅台酒股份有限公司主要从事茅台酒及系列酒的生产和销售，是中国白酒行业的龙头企业。',
            '中国平安': '中国平安保险(集团)股份有限公司是中国第一家股份制保险企业，现已发展成为金融保险、银行、投资等金融业务为一体的整合、紧密、多元的综合金融服务集团。',
            '招商银行': '招商银行股份有限公司是中国第一家完全由企业法人持股的股份制商业银行。',
            '融发核电': '北京江融天下控股股份有限公司，原融发核电，是一家专业从事核电装备制造及核电技术服务的高科技企业。公司主营业务包括核电设备制造、核电技术服务等，属于新能源概念、核电概念股。公司总部位于北京，是核电装备制造领域的重要参与者。'
        }
        return backgrounds.get(stock_name, f'{stock_name}是一家在中国证券交易所上市的公司。')
    
    def _get_enhanced_company_background(self, stock_code: str, basic_info: pd.DataFrame, stock_name: str) -> str:
        """获取增强的公司背景信息 / Get enhanced company background information"""
        try:
            # Extract info from basic_info DataFrame
            company_info = {}
            if basic_info is not None and not basic_info.empty:
                for _, row in basic_info.iterrows():
                    company_info[row['item']] = row['value']
            
            # Build comprehensive background
            background_parts = []
            
            # Company full name and location (inferred from stock name and code)
            full_name = self._get_full_company_name(stock_code, stock_name)
            background_parts.append(full_name)
            
            # Industry information
            industry = company_info.get('行业', '')
            if industry:
                background_parts.append(f'公司主营业务属于{industry}行业')
            
            # Market cap and scale info
            market_cap = company_info.get('总市值', 0)
            if market_cap and market_cap > 0:
                market_cap_billion = float(market_cap) / 1000000000
                if market_cap_billion >= 100:
                    scale = '大型'
                elif market_cap_billion >= 10:
                    scale = '中型'
                else:
                    scale = '小型'
                background_parts.append(f'总市值约{market_cap_billion:.1f}亿元，属于{scale}企业')
            
            # Listing date
            listing_date = company_info.get('上市时间', '')
            if listing_date:
                listing_year = str(listing_date)[:4] if len(str(listing_date)) >= 4 else ''
                if listing_year:
                    background_parts.append(f'{listing_year}年上市')
            
            # Add concept tags based on industry and stock name
            concept_tags = self._get_concept_tags(stock_code, stock_name, industry)
            if concept_tags:
                background_parts.append(f'涉及概念：{"，".join(concept_tags)}')
            
            # Combine all parts
            if background_parts:
                return '。'.join(background_parts) + '。'
            else:
                return self._get_company_background_simple(stock_name)
                
        except Exception as e:
            logger.warning(f"获取增强背景信息失败 / Failed to get enhanced background: {e}")
            return self._get_company_background_simple(stock_name)
    
    def _get_full_company_name(self, stock_code: str, stock_name: str) -> str:
        """获取公司全名 / Get full company name"""
        # Map stock codes/names to full company names
        full_names = {
            '603799': '浙江华友钴业股份有限公司',
            '000858': '五粮液集团股份有限公司',
            '000001': '平安银行股份有限公司', 
            '600036': '招商银行股份有限公司',
            '002366': '北京江融天下控股股份有限公司',
            '华友钴业': '浙江华友钴业股份有限公司',
            '五粮液': '五粮液集团股份有限公司',
            '平安银行': '平安银行股份有限公司',
            '招商银行': '招商银行股份有限公司',
            '融发核电': '北京江融天下控股股份有限公司'
        }
        
        # Try stock code first, then stock name
        full_name = full_names.get(stock_code) or full_names.get(stock_name)
        if full_name:
            return full_name
        
        # Generate based on stock name if not found
        if stock_name:
            if '银行' in stock_name:
                return f'{stock_name}股份有限公司'
            elif '保险' in stock_name or '平安' in stock_name:
                return f'{stock_name}集团股份有限公司'
            else:
                return f'{stock_name}股份有限公司'
        
        return f'股票代码{stock_code}对应公司'
    
    def _get_concept_tags(self, stock_code: str, stock_name: str, industry: str) -> List[str]:
        """获取概念标签 / Get concept tags"""
        tags = []
        
        # Industry-based concepts
        industry_concepts = {
            '有色金属': ['有色金属', '稀有金属', '新材料'],
            '电源设备': ['新能源', '电力设备', '智能电网'],
            '核电': ['核电概念', '清洁能源', '新能源'],
            '银行': ['金融', '银行概念', 'A股核心资产'],
            '保险': ['金融', '保险概念', 'A股核心资产'],
            '白酒': ['白酒概念', '消费升级', 'A股核心资产'],
            '钢铁': ['钢铁概念', '周期股', '基建'],
            '房地产': ['房地产', '基建概念']
        }
        
        for ind, concepts in industry_concepts.items():
            if ind in industry:
                tags.extend(concepts)
                break
        
        # Stock name based concepts
        name_concepts = {
            '钴': ['钴概念', '稀有金属', '新能源汽车', '三元材料'],
            '锂': ['锂电池', '新能源汽车', '储能概念'],
            '核电': ['核电概念', '核能概念', '清洁能源'],
            '融发': ['重组概念'],
            '华友': ['钴概念', '镍概念', '印尼概念']
        }
        
        if stock_name:
            for keyword, concepts in name_concepts.items():
                if keyword in stock_name:
                    tags.extend(concepts)
        
        # Stock code based special concepts
        code_concepts = {
            '002366': ['重组概念', '核电概念', '国企改革'],
            '603799': ['钴概念', '印尼概念', '新能源汽车']
        }
        
        if stock_code in code_concepts:
            tags.extend(code_concepts[stock_code])
        
        # Remove duplicates and return
        return list(set(tags))
    
    def _get_us_company_background(self, symbol: str) -> str:
        """获取美股公司背景 / Get US stock company background"""
        # 简单的公司背景映射
        backgrounds = {
            'AAPL': 'Apple Inc. is an American multinational technology company headquartered in Cupertino, California.',
            'MSFT': 'Microsoft Corporation is an American multinational technology corporation.',
            'GOOGL': 'Alphabet Inc. is an American multinational conglomerate headquartered in Mountain View, California.',
            'TSLA': 'Tesla, Inc. is an American electric vehicle and clean energy company.',
            'AMZN': 'Amazon.com, Inc. is an American multinational technology company.'
        }
        return backgrounds.get(symbol, '')
    
    def _extract_pe_ratio(self, fundamental_info) -> Optional[float]:
        """提取市盈率 / Extract PE ratio"""
        try:
            if fundamental_info is not None and '市盈率' in fundamental_info.columns:
                return float(fundamental_info['市盈率'].iloc[0])
        except:
            pass
        return None
    
    def _extract_pb_ratio(self, fundamental_info) -> Optional[float]:
        """提取市净率 / Extract PB ratio"""
        try:
            if fundamental_info is not None and '市净率' in fundamental_info.columns:
                return float(fundamental_info['市净率'].iloc[0])
        except:
            pass
        return None
    
    def _extract_sector(self, fundamental_info) -> str:
        """提取行业信息 / Extract sector information"""
        try:
            if fundamental_info is not None and '行业' in fundamental_info.columns:
                return str(fundamental_info['行业'].iloc[0])
        except:
            pass
        return ''
    
    def _get_exchange_from_symbol(self, symbol: str) -> str:
        """根据股票代码获取交易所 / Get exchange from stock symbol"""
        if symbol.endswith('.N'):
            return 'NYSE'
        elif symbol.endswith('.O'):
            return 'NASDAQ'
        else:
            return 'NASDAQ'  # 默认NASDAQ / Default NASDAQ
    
    def _extract_contract_month(self, futures_code: str) -> str:
        """提取合约月份 / Extract contract month"""
        # 从期货代码中提取月份信息
        import re
        match = re.search(r'(\d{4})', futures_code)
        if match:
            year_month = match.group(1)
            year = year_month[:2]
            month = year_month[2:]
            return f"20{year}-{month}"
        return ''
    
    def _get_futures_exchange(self, futures_code: str) -> str:
        """获取期货交易所 / Get futures exchange"""
        # 根据期货代码前缀判断交易所
        if futures_code.startswith(('cu', 'al', 'zn', 'pb', 'ni', 'sn', 'au', 'ag')):
            return 'SHFE'  # 上海期货交易所
        elif futures_code.startswith(('c', 'm', 'y', 'a', 'b', 'p', 'fb', 'bb', 'jd', 'l', 'v', 'pp', 'j', 'jm', 'i', 'eg', 'eb', 'pg', 'lh', 'rr')):
            return 'DCE'   # 大连商品交易所
        elif futures_code.startswith(('zc', 'wh', 'pm', 'cf', 'sr', 'oi', 'ma', 'fg', 'rs', 'rm', 'jf', 'sm', 'sf', 'cy', 'ap', 'cj', 'ur', 'sa', 'pk')):
            return 'CZCE'  # 郑州商品交易所
        else:
            return 'CFFEX' # 中国金融期货交易所
    
    def _get_underlying_asset(self, futures_code: str) -> str:
        """获取期货标的资产 / Get futures underlying asset"""
        asset_mappings = {
            'cu': '铜',
            'al': '铝',
            'zn': '锌',
            'pb': '铅',
            'ni': '镍',
            'au': '黄金',
            'ag': '白银',
            'c': '玉米',
            'm': '豆粕',
            'y': '豆油',
            'a': '豆一',
            'b': '豆二',
            'j': '焦炭',
            'jm': '焦煤',
            'i': '铁矿石',
            'zc': '动力煤',
            'wh': '强麦',
            'cf': '棉花',
            'sr': '白糖'
        }
        for prefix, asset in asset_mappings.items():
            if futures_code.startswith(prefix):
                return asset
        return ''
    
    def _get_contract_size(self, contract_info) -> Optional[float]:
        """获取合约规模 / Get contract size"""
        try:
            if contract_info is not None and '合约乘数' in contract_info.columns:
                return float(contract_info['合约乘数'].iloc[0])
        except:
            pass
        return None
    
    def _get_tick_size(self, contract_info) -> Optional[float]:
        """获取最小变动价位 / Get tick size"""
        try:
            if contract_info is not None and '最小变动价位' in contract_info.columns:
                return float(contract_info['最小变动价位'].iloc[0])
        except:
            pass
        return None
    
    def _get_trading_unit(self, contract_info) -> str:
        """获取交易单位 / Get trading unit"""
        try:
            if contract_info is not None and '交易单位' in contract_info.columns:
                return str(contract_info['交易单位'].iloc[0])
        except:
            pass
        return ''
    
    def _get_delivery_month(self, contract_info) -> str:
        """获取交割月份 / Get delivery month"""
        try:
            if contract_info is not None and '交割月份' in contract_info.columns:
                return str(contract_info['交割月份'].iloc[0])
        except:
            pass
        return ''
    
    def get_financial_abstract(self, stock_code: str) -> Optional[pd.DataFrame]:
        """获取股票财务摘要数据 / Get stock financial abstract data"""
        try:
            def get_financial_data():
                return ak.stock_financial_abstract(symbol=stock_code)
            
            financial_data = self._retry_request(get_financial_data)
            
            if financial_data is None or financial_data.empty:
                logger.warning(f"无法获取股票 {stock_code} 的财务摘要数据")
                return None
            
            logger.info(f"成功获取股票 {stock_code} 财务数据，共 {len(financial_data)} 行")
            return financial_data
            
        except Exception as e:
            logger.error(f"获取财务摘要数据失败: {str(e)}")
            return None
    
    def get_comprehensive_financial_indicators(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取全面的财务指标数据 / Get comprehensive financial indicators data"""
        try:
            result = {
                'stock_code': stock_code,
                'update_time': datetime.utcnow().isoformat(),
                'financial_statements': {},
                'financial_ratios': {},
                'profitability_indicators': {},
                'efficiency_indicators': {},
                'liquidity_indicators': {},
                'leverage_indicators': {},
                'growth_indicators': {}
            }
            
            # 1. 财务摘要数据（主要财务指标）
            financial_abstract = self.get_financial_abstract(stock_code)
            if financial_abstract is not None:
                result['financial_statements']['abstract'] = self._extract_financial_abstract_indicators(financial_abstract)
            
            # 2. 获取利润表数据
            try:
                def get_income_statement():
                    return ak.stock_financial_analysis_indicator(symbol=stock_code)
                
                income_data = self._retry_request(get_income_statement)
                if income_data is not None and not income_data.empty:
                    result['financial_statements']['income_statement'] = self._extract_income_statement_indicators(income_data)
                    logger.info(f"获取到 {stock_code} 利润表数据")
            except Exception as e:
                logger.warning(f"获取利润表数据失败: {str(e)}")
            
            # 3. 获取资产负债表数据
            try:
                def get_balance_sheet():
                    return ak.stock_balance_sheet_by_report_em(symbol=stock_code)
                
                balance_data = self._retry_request(get_balance_sheet)
                if balance_data is not None and not balance_data.empty:
                    result['financial_statements']['balance_sheet'] = self._extract_balance_sheet_indicators(balance_data)
                    logger.info(f"获取到 {stock_code} 资产负债表数据")
            except Exception as e:
                logger.warning(f"获取资产负债表数据失败: {str(e)}")
            
            # 4. 获取现金流量表数据
            try:
                def get_cash_flow():
                    return ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
                
                cash_flow_data = self._retry_request(get_cash_flow)
                if cash_flow_data is not None and not cash_flow_data.empty:
                    result['financial_statements']['cash_flow'] = self._extract_cash_flow_indicators(cash_flow_data)
                    logger.info(f"获取到 {stock_code} 现金流量表数据")
            except Exception as e:
                logger.warning(f"获取现金流量表数据失败: {str(e)}")
            
            # 5. 获取财务比率数据
            try:
                def get_financial_ratios():
                    return ak.stock_financial_hk_report_em(symbol=stock_code)
                
                ratio_data = self._retry_request(get_financial_ratios)
                if ratio_data is not None and not ratio_data.empty:
                    result['financial_ratios'] = self._extract_financial_ratios(ratio_data)
                    logger.info(f"获取到 {stock_code} 财务比率数据")
            except Exception as e:
                logger.warning(f"获取财务比率数据失败: {str(e)}")
            
            # 6. 计算综合财务指标
            if result['financial_statements'].get('abstract'):
                profitability = self._calculate_profitability_indicators(result['financial_statements']['abstract'])
                efficiency = self._calculate_efficiency_indicators(result['financial_statements']['abstract'])
                liquidity = self._calculate_liquidity_indicators(result['financial_statements']['abstract'])
                leverage = self._calculate_leverage_indicators(result['financial_statements']['abstract'])
                growth = self._calculate_growth_indicators(result['financial_statements']['abstract'])
                
                result['profitability_indicators'] = profitability
                result['efficiency_indicators'] = efficiency
                result['liquidity_indicators'] = liquidity
                result['leverage_indicators'] = leverage
                result['growth_indicators'] = growth
            
            # 7. 数据完整性检查
            data_sections = ['financial_statements', 'financial_ratios', 'profitability_indicators', 
                           'efficiency_indicators', 'liquidity_indicators', 'leverage_indicators', 'growth_indicators']
            available_sections = [section for section in data_sections if result.get(section)]
            
            result['data_quality'] = {
                'completeness_score': len(available_sections) * 100 // len(data_sections),
                'available_sections': available_sections,
                'total_sections': len(data_sections),
                'data_freshness': datetime.utcnow().isoformat()
            }
            
            logger.info(f"综合财务指标获取完成，completeness: {result['data_quality']['completeness_score']}%")
            return result
            
        except Exception as e:
            logger.error(f"获取综合财务指标失败: {str(e)}")
            return None
    
    def get_comprehensive_financial_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票综合财务数据 / Get comprehensive financial data"""
        try:
            # 获取财务摘要数据
            financial_abstract = self.get_financial_abstract(stock_code)
            if financial_abstract is None or financial_abstract.empty:
                return None
            
            # 处理财务摘要数据，提取关键指标
            financial_metrics = self._process_financial_abstract(financial_abstract)
            
            # 获取历史数据用于技术指标计算
            historical_data = self._get_historical_data(stock_code)
            technical_metrics = self._calculate_technical_indicators(historical_data) if historical_data is not None else {}
            
            # 获取股票基本信息
            basic_info = self.get_stock_basic_info(stock_code)
            
            # 综合结果
            comprehensive_data = {
                'stock_code': stock_code,
                'update_time': datetime.utcnow().isoformat(),
                'financial_metrics': financial_metrics,
                'technical_metrics': technical_metrics,
                'basic_info': basic_info,
                'data_completeness': {
                    'has_financial_data': len(financial_metrics) > 0,
                    'has_technical_data': len(technical_metrics) > 0,
                    'has_basic_info': basic_info is not None
                }
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"获取综合财务数据失败: {str(e)}")
            return None
    
    def _process_financial_abstract(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """处理财务摘要数据 / Process financial abstract data"""
        try:
            result = {}
            
            # 获取最近4个季度的数据
            date_columns = [col for col in financial_data.columns if col.isdigit() and len(col) == 8]
            date_columns = sorted(date_columns, reverse=True)[:4]  # 最近4个季度
            
            # 定义关键指标映射
            key_metrics = {
                '归母净利润': 'net_profit_parent',
                '营业总收入': 'total_revenue', 
                '营业成本': 'operating_cost',
                '净利润': 'net_profit',
                '扣非净利润': 'net_profit_deducted',
                '股东权益合计(净资产)': 'total_equity',
                '经营现金流量净额': 'operating_cash_flow',
                '基本每股收益': 'eps',
                '每股净资产': 'book_value_per_share',
                '每股现金流': 'cash_flow_per_share',
                '净资产收益率(ROE)': 'roe',
                '总资产报酬率(ROA)': 'roa',
                '毛利率': 'gross_margin',
                '销售净利率': 'net_margin',
                '资产负债率': 'debt_ratio'
            }
            
            # 提取各个时期的数据
            for period in date_columns:
                period_data = {}
                for _, row in financial_data.iterrows():
                    metric_name = row['指标']
                    if metric_name in key_metrics:
                        try:
                            value = row[period]
                            if pd.notna(value) and value != '':
                                period_data[key_metrics[metric_name]] = float(value)
                        except (ValueError, TypeError):
                            continue
                
                if period_data:
                    # 格式化日期
                    formatted_date = f"{period[:4]}-{period[4:6]}-{period[6:]}"
                    result[formatted_date] = period_data
            
            # 计算同比增长率
            if len(result) >= 2:
                periods = sorted(result.keys(), reverse=True)
                current_period = result[periods[0]]
                previous_period = result[periods[1]] if len(periods) > 1 else {}
                
                growth_rates = {}
                for metric in current_period:
                    if metric in previous_period:
                        current_val = current_period[metric]
                        previous_val = previous_period[metric]
                        if previous_val != 0:
                            growth_rate = ((current_val - previous_val) / abs(previous_val)) * 100
                            growth_rates[f"{metric}_growth_rate"] = round(growth_rate, 2)
                
                result['growth_analysis'] = growth_rates
            
            return result
            
        except Exception as e:
            logger.error(f"处理财务摘要数据失败: {str(e)}")
            return {}
    
    def _get_historical_data(self, stock_code: str, period: str = "daily", days: int = 60) -> Optional[pd.DataFrame]:
        """获取历史数据 / Get historical data"""
        try:
            def get_hist_data():
                return ak.stock_zh_a_hist(symbol=stock_code, period=period, adjust='')
            
            hist_data = self._retry_request(get_hist_data)
            
            if hist_data is None or hist_data.empty:
                return None
            
            # 获取最近N天数据
            return hist_data.tail(days)
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {str(e)}")
            return None
    
    def _calculate_technical_indicators(self, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """计算技术指标 / Calculate technical indicators"""
        try:
            if hist_data is None or hist_data.empty or len(hist_data) < 20:
                return {}
            
            result = {}
            
            # 价格相关指标
            close_prices = hist_data['收盘'].astype(float)
            high_prices = hist_data['最高'].astype(float)
            low_prices = hist_data['最低'].astype(float)
            open_prices = hist_data['开盘'].astype(float)
            volumes = hist_data['成交量'].astype(float)
            
            # 当前价格
            current_price = close_prices.iloc[-1]
            result['current_price'] = current_price
            
            # 移动平均线
            if len(close_prices) >= 5:
                result['ma5'] = round(close_prices.tail(5).mean(), 2)
            if len(close_prices) >= 10:
                result['ma10'] = round(close_prices.tail(10).mean(), 2)
            if len(close_prices) >= 20:
                result['ma20'] = round(close_prices.tail(20).mean(), 2)
            if len(close_prices) >= 60:
                result['ma60'] = round(close_prices.tail(60).mean(), 2)
            
            # 价格变化
            if len(close_prices) >= 2:
                yesterday_price = close_prices.iloc[-2]
                result['price_change'] = round(current_price - yesterday_price, 2)
                result['price_change_pct'] = round(((current_price - yesterday_price) / yesterday_price) * 100, 2)
            
            # 近期高低点
            if len(close_prices) >= 20:
                result['high_20d'] = close_prices.tail(20).max()
                result['low_20d'] = close_prices.tail(20).min()
            
            # 波动率 (20日标准差)
            if len(close_prices) >= 20:
                returns = close_prices.pct_change().tail(20)
                result['volatility_20d'] = round(returns.std() * 100, 2)
            
            # 成交量相关
            if len(volumes) >= 5:
                result['avg_volume_5d'] = int(volumes.tail(5).mean())
            if len(volumes) >= 20:
                result['avg_volume_20d'] = int(volumes.tail(20).mean())
                
            current_volume = volumes.iloc[-1]
            result['volume_ratio'] = round(current_volume / result.get('avg_volume_20d', current_volume) if result.get('avg_volume_20d', 0) > 0 else 1, 2)
            
            # 高级技术指标
            advanced_indicators = self._calculate_advanced_indicators(close_prices, high_prices, low_prices, open_prices, volumes)
            result.update(advanced_indicators)
            
            return result
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {str(e)}")
            return {}
    
    def _calculate_advanced_indicators(self, closes: pd.Series, highs: pd.Series, lows: pd.Series, 
                                     opens: pd.Series, volumes: pd.Series) -> Dict[str, Any]:
        """计算高级技术指标 / Calculate advanced technical indicators"""
        try:
            import numpy as np
            result = {}
            
            # RSI计算
            def calculate_rsi(prices, periods=14):
                deltas = np.diff(prices)
                gains = np.where(deltas > 0, deltas, 0)
                losses = np.where(deltas < 0, -deltas, 0)
                avg_gains = pd.Series(gains).rolling(periods, min_periods=periods).mean()
                avg_losses = pd.Series(losses).rolling(periods, min_periods=periods).mean()
                rs = avg_gains / avg_losses
                rsi = 100 - (100 / (1 + rs))
                return rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else None
            
            # 布林带计算
            def calculate_bollinger_bands(prices, periods=20, std_dev=2):
                sma = prices.rolling(periods, min_periods=periods).mean()
                std = prices.rolling(periods, min_periods=periods).std()
                upper_band = sma + (std * std_dev)
                lower_band = sma - (std * std_dev)
                return {
                    'upper': round(upper_band.iloc[-1], 2) if not pd.isna(upper_band.iloc[-1]) else None,
                    'middle': round(sma.iloc[-1], 2) if not pd.isna(sma.iloc[-1]) else None,
                    'lower': round(lower_band.iloc[-1], 2) if not pd.isna(lower_band.iloc[-1]) else None
                }
            
            # KDJ计算
            def calculate_kdj(highs, lows, closes, periods=9):
                lowest_lows = lows.rolling(periods, min_periods=periods).min()
                highest_highs = highs.rolling(periods, min_periods=periods).max()
                rsv = (closes - lowest_lows) / (highest_highs - lowest_lows) * 100
                k = rsv.ewm(alpha=1/3, adjust=False).mean()
                d = k.ewm(alpha=1/3, adjust=False).mean()
                j = 3 * k - 2 * d
                return {
                    'K': round(k.iloc[-1], 2) if not pd.isna(k.iloc[-1]) else None,
                    'D': round(d.iloc[-1], 2) if not pd.isna(d.iloc[-1]) else None,
                    'J': round(j.iloc[-1], 2) if not pd.isna(j.iloc[-1]) else None
                }
            
            # MACD计算
            def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
                exp1 = prices.ewm(span=fast_period, adjust=False).mean()
                exp2 = prices.ewm(span=slow_period, adjust=False).mean()
                macd_line = exp1 - exp2
                signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
                histogram = macd_line - signal_line
                return {
                    'macd': round(macd_line.iloc[-1], 4) if not pd.isna(macd_line.iloc[-1]) else None,
                    'signal': round(signal_line.iloc[-1], 4) if not pd.isna(signal_line.iloc[-1]) else None,
                    'histogram': round(histogram.iloc[-1], 4) if not pd.isna(histogram.iloc[-1]) else None
                }
            
            # ATR计算
            def calculate_atr(highs, lows, closes, periods=14):
                tr1 = highs - lows
                tr2 = abs(highs - closes.shift(1))
                tr3 = abs(lows - closes.shift(1))
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = tr.rolling(periods, min_periods=periods).mean()
                return round(atr.iloc[-1], 2) if not pd.isna(atr.iloc[-1]) else None
            
            # 威廉指标计算
            def calculate_williams_r(highs, lows, closes, periods=14):
                highest_high = highs.rolling(periods, min_periods=periods).max()
                lowest_low = lows.rolling(periods, min_periods=periods).min()
                wr = ((highest_high - closes) / (highest_high - lowest_low)) * -100
                return round(wr.iloc[-1], 2) if not pd.isna(wr.iloc[-1]) else None
            
            # CCI计算
            def calculate_cci(highs, lows, closes, periods=20):
                typical_price = (highs + lows + closes) / 3
                sma_tp = typical_price.rolling(periods, min_periods=periods).mean()
                mad = typical_price.rolling(periods, min_periods=periods).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
                cci = (typical_price - sma_tp) / (0.015 * mad)
                return round(cci.iloc[-1], 2) if not pd.isna(cci.iloc[-1]) else None
            
            # 计算各项指标
            if len(closes) >= 14:
                # RSI
                rsi_14 = calculate_rsi(closes, 14)
                if rsi_14 is not None:
                    result['rsi_14'] = round(rsi_14, 2)
                
                # ATR
                atr_14 = calculate_atr(highs, lows, closes, 14)
                if atr_14 is not None:
                    result['atr_14'] = atr_14
                
                # 威廉指标
                wr_14 = calculate_williams_r(highs, lows, closes, 14)
                if wr_14 is not None:
                    result['williams_r'] = wr_14
            
            if len(closes) >= 20:
                # 布林带
                bollinger = calculate_bollinger_bands(closes)
                result['bollinger_bands'] = bollinger
                
                # CCI
                cci_20 = calculate_cci(highs, lows, closes, 20)
                if cci_20 is not None:
                    result['cci_20'] = cci_20
            
            if len(closes) >= 9:
                # KDJ
                kdj = calculate_kdj(highs, lows, closes)
                result['kdj'] = kdj
            
            if len(closes) >= 26:
                # MACD
                macd = calculate_macd(closes)
                result['macd'] = macd
            
            # 支撑阻力位分析
            if len(closes) >= 20:
                recent_closes = closes.tail(20)
                result['support_resistance'] = {
                    'support': round(recent_closes.min(), 2),
                    'resistance': round(recent_closes.max(), 2),
                    'pivot_point': round((highs.tail(20).max() + lows.tail(20).min() + closes.iloc[-1]) / 3, 2)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"计算高级技术指标失败: {str(e)}")
            return {}
    
    def get_industry_analysis(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取行业分析数据 / Get industry analysis data"""
        try:
            # 获取股票基本信息中的行业
            basic_info = self.get_stock_basic_info(stock_code)
            if not basic_info or '行业' not in basic_info:
                return None
            
            industry = basic_info['行业']
            
            # 获取同行业股票列表进行比较
            def get_industry_stocks():
                return ak.stock_zh_a_spot_em()
            
            all_stocks = self._retry_request(get_industry_stocks)
            if all_stocks is None or all_stocks.empty:
                return None
            
            # 这里简化处理，实际应用中需要更复杂的行业分类
            industry_analysis = {
                'industry': industry,
                'stock_code': stock_code,
                'analysis_date': datetime.utcnow().isoformat(),
                'industry_overview': f'{industry}行业分析',
                'market_position': '行业地位分析需要更多数据源',
                'peer_comparison': '同业比较分析'
            }
            
            return industry_analysis
            
        except Exception as e:
            logger.error(f"获取行业分析数据失败: {str(e)}")
            return None
    
    def get_fund_flow_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取资金流向数据 / Get fund flow data"""
        try:
            # 根据股票代码判断市场
            market = 'sz' if stock_code.startswith(('000', '002', '300')) else 'sh'
            
            def get_fund_flow():
                return ak.stock_individual_fund_flow(stock=stock_code, market=market)
            
            fund_flow_data = self._retry_request(get_fund_flow)
            
            if fund_flow_data is None or fund_flow_data.empty:
                logger.warning(f"无法获取股票 {stock_code} 的资金流向数据")
                return None
            
            # 处理最近的资金流向数据
            recent_data = fund_flow_data.tail(30)  # 最近30天
            
            # 计算汇总统计
            total_main_inflow = recent_data['主力净流入-净额'].sum()
            avg_main_inflow_pct = recent_data['主力净流入-净占比'].mean()
            
            result = {
                'stock_code': stock_code,
                'data_source': 'akshare_fund_flow',
                'update_time': datetime.utcnow().isoformat(),
                'recent_30_days': recent_data.to_dict('records'),
                'summary': {
                    'total_main_inflow_30d': round(total_main_inflow, 2),
                    'avg_main_inflow_pct_30d': round(avg_main_inflow_pct, 2),
                    'net_inflow_days': len(recent_data[recent_data['主力净流入-净额'] > 0]),
                    'net_outflow_days': len(recent_data[recent_data['主力净流入-净额'] < 0])
                },
                'latest_data': recent_data.iloc[-1].to_dict() if len(recent_data) > 0 else {}
            }
            
            logger.info(f"成功获取股票 {stock_code} 资金流向数据，共 {len(recent_data)} 天")
            return result
            
        except Exception as e:
            logger.error(f"获取资金流向数据失败: {str(e)}")
            return None
    
    def get_dragon_tiger_data(self, stock_code: str, days: int = 90) -> Optional[Dict[str, Any]]:
        """获取龙虎榜数据 / Get dragon tiger list data"""
        try:
            # 计算查询日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            def get_lhb_data():
                return ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
            
            lhb_data = self._retry_request(get_lhb_data)
            
            if lhb_data is None or lhb_data.empty:
                logger.warning(f"无法获取龙虎榜数据")
                return None
            
            # 筛选特定股票的龙虎榜记录
            stock_lhb = lhb_data[lhb_data['代码'] == stock_code]
            
            if stock_lhb.empty:
                # 返回空结果但不是None
                result = {
                    'stock_code': stock_code,
                    'data_source': 'akshare_dragon_tiger',
                    'update_time': datetime.utcnow().isoformat(),
                    'query_period_days': days,
                    'total_records': 0,
                    'dragon_tiger_records': [],
                    'summary': {
                        'total_appearances': 0,
                        'total_net_buy': 0,
                        'reasons': []
                    }
                }
                return result
            
            # 处理数据
            stock_lhb = stock_lhb.fillna('')
            records = stock_lhb.to_dict('records')
            
            # 计算汇总数据
            total_net_buy = stock_lhb['龙虎榜净买额'].sum()
            reasons = stock_lhb['上榜原因'].unique().tolist()
            reasons = [r for r in reasons if r != '']
            
            result = {
                'stock_code': stock_code,
                'data_source': 'akshare_dragon_tiger',
                'update_time': datetime.utcnow().isoformat(),
                'query_period_days': days,
                'total_records': len(records),
                'dragon_tiger_records': records,
                'summary': {
                    'total_appearances': len(records),
                    'total_net_buy': round(total_net_buy, 2),
                    'reasons': reasons
                }
            }
            
            logger.info(f"成功获取股票 {stock_code} 龙虎榜数据，共 {len(records)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"获取龙虎榜数据失败: {str(e)}")
            return None

    def get_news_and_research_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取新闻和研报数据 / Get news and research data"""
        try:
            result = {
                'stock_code': stock_code,
                'data_source': 'akshare_news_research',
                'update_time': datetime.utcnow().isoformat(),
                'news': [],
                'research_reports': []
            }
            
            # 获取新闻数据
            try:
                def get_news():
                    return ak.stock_news_em(symbol=stock_code)
                
                news_data = self._retry_request(get_news)
                if news_data is not None and not news_data.empty:
                    # 取最新20条新闻
                    recent_news = news_data.head(20)
                    # 处理NaN值
                    recent_news = recent_news.fillna('')
                    result['news'] = recent_news.to_dict('records')
                    logger.info(f"获取到 {len(recent_news)} 条新闻")
                
            except Exception as e:
                logger.warning(f"获取新闻数据失败: {str(e)}")
            
            # 获取研报数据
            try:
                def get_research():
                    return ak.stock_research_report_em(symbol=stock_code)
                
                research_data = self._retry_request(get_research)
                if research_data is not None and not research_data.empty:
                    # 取最新10份研报
                    recent_research = research_data.head(10)
                    # 处理NaN值
                    recent_research = recent_research.fillna('')
                    result['research_reports'] = recent_research.to_dict('records')
                    logger.info(f"获取到 {len(recent_research)} 份研报")
                
            except Exception as e:
                logger.warning(f"获取研报数据失败: {str(e)}")
            
            return result if result['news'] or result['research_reports'] else None
            
        except Exception as e:
            logger.error(f"获取新闻和研报数据失败: {str(e)}")
            return None
    
    def get_minute_data(self, stock_code: str, period: str = '5') -> Optional[Dict[str, Any]]:
        """获取分钟级数据 / Get minute-level data"""
        try:
            def get_minute_data():
                return ak.stock_zh_a_hist_min_em(symbol=stock_code, period=period)
            
            minute_data = self._retry_request(get_minute_data)
            
            if minute_data is None or minute_data.empty:
                logger.warning(f"无法获取股票 {stock_code} 的分钟数据")
                return None
            
            # 今日分钟数据统计
            today_stats = {
                'today_high': round(minute_data['最高'].max(), 2),
                'today_low': round(minute_data['最低'].min(), 2),
                'total_volume': int(minute_data['成交量'].sum()),
                'total_amount': round(minute_data['成交额'].sum(), 2),
                'data_points': len(minute_data)
            }
            
            # 最新数据
            latest_data = minute_data.tail(10).to_dict('records')
            
            result = {
                'stock_code': stock_code,
                'data_source': 'akshare_minute_data',
                'period': f'{period}分钟',
                'update_time': datetime.utcnow().isoformat(),
                'today_statistics': today_stats,
                'latest_10_records': latest_data,
                'trading_pattern_analysis': self._analyze_trading_pattern(minute_data)
            }
            
            logger.info(f"成功获取股票 {stock_code} 分钟数据，共 {len(minute_data)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"获取分钟数据失败: {str(e)}")
            return None
    
    def _analyze_trading_pattern(self, minute_data: pd.DataFrame) -> Dict[str, Any]:
        """分析交易模式 / Analyze trading pattern"""
        try:
            # 时间段成交量分析
            minute_data['时间'] = pd.to_datetime(minute_data['时间'])
            minute_data['小时'] = minute_data['时间'].dt.hour
            
            # 各时间段成交量统计
            hourly_volume = minute_data.groupby('小时')['成交量'].sum()
            
            # 找出成交最活跃的时间段
            peak_hour = hourly_volume.idxmax()
            peak_volume = hourly_volume.max()
            
            # 价格振幅分析
            price_range = minute_data['最高'].max() - minute_data['最低'].min()
            avg_price = (minute_data['最高'] + minute_data['最低']).mean() / 2
            amplitude_pct = (price_range / avg_price) * 100
            
            return {
                'peak_trading_hour': f'{peak_hour}:00-{peak_hour+1}:00',
                'peak_hour_volume': int(peak_volume),
                'price_amplitude': round(price_range, 2),
                'amplitude_percentage': round(amplitude_pct, 2),
                'trading_activity': 'active' if amplitude_pct > 2 else 'normal' if amplitude_pct > 1 else 'quiet'
            }
            
        except Exception as e:
            logger.warning(f"分析交易模式失败: {str(e)}")
            return {}
    
    def get_comprehensive_market_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取综合市场数据 / Get comprehensive market data"""
        try:
            result = {
                'stock_code': stock_code,
                'data_source': 'akshare_comprehensive',
                'update_time': datetime.utcnow().isoformat(),
                'data_sections': {}
            }
            
            # 1. 资金流向数据
            fund_flow = self.get_fund_flow_data(stock_code)
            if fund_flow:
                result['data_sections']['fund_flow'] = fund_flow
            
            # 2. 新闻研报数据
            news_research = self.get_news_and_research_data(stock_code)
            if news_research:
                result['data_sections']['news_research'] = news_research
            
            # 3. 分钟数据摘要
            minute_summary = self.get_minute_data(stock_code)
            if minute_summary:
                # 只保留统计信息，不保留详细数据
                result['data_sections']['intraday_summary'] = {
                    'today_statistics': minute_summary.get('today_statistics', {}),
                    'trading_pattern': minute_summary.get('trading_pattern_analysis', {})
                }
            
            # 4. 综合数据完整性评分
            data_completeness_score = 0
            if 'fund_flow' in result['data_sections']:
                data_completeness_score += 30
            if 'news_research' in result['data_sections']:
                data_completeness_score += 40
            if 'intraday_summary' in result['data_sections']:
                data_completeness_score += 30
            
            result['data_quality'] = {
                'completeness_score': data_completeness_score,
                'available_sections': list(result['data_sections'].keys()),
                'total_sections': 3
            }
            
            logger.info(f"综合市场数据获取完成，completeness: {data_completeness_score}%")
            return result
            
        except Exception as e:
            logger.error(f"获取综合市场数据失败: {str(e)}")
            return None
    
    def get_stock_basic_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息 / Get stock basic information"""
        try:
            def get_basic_info():
                return ak.stock_individual_info_em(symbol=stock_code)
            
            basic_info = self._retry_request(get_basic_info)
            
            if basic_info is None or basic_info.empty:
                logger.warning(f"无法获取股票 {stock_code} 的基本信息")
                return None
            
            # 转换为字典格式
            result = {}
            for _, row in basic_info.iterrows():
                result[row['item']] = row['value']
            
            logger.info(f"成功获取股票 {stock_code} 基本信息")
            return result
            
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {str(e)}")
            return None
    
    # ========== 财务指标提取辅助方法 / Financial Indicators Helper Methods ==========
    
    def _extract_financial_abstract_indicators(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """从财务摘要中提取关键指标 / Extract key indicators from financial abstract"""
        try:
            result = {}
            
            # 获取最近4个季度的数据列
            date_columns = [col for col in financial_data.columns if col.isdigit() and len(col) == 8]
            date_columns = sorted(date_columns, reverse=True)[:4]  # 最近4个季度
            
            # 定义要提取的财务指标
            key_indicators = {
                '归母净利润': 'net_profit_parent',
                '营业总收入': 'total_revenue', 
                '营业成本': 'operating_cost',
                '净利润': 'net_profit',
                '扣非净利润': 'net_profit_deducted',
                '股东权益合计(净资产)': 'total_equity',
                '总资产': 'total_assets',
                '经营现金流量净额': 'operating_cash_flow',
                '基本每股收益': 'eps',
                '每股净资产': 'book_value_per_share',
                '每股现金流': 'cash_flow_per_share',
                '净资产收益率(ROE)': 'roe',
                '总资产报酬率(ROA)': 'roa',
                '毛利率': 'gross_margin',
                '销售净利率': 'net_margin',
                '资产负债率': 'debt_ratio',
                '流动比率': 'current_ratio',
                '速动比率': 'quick_ratio',
                '存货周转率': 'inventory_turnover',
                '应收账款周转率': 'receivables_turnover',
                '总资产周转率': 'total_asset_turnover',
                '市盈率': 'pe_ratio',
                '市净率': 'pb_ratio',
                '营业利润': 'operating_profit',
                '利润总额': 'total_profit',
                '所得税费用': 'income_tax',
                '销售费用': 'selling_expenses',
                '管理费用': 'administrative_expenses',
                '财务费用': 'financial_expenses',
                '研发费用': 'rd_expenses',
                '流动资产': 'current_assets',
                '非流动资产': 'non_current_assets',
                '流动负债': 'current_liabilities',
                '非流动负债': 'non_current_liabilities',
                '负债合计': 'total_liabilities',
                '投资收益': 'investment_income',
                '公允价值变动收益': 'fair_value_change_income',
                '资产减值损失': 'asset_impairment_loss',
                '信用减值损失': 'credit_impairment_loss'
            }
            
            # 提取各个时期的数据
            for i, period in enumerate(date_columns):
                period_data = {}
                for _, row in financial_data.iterrows():
                    metric_name = row['指标']
                    if metric_name in key_indicators:
                        try:
                            value = row[period]
                            if pd.notna(value) and value != '' and value != 0:
                                # 转换为float，处理可能的字符串数值
                                period_data[key_indicators[metric_name]] = float(value)
                        except (ValueError, TypeError):
                            continue
                
                if period_data:
                    # 格式化日期
                    formatted_date = f"{period[:4]}-{period[4:6]}-{period[6:]}"
                    quarter_name = f"Q{i+1}_{period[:4]}"  # Q1_2025, Q2_2024等
                    result[quarter_name] = {
                        'date': formatted_date,
                        'metrics': period_data
                    }
            
            # 计算同比和环比增长率
            if len(result) >= 2:
                quarters = sorted(result.keys(), reverse=True)
                current_quarter = result[quarters[0]]['metrics']
                previous_quarter = result[quarters[1]]['metrics'] if len(quarters) > 1 else {}
                
                growth_rates = {}
                for metric in current_quarter:
                    if metric in previous_quarter:
                        current_val = current_quarter[metric]
                        previous_val = previous_quarter[metric]
                        if previous_val != 0:
                            growth_rate = ((current_val - previous_val) / abs(previous_val)) * 100
                            growth_rates[f"{metric}_qoq_growth"] = round(growth_rate, 2)
                
                result['growth_analysis'] = {
                    'quarter_over_quarter': growth_rates,
                    'comparison_period': f"{quarters[1]} vs {quarters[0]}"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"提取财务摘要指标失败: {str(e)}")
            return {}
    
    def _extract_income_statement_indicators(self, income_data: pd.DataFrame) -> Dict[str, Any]:
        """提取利润表指标 / Extract income statement indicators"""
        try:
            result = {}
            # 这里可以根据实际返回的数据结构进行处理
            if not income_data.empty:
                result['raw_data'] = income_data.fillna('').to_dict('records')
                result['data_points'] = len(income_data)
            return result
        except Exception as e:
            logger.error(f"提取利润表指标失败: {str(e)}")
            return {}
    
    def _extract_balance_sheet_indicators(self, balance_data: pd.DataFrame) -> Dict[str, Any]:
        """提取资产负债表指标 / Extract balance sheet indicators"""
        try:
            result = {}
            # 这里可以根据实际返回的数据结构进行处理
            if not balance_data.empty:
                result['raw_data'] = balance_data.fillna('').to_dict('records')
                result['data_points'] = len(balance_data)
            return result
        except Exception as e:
            logger.error(f"提取资产负债表指标失败: {str(e)}")
            return {}
    
    def _extract_cash_flow_indicators(self, cash_flow_data: pd.DataFrame) -> Dict[str, Any]:
        """提取现金流量表指标 / Extract cash flow indicators"""
        try:
            result = {}
            # 这里可以根据实际返回的数据结构进行处理
            if not cash_flow_data.empty:
                result['raw_data'] = cash_flow_data.fillna('').to_dict('records')
                result['data_points'] = len(cash_flow_data)
            return result
        except Exception as e:
            logger.error(f"提取现金流量表指标失败: {str(e)}")
            return {}
    
    def _extract_financial_ratios(self, ratio_data: pd.DataFrame) -> Dict[str, Any]:
        """提取财务比率 / Extract financial ratios"""
        try:
            result = {}
            # 这里可以根据实际返回的数据结构进行处理
            if not ratio_data.empty:
                result['raw_data'] = ratio_data.fillna('').to_dict('records')
                result['data_points'] = len(ratio_data)
            return result
        except Exception as e:
            logger.error(f"提取财务比率失败: {str(e)}")
            return {}
    
    def _calculate_profitability_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算盈利能力指标 / Calculate profitability indicators"""
        try:
            result = {}
            
            # 获取最新季度数据
            latest_quarter = None
            for key in sorted(financial_data.keys(), reverse=True):
                if key.startswith('Q') and 'metrics' in financial_data[key]:
                    latest_quarter = financial_data[key]['metrics']
                    break
            
            if not latest_quarter:
                return result
            
            # 计算各种盈利能力指标
            revenue = latest_quarter.get('total_revenue', 0)
            net_profit = latest_quarter.get('net_profit', 0)
            operating_profit = latest_quarter.get('operating_profit', 0)
            total_assets = latest_quarter.get('total_assets', 0)
            total_equity = latest_quarter.get('total_equity', 0)
            
            if revenue > 0:
                result['net_profit_margin'] = round((net_profit / revenue) * 100, 2)
                if operating_profit > 0:
                    result['operating_profit_margin'] = round((operating_profit / revenue) * 100, 2)
            
            if total_assets > 0:
                result['return_on_assets'] = round((net_profit / total_assets) * 100, 2)
            
            if total_equity > 0:
                result['return_on_equity'] = round((net_profit / total_equity) * 100, 2)
            
            # 添加ROE和ROA直接值
            result['roe'] = latest_quarter.get('roe', 0)
            result['roa'] = latest_quarter.get('roa', 0)
            
            return result
            
        except Exception as e:
            logger.error(f"计算盈利能力指标失败: {str(e)}")
            return {}
    
    def _calculate_efficiency_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算运营效率指标 / Calculate efficiency indicators"""
        try:
            result = {}
            
            # 获取最新季度数据
            latest_quarter = None
            for key in sorted(financial_data.keys(), reverse=True):
                if key.startswith('Q') and 'metrics' in financial_data[key]:
                    latest_quarter = financial_data[key]['metrics']
                    break
            
            if not latest_quarter:
                return result
            
            # 直接使用已有的周转率指标
            result['inventory_turnover'] = latest_quarter.get('inventory_turnover', 0)
            result['receivables_turnover'] = latest_quarter.get('receivables_turnover', 0)
            result['total_asset_turnover'] = latest_quarter.get('total_asset_turnover', 0)
            
            # 计算资产使用效率
            revenue = latest_quarter.get('total_revenue', 0)
            total_assets = latest_quarter.get('total_assets', 0)
            
            if total_assets > 0 and revenue > 0:
                result['asset_utilization_ratio'] = round(revenue / total_assets, 2)
            
            return result
            
        except Exception as e:
            logger.error(f"计算运营效率指标失败: {str(e)}")
            return {}
    
    def _calculate_liquidity_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算流动性指标 / Calculate liquidity indicators"""
        try:
            result = {}
            
            # 获取最新季度数据
            latest_quarter = None
            for key in sorted(financial_data.keys(), reverse=True):
                if key.startswith('Q') and 'metrics' in financial_data[key]:
                    latest_quarter = financial_data[key]['metrics']
                    break
            
            if not latest_quarter:
                return result
            
            # 直接使用已有的流动性指标
            result['current_ratio'] = latest_quarter.get('current_ratio', 0)
            result['quick_ratio'] = latest_quarter.get('quick_ratio', 0)
            
            # 计算现金流量相关指标
            operating_cash_flow = latest_quarter.get('operating_cash_flow', 0)
            current_liabilities = latest_quarter.get('current_liabilities', 0)
            
            if current_liabilities > 0:
                result['cash_flow_to_current_liabilities'] = round(operating_cash_flow / current_liabilities, 2)
            
            return result
            
        except Exception as e:
            logger.error(f"计算流动性指标失败: {str(e)}")
            return {}
    
    def _calculate_leverage_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算杠杆指标 / Calculate leverage indicators"""
        try:
            result = {}
            
            # 获取最新季度数据
            latest_quarter = None
            for key in sorted(financial_data.keys(), reverse=True):
                if key.startswith('Q') and 'metrics' in financial_data[key]:
                    latest_quarter = financial_data[key]['metrics']
                    break
            
            if not latest_quarter:
                return result
            
            # 直接使用已有的负债指标
            result['debt_ratio'] = latest_quarter.get('debt_ratio', 0)
            
            # 计算其他杠杆指标
            total_liabilities = latest_quarter.get('total_liabilities', 0)
            total_equity = latest_quarter.get('total_equity', 0)
            total_assets = latest_quarter.get('total_assets', 0)
            
            if total_equity > 0:
                result['debt_to_equity_ratio'] = round(total_liabilities / total_equity, 2)
            
            if total_assets > 0:
                result['equity_multiplier'] = round(total_assets / total_equity, 2) if total_equity > 0 else 0
            
            return result
            
        except Exception as e:
            logger.error(f"计算杠杆指标失败: {str(e)}")
            return {}
    
    def _calculate_growth_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算成长性指标 / Calculate growth indicators"""
        try:
            result = {}
            
            # 获取增长分析数据
            growth_analysis = financial_data.get('growth_analysis', {})
            if 'quarter_over_quarter' in growth_analysis:
                qoq_data = growth_analysis['quarter_over_quarter']
                
                # 提取关键增长指标
                result['revenue_growth_qoq'] = qoq_data.get('total_revenue_qoq_growth', 0)
                result['net_profit_growth_qoq'] = qoq_data.get('net_profit_qoq_growth', 0)
                result['operating_cash_flow_growth_qoq'] = qoq_data.get('operating_cash_flow_qoq_growth', 0)
                result['total_assets_growth_qoq'] = qoq_data.get('total_assets_qoq_growth', 0)
                result['total_equity_growth_qoq'] = qoq_data.get('total_equity_qoq_growth', 0)
            
            # 计算平均增长率
            growth_rates = [v for k, v in result.items() if k.endswith('_growth_qoq') and isinstance(v, (int, float))]
            if growth_rates:
                result['average_growth_rate'] = round(sum(growth_rates) / len(growth_rates), 2)
            
            return result
            
        except Exception as e:
            logger.error(f"计算成长性指标失败: {str(e)}")
            return {}