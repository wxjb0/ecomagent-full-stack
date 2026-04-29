from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.llms import BaseLLM

class SharedAgentMemory:
    """Agent间的共享记忆模块"""
    
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm
        self.agent_outputs: Dict[str, Any] = {}
        self.conversation_memory = ConversationBufferMemory(
            memory_key="shared_chat_history",
            return_messages=True,
            output_key="output"
        )
        self.summary_memory = None
        
        if llm:
            self.summary_memory = ConversationSummaryMemory(
                llm=llm,
                memory_key="conversation_summary",
                return_messages=True
            )
    
    def save_agent_output(self, agent_name: str, output: Dict[str, Any]):
        """保存Agent的输出"""
        self.agent_outputs[agent_name] = output
        
        # 同时保存到对话记忆
        self.conversation_memory.save_context(
            {"input": f"{agent_name}_agent_executed"},
            {"output": str(output.get("summary", "Agent executed successfully"))}
        )
        
        if self.summary_memory:
            self.summary_memory.save_context(
                {"input": f"{agent_name}_agent_executed"},
                {"output": str(output.get("summary", "Agent executed successfully"))}
            )
    
    def get_agent_output(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """获取特定Agent的输出"""
        return self.agent_outputs.get(agent_name)
    
    def get_all_outputs(self) -> Dict[str, Any]:
        """获取所有Agent的输出"""
        return self.agent_outputs.copy()
    
    def get_memory(self) -> ConversationBufferMemory:
        """获取对话记忆"""
        return self.conversation_memory
    
    def get_summary(self) -> Optional[str]:
        """获取对话摘要"""
        if self.summary_memory:
            variables = self.summary_memory.load_memory_variables({})
            return variables.get("conversation_summary", "")
        return None
    
    def get_context_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        获取特定Agent的上下文信息
        包含之前Agent的输出，供当前Agent使用
        """
        context = {
            "shared_memory": self.get_all_outputs(),
            "conversation_history": self.conversation_memory.load_memory_variables({}),
        }
        
        if self.summary_memory:
            context["conversation_summary"] = self.get_summary()
        
        return context
    
    def clear(self):
        """清空所有记忆"""
        self.agent_outputs = {}
        self.conversation_memory.clear()
        if self.summary_memory:
            self.summary_memory.clear()
    
    def get_memory_state(self) -> Dict[str, Any]:
        """获取记忆状态"""
        return {
            "agent_outputs_count": len(self.agent_outputs),
            "agent_outputs": list(self.agent_outputs.keys()),
            "has_summary_memory": self.summary_memory is not None,
            "conversation_summary": self.get_summary()
        }
