from abc import ABC, abstractmethod
from typing import Dict, Any
import hashlib

class UserInterface(ABC):
    """用户接口，定义用户基本行为"""
    
    @abstractmethod
    def get_username(self) -> str:
        """获取用户名"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str) -> bool:
        """验证密码是否正确"""
        pass
    
    @abstractmethod
    def update_record(self, won: bool) -> None:
        """更新用户战绩"""
        pass
    
    @abstractmethod
    def get_win_rate(self) -> float:
        """获取胜率"""
        pass


class User(UserInterface):
    """用户类 - 保存用户账号信息和战绩"""
    
    def __init__(self, username: str, password: str, total_games: int = 0, wins: int = 0):
        """
        初始化用户
        :param username: 用户名
        :param password: 密码
        :param total_games: 总对局数
        :param wins: 胜场数
        """
        # 属性验证
        if not username or len(username) < 3 or len(username) > 20:
            raise ValueError("用户名长度必须在3-20个字符之间")
        
        if not password or len(password) < 6:
            raise ValueError("密码长度必须至少为6个字符")
        
        if total_games < 0 or wins < 0 or wins > total_games:
            raise ValueError("战绩数据无效")
        
        # 使用私有属性增强封装
        self._username = username
        self._password_hash = self._hash_password(password)  # 存储密码哈希值
        self._total_games = total_games
        self._wins = wins
    
    def _hash_password(self, password: str) -> str:
        """
        对密码进行哈希处理
        :param password: 原始密码
        :return: 哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_username(self) -> str:
        """
        获取用户名
        :return: 用户名
        """
        return self._username
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码是否正确
        :param password: 待验证密码
        :return: 密码是否正确
        """
        return self._password_hash == self._hash_password(password)
    
    def update_password(self, old_password: str, new_password: str) -> bool:
        """
        更新密码
        :param old_password: 旧密码
        :param new_password: 新密码
        :return: 是否更新成功
        """
        if self.verify_password(old_password):
            self._password_hash = self._hash_password(new_password)
            return True
        return False
    
    @property
    def total_games(self) -> int:
        """
        获取总对局数
        :return: 总对局数
        """
        return self._total_games
    
    @property
    def wins(self) -> int:
        """
        获取胜场数
        :return: 胜场数
        """
        return self._wins
    
    def update_record(self, won: bool) -> None:
        """
        更新用户战绩
        :param won: 是否获胜
        """
        self._total_games += 1
        if won:
            self._wins += 1
    
    def get_win_rate(self) -> float:
        """
        获取胜率
        :return: 胜率，保留两位小数
        """
        if self._total_games == 0:
            return 0.0
        return round(self._wins / self._total_games, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典，用于持久化存储
        :return: 包含用户信息的字典
        """
        return {
            "username": self._username,
            "password_hash": self._password_hash,  # 存储哈希值而非明文
            "total_games": self._total_games,
            "wins": self._wins
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        从字典创建用户对象
        :param data: 包含用户信息的字典
        :return: User对象
        """
        user = cls.__new__(cls)  # 创建对象但不调用__init__
        user._username = data["username"]
        user._password_hash = data["password_hash"]
        user._total_games = data.get("total_games", 0)
        user._wins = data.get("wins", 0)
        return user

