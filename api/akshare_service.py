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
from config import Config

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