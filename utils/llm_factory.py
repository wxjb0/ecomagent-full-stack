from typing import Optional, Dict, Any
from config.settings import get_settings

settings = get_settings()

class LLMFactory:
    """LLM工厂类 - 创建和管理不同的大语言模型"""
    
    @staticmethod
    def create_llm(
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        创建LLM实例
        
        Args:
            provider: LLM提供商 (openai/anthropic/mock)
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            LLM实例
        """
        if provider == "mock" or not settings.OPENAI_API_KEY:
            return LLMFactory._create_mock_llm()
        
        if provider == "openai":
            return LLMFactory._create_openai_llm(
                model_name or settings.OPENAI_MODEL,
                temperature or settings.OPENAI_TEMPERATURE,
                max_tokens or settings.OPENAI_MAX_TOKENS,
                **kwargs
            )
        elif provider == "anthropic":
            return LLMFactory._create_anthropic_llm(
                model_name or settings.ANTHROPIC_MODEL,
                temperature or 0.7,
                max_tokens or 2000,
                **kwargs
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    @staticmethod
    def _create_openai_llm(
        model_name: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ):
        """创建OpenAI LLM"""
        try:
            from langchain_openai import ChatOpenAI
            
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=settings.OPENAI_API_KEY,
                **kwargs
            )
        except ImportError:
            print("警告: langchain-openai未安装，使用模拟LLM")
            return LLMFactory._create_mock_llm()
    
    @staticmethod
    def _create_anthropic_llm(
        model_name: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ):
        """创建Anthropic Claude LLM"""
        try:
            from langchain_anthropic import ChatAnthropic
            
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=settings.ANTHROPIC_API_KEY,
                **kwargs
            )
        except ImportError:
            print("警告: langchain-anthropic未安装，使用模拟LLM")
            return LLMFactory._create_mock_llm()
    
    @staticmethod
    def _create_mock_llm():
        """创建模拟LLM（用于测试）"""
        return MockLLM()


class MockLLM:
    """模拟LLM类 - 用于无需真实LLM的场景"""
    
    def __init__(self):
        self.model_name = "mock-llm"
    
    def invoke(self, *args, **kwargs):
        """模拟调用"""
        return MockResponse("这是模拟LLM的响应")
    
    def __call__(self, *args, **kwargs):
        """使对象可调用"""
        return self.invoke(*args, **kwargs)


class MockResponse:
    """模拟响应类"""
    
    def __init__(self, content: str):
        self.content = content
        self.response_metadata = {}
    
    def __str__(self):
        return self.content
