from abc import ABC, abstractmethod
from typing import Optional
from .ai_strategy import AIStrategy
from .ai_strategy_factory import AIStrategyFactory


class Player(ABC):
    """玩家抽象基类 - 定义玩家的基本接口"""
    
    def __init__(self, color):
        """
        初始化玩家
        :param color: 玩家颜色，"black"或"white"
        """
        self.color = color
        self.name = ""
        self.user = None  # 新增：关联的User对象，None表示游客或AI
    
    @abstractmethod
    def get_action(self, game_model):
        """
        根据当前局面做出决策
        :param game_model: 游戏模型对象，用于获取当前局面信息
        :return: 落子坐标(x, y)，或None表示需要等待外部事件
        """
        pass
    
    def get_color(self):
        """
        获取玩家颜色
        :return: 玩家颜色
        """
        return self.color
    
    def set_name(self, name):
        """
        设置玩家名称
        :param name: 玩家名称
        """
        self.name = name
    
    def get_name(self):
        """
        获取玩家名称
        :return: 玩家名称
        """
        return self.name
    
    def set_user(self, user):
        """
        设置关联的用户
        :param user: User对象，None表示游客或AI
        """
        self.user = user
        # 如果关联了用户，使用用户名作为玩家名称
        if user:
            self.name = user.get_username()
    
    def get_user(self):
        """
        获取关联的用户
        :return: User对象，None表示游客或AI
        """
        return self.user
    
    def is_logged_in(self):
        """
        判断玩家是否已登录
        :return: 是否已登录
        """
        return self.user is not None


class HumanPlayer(Player):
    """人类玩家 - 具体玩家实现"""
    
    def __init__(self, color):
        """
        初始化人类玩家
        :param color: 玩家颜色，"black"或"white"
        """
        super().__init__(color)
        self.name = "人类玩家"  # 默认名称，游客状态
    
    def get_action(self, game_model):
        """
        人类玩家通过GUI交互落子，此方法返回None表示等待外部事件
        :param game_model: 游戏模型对象
        :return: None
        """
        # 人类玩家通过GUI交互落子，此方法返回None表示等待外部事件
        return None


class AIPlayer(Player):
    """AI玩家 - 策略模式的上下文类，持有并调用策略"""
    
    def __init__(self, color, strategy=None, game_type="gomoku", difficulty="normal"):
        """
        初始化AI玩家
        
        :param color: 玩家颜色，"black"或"white"
        :param strategy: AIStrategy实例，如果为None则根据game_type和difficulty自动创建
        :param game_type: 游戏类型（如"gomoku", "reversi", "go"）
        :param difficulty: 难度等级（"easy", "normal", "hard"）
        """
        super().__init__(color)
        
        if strategy is not None:
            # 使用传入的策略
            if not isinstance(strategy, AIStrategy):
                raise ValueError(f"strategy必须是AIStrategy的实例: {strategy}")
            self.strategy = strategy
        else:
            # 根据游戏类型和难度自动创建策略
            factory = AIStrategyFactory()
            self.strategy = factory.get_strategy(game_type, difficulty)
        
        # 设置AI名称 - 简化为难度级别
        difficulty_map = {
            "easy": "一级",
            "normal": "二级", 
            "hard": "三级"
        }
        self.name = f"{difficulty_map.get(difficulty, difficulty)} AI"
        # AI玩家不关联用户，user属性保持为None
    
    def get_action(self, game_model):
        """
        根据策略获取落子动作
        
        :param game_model: 游戏模型对象
        :return: 落子坐标(x, y)，或None表示无棋可下
        """
        # 获取游戏信息
        board = game_model.get_board()
        rule_strategy = game_model.rule_strategy
        
        # 调用策略的get_action方法获取动作
        return self.strategy.get_action(board, rule_strategy, self.color)
    
    def set_strategy(self, strategy):
        """
        设置AI策略
        
        :param strategy: AIStrategy实例
        :return: None
        """
        if not isinstance(strategy, AIStrategy):
            raise ValueError(f"strategy必须是AIStrategy的实例: {strategy}")
        self.strategy = strategy
    
    def get_strategy(self):
        """
        获取当前AI策略
        
        :return: AIStrategy实例
        """
        return self.strategy




