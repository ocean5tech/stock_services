# -*- coding: utf-8 -*-
"""
AI Agent提示词管理器
Prompt Manager for AI Agents
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """提示词管理器 - 负责加载和管理AI Agent的提示词配置"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词文件目录，默认为当前文件夹下的prompts目录
        """
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.prompts_cache = {}  # 提示词缓存
        self.file_mtimes = {}    # 文件修改时间缓存
        
        # 确保prompts目录存在
        self.prompts_dir.mkdir(exist_ok=True)
        
        logger.info(f"PromptManager initialized with prompts_dir: {self.prompts_dir}")
    
    def load_prompt_config(self, agent_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载指定Agent的提示词配置
        
        Args:
            agent_name: Agent名称（对应yaml文件名）
            force_reload: 是否强制重新加载
            
        Returns:
            Dict: 提示词配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML解析错误
        """
        config_file = self.prompts_dir / f"{agent_name}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Prompt config file not found: {config_file}")
        
        # 检查文件是否需要重新加载
        current_mtime = config_file.stat().st_mtime
        cache_key = str(config_file)
        
        if (not force_reload and 
            cache_key in self.prompts_cache and 
            self.file_mtimes.get(cache_key) == current_mtime):
            logger.debug(f"Using cached prompt config for {agent_name}")
            return self.prompts_cache[cache_key]
        
        # 读取并解析YAML配置文件
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 验证必需的字段
            required_fields = ['agent_name', 'system_prompt', 'user_prompt_template']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                raise ValueError(f"Missing required fields in {config_file}: {missing_fields}")
            
            # 缓存配置和文件修改时间
            self.prompts_cache[cache_key] = config
            self.file_mtimes[cache_key] = current_mtime
            
            logger.info(f"Loaded prompt config for {agent_name} from {config_file}")
            return config
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config {config_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt config {config_file}: {e}")
            raise
    
    def get_system_prompt(self, agent_name: str) -> str:
        """获取系统提示词"""
        config = self.load_prompt_config(agent_name)
        return config['system_prompt']
    
    def get_user_prompt(self, agent_name: str, **kwargs) -> str:
        """
        获取用户提示词（支持模板变量替换）
        
        Args:
            agent_name: Agent名称
            **kwargs: 模板变量
            
        Returns:
            str: 格式化后的用户提示词
        """
        config = self.load_prompt_config(agent_name)
        template = config['user_prompt_template']
        
        try:
            # 添加默认变量
            default_vars = {
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': datetime.now().isoformat()
            }
            
            # 合并用户变量和默认变量
            variables = {**default_vars, **kwargs}
            
            # 使用format方法进行模板替换
            formatted_prompt = template.format(**variables)
            
            logger.debug(f"Formatted user prompt for {agent_name} with variables: {list(variables.keys())}")
            return formatted_prompt
            
        except KeyError as e:
            logger.error(f"Missing template variable {e} for agent {agent_name}")
            raise ValueError(f"Missing required template variable: {e}")
        except Exception as e:
            logger.error(f"Error formatting user prompt for {agent_name}: {e}")
            raise
    
    def get_model_parameters(self, agent_name: str) -> Dict[str, Any]:
        """获取模型参数配置"""
        config = self.load_prompt_config(agent_name)
        return config.get('parameters', {})
    
    def get_cache_config(self, agent_name: str) -> Dict[str, Any]:
        """获取缓存配置"""
        config = self.load_prompt_config(agent_name)
        return config.get('cache_config', {'enabled': False})
    
    def list_available_agents(self) -> list:
        """列出所有可用的Agent配置"""
        yaml_files = list(self.prompts_dir.glob("*.yaml"))
        agent_names = [f.stem for f in yaml_files]
        return sorted(agent_names)
    
    def validate_config(self, agent_name: str) -> Dict[str, Any]:
        """
        验证配置文件的完整性
        
        Returns:
            Dict: 验证结果
        """
        try:
            config = self.load_prompt_config(agent_name)
            result = {
                'valid': True,
                'agent_name': config.get('agent_name'),
                'version': config.get('version', 'unknown'),
                'has_system_prompt': bool(config.get('system_prompt')),
                'has_user_template': bool(config.get('user_prompt_template')),
                'parameters': config.get('parameters', {}),
                'cache_enabled': config.get('cache_config', {}).get('enabled', False)
            }
            
            logger.info(f"Config validation passed for {agent_name}")
            return result
            
        except Exception as e:
            logger.error(f"Config validation failed for {agent_name}: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def reload_all_configs(self):
        """重新加载所有配置文件"""
        self.prompts_cache.clear()
        self.file_mtimes.clear()
        logger.info("All prompt configs reloaded")

# 全局提示词管理器实例
prompt_manager = PromptManager()