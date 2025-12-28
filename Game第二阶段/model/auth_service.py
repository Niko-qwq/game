from abc import ABC, abstractmethod
from typing import Optional, Tuple
from model.user import User
from model.user_storage import UserStorage, UserStorageInterface


class AuthenticationServiceInterface(ABC):
    """认证服务抽象接口 - 定义用户认证操作"""
    
    @abstractmethod
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: (是否成功, 消息, User对象或None)
        """
        pass
    
    @abstractmethod
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户注册
        :param username: 用户名
        :param password: 密码
        :return: (是否成功, 消息)
        """
        pass
    
    @abstractmethod
    def verify_user(self, username: str, password: str) -> Tuple[bool, Optional[User]]:
        """
        验证用户凭证
        :param username: 用户名
        :param password: 密码
        :return: (是否验证成功, User对象或None)
        """
        pass


class DefaultAuthenticationService(AuthenticationServiceInterface):
    """默认认证服务实现"""
    
    def __init__(self, user_storage: Optional[UserStorageInterface] = None):
        """
        初始化认证服务
        :param user_storage: 用户存储接口实例，默认为None，使用默认JSON文件存储
        """
        self._user_storage = user_storage or UserStorage.create_default()
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录实现
        """
        try:
            # 加载用户
            user, message = self._user_storage.load_user(username)
            if user is None:
                return False, "用户名或密码错误", None
            
            # 验证密码
            if user.verify_password(password):
                return True, "登录成功", user
            return False, "用户名或密码错误", None
        except Exception as e:
            return False, f"登录失败：未知错误 - {str(e)}", None
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户注册实现
        """
        try:
            # 检查用户名是否已存在
            if self._user_storage.exists(username):
                return False, f"用户名 '{username}' 已存在"
            
            # 创建新用户
            user = User(username, password)
            
            # 保存用户
            success, message = self._user_storage.save_user(user)
            if success:
                return True, "注册成功"
            return False, f"注册失败：{message}"
        except ValueError as e:
            return False, f"注册失败：{str(e)}"
        except Exception as e:
            return False, f"注册失败：未知错误 - {str(e)}"
    
    def verify_user(self, username: str, password: str) -> Tuple[bool, Optional[User]]:
        """
        验证用户凭证实现
        """
        try:
            user, _ = self._user_storage.load_user(username)
            if user and user.verify_password(password):
                return True, user
            return False, None
        except Exception:
            return False, None