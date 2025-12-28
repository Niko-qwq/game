from typing import Optional, Tuple
from abc import ABC, abstractmethod
from model.user import User
from model.user_storage import UserStorage, UserStorageInterface
from model.auth_service import AuthenticationServiceInterface, DefaultAuthenticationService
from model.session_manager import SessionManagerInterface, DefaultSessionManager


# 自定义异常类
class UserManagerException(Exception):
    """UserManager相关异常基类"""
    pass


class UserAlreadyExistsException(UserManagerException):
    """用户已存在异常"""
    def __init__(self, username: str):
        super().__init__(f"用户名 '{username}' 已存在")


class AuthenticationFailedException(UserManagerException):
    """认证失败异常"""
    def __init__(self):
        super().__init__("用户名或密码错误")


class UserNotFoundException(UserManagerException):
    """用户不存在异常"""
    def __init__(self, username: str):
        super().__init__(f"用户名 '{username}' 不存在")


class UserManager:
    """用户管理器 - 负责用户注册、登录、战绩更新等"""
    
    def __init__(self, 
                 user_storage: Optional[UserStorageInterface] = None,
                 auth_service: Optional[AuthenticationServiceInterface] = None,
                 session_manager: Optional[SessionManagerInterface] = None):
        """
        初始化用户管理器
        :param user_storage: 用户存储接口实例，默认为None，使用默认JSON文件存储
        :param auth_service: 认证服务接口实例，默认为None，使用默认认证服务
        :param session_manager: 会话管理器接口实例，默认为None，使用默认会话管理器
        """
        # 使用依赖注入，支持不同存储策略
        self._user_storage = user_storage or UserStorage.create_default()
        # 注入认证服务
        self._auth_service = auth_service or DefaultAuthenticationService(self._user_storage)
        # 注入会话管理器
        self._session_manager = session_manager or DefaultSessionManager()
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户注册
        :param username: 用户名
        :param password: 密码
        :return: (是否成功, 消息)
        """
        return self._auth_service.register(username, password)
    
    def login(self, username: str, password: str, session_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :param session_id: 会话ID，用于标识不同玩家的登录会话，默认为None
        :return: (是否成功, 消息)
        """
        success, message, user = self._auth_service.login(username, password)
        if success and user and session_id:
            # 如果提供了会话ID，将用户关联到该会话
            self._session_manager.create_session(session_id, user)
        return success, message
    
    def logout(self, session_id: Optional[str] = None) -> None:
        """
        用户登出
        :param session_id: 会话ID，用于标识要登出的玩家会话，默认为None（登出所有会话）
        """
        if session_id:
            # 登出指定会话
            self._session_manager.remove_session(session_id)
        else:
            # 登出所有会话
            self._session_manager.clear_all_sessions()
    
    def get_current_user(self, session_id: Optional[str] = None) -> Optional[User]:
        """
        获取当前登录用户
        :param session_id: 会话ID，用于标识要获取的玩家会话，默认为None
        :return: 当前登录用户或None
        """
        if session_id:
            # 获取指定会话的用户
            return self._session_manager.get_session_user(session_id)
        # 保持向后兼容，返回第一个活跃会话的用户
        # 实际实现中，可以根据需要调整，这里简单返回None
        return None
    
    def update_player_record(self, player, won: bool) -> None:
        """
        更新玩家战绩
        :param player: 玩家对象
        :param won: 是否获胜
        """
        # 检查玩家是否关联了用户
        if hasattr(player, 'user') and player.user is not None:
            # 更新用户战绩
            player.user.update_record(won)
            # 保存用户数据
            self._user_storage.save_user(player.user)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        :param username: 用户名
        :return: User对象或None
        """
        user, _ = self._user_storage.load_user(username)
        return user
    
    def update_current_user_record(self, won: bool) -> bool:
        """
        更新当前登录用户的战绩
        :param won: 是否获胜
        :return: 是否更新成功
        """
        if self._current_user is not None:
            self._current_user.update_record(won)
            success, _ = self._user_storage.save_user(self._current_user)
            return success
        return False
    
    def is_logged_in(self, session_id: Optional[str] = None) -> bool:
        """
        检查是否有用户登录
        :param session_id: 会话ID，用于标识要检查的玩家会话，默认为None
        :return: 是否有用户登录
        """
        if session_id:
            # 检查指定会话是否有用户登录
            return self._session_manager.is_session_active(session_id)
        # 检查是否有任何活跃会话
        # 实际实现中，可以根据需要调整，这里简单返回False
        return False
    
    def get_current_username(self, session_id: Optional[str] = None) -> Optional[str]:
        """
        获取当前登录用户名
        :param session_id: 会话ID，用于标识要获取的玩家会话，默认为None
        :return: 当前登录用户名或None
        """
        user = self.get_current_user(session_id)
        if user:
            return user.get_username()
        return None
    
    def save_user(self, user: User) -> Tuple[bool, str]:
        """
        保存用户数据
        :param user: User对象
        :return: (是否成功, 消息)
        """
        return self._user_storage.save_user(user)
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        删除用户
        :param username: 用户名
        :return: (是否成功, 消息)
        """
        return self._user_storage.delete_user(username)
    
    def get_all_usernames(self) -> list[str]:
        """
        获取所有用户名
        :return: 用户名列表
        """
        return self._user_storage.get_all_usernames()


# 创建一个默认实例，方便其他模块使用，但不强制使用单例模式
default_user_manager = UserManager()
