from typing import Optional


class LoginContextManager:
    """登录上下文管理器 - 负责跟踪和管理登录上下文"""
    
    def __init__(self):
        """
        初始化登录上下文管理器
        """
        self._current_context = None
    
    def set_context(self, context: Optional[str]) -> None:
        """
        设置登录上下文
        :param context: 上下文信息，通常是会话ID，用于标识不同玩家
        """
        self._current_context = context
    
    def get_context(self) -> Optional[str]:
        """
        获取当前登录上下文
        :return: 当前上下文信息或None
        """
        return self._current_context
    
    def clear_context(self) -> None:
        """
        清除当前登录上下文
        """
        self._current_context = None
    
    def is_context_set(self) -> bool:
        """
        检查是否设置了登录上下文
        :return: 是否已设置上下文
        """
        return self._current_context is not None