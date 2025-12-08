from abc import ABC, abstractmethod
from .memento import AbstractGameMemento


class GameTypeRegistry:
    """游戏类型注册表 - 单例模式，统一管理游戏类型相关的所有注册信息"""
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化各类注册表
            cls._instance._rule_strategies = {}  # {game_type: GameRuleStrategy子类}
            cls._instance._memento_classes = {}  # {game_type: AbstractGameMemento子类}
            cls._instance._game_state_classes = {}  # {game_type: GameState子类}
            cls._instance._display_names = {}  # {game_type: 显示名称}
            cls._instance._default_board_sizes = {}  # {game_type: 默认棋盘大小}
        return cls._instance
    
    def register_rule_strategy(self, game_type, strategy_class):
        """
        注册游戏规则策略类
        :param game_type: 游戏类型标识
        :param strategy_class: 游戏规则策略类
        """
        self._rule_strategies[game_type] = strategy_class
    
    def unregister_rule_strategy(self, game_type):
        """
        注销游戏规则策略类
        :param game_type: 游戏类型标识
        """
        if game_type in self._rule_strategies:
            del self._rule_strategies[game_type]
    
    def get_rule_strategy(self, game_type):
        """
        获取游戏规则策略类
        :param game_type: 游戏类型标识
        :return: 游戏规则策略类
        """
        if game_type not in self._rule_strategies:
            raise ValueError(f"不支持的游戏类型: {game_type}")
        return self._rule_strategies[game_type]
    
    def register_memento_class(self, game_type, memento_class):
        """
        注册游戏备忘录类
        :param game_type: 游戏类型标识
        :param memento_class: 游戏备忘录类，必须是AbstractGameMemento的子类
        """
        if not issubclass(memento_class, AbstractGameMemento):
            raise TypeError(f"{memento_class.__name__} 必须是 AbstractGameMemento 的子类")
        self._memento_classes[game_type] = memento_class
    
    def unregister_memento_class(self, game_type):
        """
        注销游戏备忘录类
        :param game_type: 游戏类型标识
        """
        if game_type in self._memento_classes:
            del self._memento_classes[game_type]
    
    def get_memento_class(self, game_type):
        """
        获取游戏备忘录类
        :param game_type: 游戏类型标识
        :return: 游戏备忘录类
        """
        return self._memento_classes.get(game_type)
    
    def register_game_state(self, game_type, game_state_class):
        """
        注册游戏状态类
        :param game_type: 游戏类型标识
        :param game_state_class: 游戏状态类，必须是GameState的子类
        """
        from .game_state import GameState
        if not issubclass(game_state_class, GameState):
            raise TypeError(f"{game_state_class.__name__} 必须是 GameState 的子类")
        self._game_state_classes[game_type] = game_state_class
    
    def unregister_game_state(self, game_type):
        """
        注销游戏状态类
        :param game_type: 游戏类型标识
        """
        if game_type in self._game_state_classes:
            del self._game_state_classes[game_type]
    
    def get_game_state_class(self, game_type):
        """
        获取游戏状态类
        :param game_type: 游戏类型标识
        :return: 游戏状态类
        """
        return self._game_state_classes.get(game_type)
    
    def register_display_name(self, game_type, display_name):
        """
        注册游戏显示名称
        :param game_type: 游戏类型标识
        :param display_name: 显示名称（如中文名称）
        """
        self._display_names[game_type] = display_name
    
    def get_display_name(self, game_type):
        """
        获取游戏显示名称
        :param game_type: 游戏类型标识
        :return: 显示名称
        """
        return self._display_names.get(game_type, game_type)
    
    def register_default_board_size(self, game_type, board_size):
        """
        注册游戏默认棋盘大小
        :param game_type: 游戏类型标识
        :param board_size: 默认棋盘大小
        """
        self._default_board_sizes[game_type] = board_size
    
    def get_default_board_size(self, game_type):
        """
        获取游戏默认棋盘大小
        :param game_type: 游戏类型标识
        :return: 默认棋盘大小
        """
        return self._default_board_sizes.get(game_type, 15)
    
    def get_all_game_types(self):
        """
        获取所有注册的游戏类型
        :return: 游戏类型列表
        """
        # 合并所有注册表中的游戏类型
        all_types = set()
        all_types.update(self._rule_strategies.keys())
        all_types.update(self._memento_classes.keys())
        all_types.update(self._display_names.keys())
        return sorted(list(all_types))
    
    def is_game_type_supported(self, game_type):
        """
        检查游戏类型是否支持
        :param game_type: 游戏类型标识
        :return: 是否支持
        """
        return game_type in self._rule_strategies
    
    def get_game_info(self, game_type):
        """
        获取游戏完整信息
        :param game_type: 游戏类型标识
        :return: 游戏信息字典
        """
        return {
            'game_type': game_type,
            'display_name': self.get_display_name(game_type),
            'default_board_size': self.get_default_board_size(game_type),
            'has_rule_strategy': game_type in self._rule_strategies,
            'has_memento_class': game_type in self._memento_classes
        }
