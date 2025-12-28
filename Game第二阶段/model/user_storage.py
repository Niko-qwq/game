import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from model.user import User


class StorageStrategy(ABC):
    """存储策略抽象接口 - 定义存储操作"""
    
    @abstractmethod
    def read(self) -> Dict[str, Dict]:
        """
        读取所有数据
        :return: 数据字典
        """
        pass
    
    @abstractmethod
    def write(self, data: Dict[str, Dict]) -> bool:
        """
        写入所有数据
        :param data: 数据字典
        :return: 是否写入成功
        """
        pass


class JsonFileStorage(StorageStrategy):
    """JSON文件存储策略 - 实现基于JSON文件的存储"""
    
    def __init__(self, file_path: str):
        """
        初始化JSON文件存储
        :param file_path: 文件路径
        """
        self._file_path = file_path
    
    def read(self) -> Dict[str, Dict]:
        """
        从JSON文件读取数据
        :return: 数据字典
        """
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 文件不存在，返回空字典
            return {}
        except json.JSONDecodeError:
            # 文件格式错误，返回空字典
            return {}
    
    def write(self, data: Dict[str, Dict]) -> bool:
        """
        向JSON文件写入数据
        :param data: 数据字典
        :return: 是否写入成功
        """
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            return False
        except IOError:
            return False
        except Exception:
            return False


class UserStorageInterface(ABC):
    """用户存储抽象接口 - 定义用户存储操作"""
    
    @abstractmethod
    def save_user(self, user: User) -> Tuple[bool, str]:
        """
        保存用户数据
        :param user: User对象
        :return: (是否成功, 消息)
        """
        pass
    
    @abstractmethod
    def load_user(self, username: str) -> Tuple[Optional[User], str]:
        """
        加载指定用户数据
        :param username: 用户名
        :return: (User对象或None, 消息)
        """
        pass
    
    @abstractmethod
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        删除指定用户数据
        :param username: 用户名
        :return: (是否成功, 消息)
        """
        pass
    
    @abstractmethod
    def exists(self, username: str) -> bool:
        """
        检查用户是否存在
        :param username: 用户名
        :return: 用户是否存在
        """
        pass
    
    @abstractmethod
    def get_all_usernames(self) -> List[str]:
        """
        获取所有用户名
        :return: 用户名列表
        """
        pass


class UserStorage(UserStorageInterface):
    """用户存储类 - 负责用户数据的持久化"""
    
    def __init__(self, storage_strategy: StorageStrategy):
        """
        初始化用户存储
        :param storage_strategy: 存储策略对象
        """
        self._storage_strategy = storage_strategy
        self._cache = None
        self._cache_expiry = 300  # 缓存过期时间（秒）
        self._last_load_time = 0
    
    @classmethod
    def create_default(cls, file_path: str = "users.json") -> 'UserStorage':
        """
        创建默认的JSON文件存储实例
        :param file_path: 文件路径
        :return: UserStorage实例
        """
        return cls(JsonFileStorage(file_path))
    
    def _load_all_users(self) -> Dict[str, Dict]:
        """
        从存储加载所有用户数据，带缓存机制
        :return: 用户数据字典，键为用户名，值为用户信息字典
        """
        current_time = time.time()
        # 检查缓存是否过期或为空
        if self._cache is None or current_time - self._last_load_time > self._cache_expiry:
            self._cache = self._storage_strategy.read()
            self._last_load_time = current_time
        return self._cache
    
    def _save_all_users(self, users_data: Dict[str, Dict]) -> bool:
        """
        将所有用户数据保存到存储，并更新缓存
        :param users_data: 用户数据字典
        :return: 是否保存成功
        """
        if self._storage_strategy.write(users_data):
            # 更新缓存
            self._cache = users_data.copy()
            self._last_load_time = time.time()
            return True
        return False
    
    def save_user(self, user: User) -> Tuple[bool, str]:
        """
        保存用户数据
        :param user: User对象
        :return: (是否成功, 消息)
        """
        try:
            users_data = self._load_all_users()
            users_data[user.get_username()] = user.to_dict()
            if self._save_all_users(users_data):
                return True, "保存成功"
            return False, "保存失败：写入存储失败"
        except PermissionError:
            return False, "保存失败：权限不足"
        except IOError as e:
            return False, f"保存失败：IO错误 - {str(e)}"
        except Exception as e:
            return False, f"保存失败：未知错误 - {str(e)}"
    
    def load_user(self, username: str) -> Tuple[Optional[User], str]:
        """
        加载指定用户数据
        :param username: 用户名
        :return: (User对象或None, 消息)
        """
        try:
            users_data = self._load_all_users()
            if username in users_data:
                user = User.from_dict(users_data[username])
                return user, "加载成功"
            return None, "用户不存在"
        except Exception as e:
            return None, f"加载失败：{str(e)}"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        删除指定用户数据
        :param username: 用户名
        :return: (是否成功, 消息)
        """
        try:
            users_data = self._load_all_users()
            if username in users_data:
                del users_data[username]
                if self._save_all_users(users_data):
                    return True, "删除成功"
                return False, "删除失败：写入存储失败"
            return False, "用户不存在"
        except PermissionError:
            return False, "删除失败：权限不足"
        except IOError as e:
            return False, f"删除失败：IO错误 - {str(e)}"
        except Exception as e:
            return False, f"删除失败：未知错误 - {str(e)}"
    
    def exists(self, username: str) -> bool:
        """
        检查用户是否存在
        :param username: 用户名
        :return: 用户是否存在
        """
        users_data = self._load_all_users()
        return username in users_data
    
    def get_all_usernames(self) -> List[str]:
        """
        获取所有用户名
        :return: 用户名列表
        """
        users_data = self._load_all_users()
        return list(users_data.keys())
