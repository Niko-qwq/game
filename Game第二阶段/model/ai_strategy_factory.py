from .ai_strategy import (
    AIStrategy,
    RandomStrategy,
    GomokuGreedyStrategy,
    GomokuMCTSStrategy,
    ReversiGreedyStrategy,
    ReversiMCTSStrategy
)
from .game_type_registry import GameTypeRegistry


class AIStrategyFactory:
    """AI策略工厂 - 用于根据游戏类型和难度选择策略"""
    
    def __init__(self):
        # 使用GameTypeRegistry来管理AI策略
        self.registry = GameTypeRegistry()
        # 初始化默认策略
        self._init_default_strategies()
    
    def _init_default_strategies(self):
        """初始化默认AI策略"""
        # 注册五子棋AI策略
        self.register_strategy("gomoku", "easy", RandomStrategy)
        self.register_strategy("gomoku", "normal", GomokuGreedyStrategy)
        self.register_strategy("gomoku", "hard", GomokuMCTSStrategy)  # 使用MCTS算法作为高级策略
        
        # 注册黑白棋AI策略
        self.register_strategy("reversi", "easy", RandomStrategy)
        self.register_strategy("reversi", "normal", ReversiGreedyStrategy)
        self.register_strategy("reversi", "hard", ReversiMCTSStrategy)  # 使用MCTS算法作为高级策略
        
        # 注册围棋AI策略
        self.register_strategy("go", "easy", RandomStrategy)
        self.register_strategy("go", "normal", RandomStrategy)  # 围棋可以添加专门的贪心策略
        self.register_strategy("go", "hard", RandomStrategy)     # 可以替换为更高级的策略，如MCTS
    
    def get_strategy(self, game_type, difficulty="normal"):
        """
        根据游戏类型和难度获取对应的策略实例
        
        :param game_type: 游戏类型（如"gomoku", "reversi", "go"）
        :param difficulty: 难度等级（"easy", "normal", "hard"）
        :return: AIStrategy实例
        :raises ValueError: 如果游戏类型或难度不支持
        """
        # 从注册表中获取策略类
        strategy_class = self.registry.get_ai_strategy(game_type, difficulty)
        return strategy_class()
    
    def register_strategy(self, game_type, difficulty, strategy_class):
        """
        注册新的策略
        
        :param game_type: 游戏类型
        :param difficulty: 难度等级
        :param strategy_class: 策略类，必须是AIStrategy的子类
        :return: None
        """
        if not issubclass(strategy_class, AIStrategy):
            raise ValueError(f"策略类必须是AIStrategy的子类: {strategy_class}")
        
        # 注册到GameTypeRegistry
        self.registry.register_ai_strategy(game_type, difficulty, strategy_class)
    
    def get_supported_difficulties(self, game_type):
        """
        获取游戏类型支持的难度列表
        
        :param game_type: 游戏类型
        :return: 难度列表
        """
        return self.registry.get_supported_difficulties(game_type)
    
    def get_supported_games(self):
        """
        获取支持的游戏类型列表
        
        :return: 游戏类型列表
        """
        return self.registry.get_all_game_types()
