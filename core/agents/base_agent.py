from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain.llms import BaseLLM
from langchain.memory import ConversationBufferMemory
from config.settings import get_settings

settings = get_settings()

class BaseAgent(ABC):
    """所有Agent的基类"""
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        memory: Optional[ConversationBufferMemory] = None,
        agent_name: str = "BaseAgent"
    ):
        self.llm = llm
        self.memory = memory or ConversationBufferMemory(
            memory_key=f"{agent_name.lower()}_chat_history",
            return_messages=True
        ) if settings.ENABLE_AGENT_MEMORY else None
        self.agent_name = agent_name
        self.settings = settings
        
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """执行Agent的核心逻辑，必须由子类实现"""
        pass
    
    def save_to_memory(self, input_str: str, output_str: str):
        """保存对话到记忆"""
        if self.memory:
            self.memory.save_context(
                {"input": input_str},
                {"output": output_str}
            )
    
    def get_memory_context(self) -> Optional[Dict]:
        """获取记忆上下文"""
        if self.memory:
            return self.memory.load_memory_variables({})
        return None
    
    def log(self, message: str, level: str = "INFO"):
        """简单的日志记录"""
        print(f"[{level}] [{self.agent_name}] {message}")
