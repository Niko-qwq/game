from abc import ABC, abstractmethod
from typing import Optional, Dict
from model.user import User


class SessionManagerInterface(ABC):
    """会话管理器抽象接口 - 定义会话管理操作"""
    
    @abstractmethod
    def create_session(self, session_id: str, user: User) -> None:
        """
        创建会话
        :param session_id: 会话ID，用于标识不同的玩家会话
        :param user: 要关联到会话的用户对象
        """
        pass
    
    @abstractmethod
    def get_session_user(self, session_id: str) -> Optional[User]:
        """
        获取会话关联的用户
        :param session_id: 会话ID
        :return: 关联的用户对象或None
        """
        pass
    
    @abstractmethod
    def remove_session(self, session_id: str) -> None:
        """
        移除会话
        :param session_id: 会话ID
        """
        pass
    
    @abstractmethod
    def clear_all_sessions(self) -> None:
        """
        清除所有会话
        """
        pass
    
    @abstractmethod
    def update_session(self, session_id: str, user: User) -> None:
        """
        更新会话关联的用户
        :param session_id: 会话ID
        :param user: 新的用户对象
        """
        pass
    
    @abstractmethod
    def is_session_active(self, session_id: str) -> bool:
        """
        检查会话是否活跃
        :param session_id: 会话ID
        :return: 会话是否活跃
        """
        pass


class DefaultSessionManager(SessionManagerInterface):
    """默认会话管理器实现"""
    
    def __init__(self):
        """
        初始化会话管理器
        """
        # 会话存储：{session_id: User对象}
        self._sessions: Dict[str, User] = {}
    
    def create_session(self, session_id: str, user: User) -> None:
        """
        创建会话实现
        """
        self._sessions[session_id] = user
    
    def get_session_user(self, session_id: str) -> Optional[User]:
        """
        获取会话关联的用户实现
        """
        return self._sessions.get(session_id, None)
    
    def remove_session(self, session_id: str) -> None:
        """
        移除会话实现
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def clear_all_sessions(self) -> None:
        """
        清除所有会话实现
        """
        self._sessions.clear()
    
    def update_session(self, session_id: str, user: User) -> None:
        """
        更新会话关联的用户实现
        """
        self._sessions[session_id] = user
    
    def is_session_active(self, session_id: str) -> bool:
        """
        检查会话是否活跃实现
        """
        return session_id in self._sessions