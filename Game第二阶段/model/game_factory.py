from .game_model import GameModel
from .rule_strategy import GameRuleStrategy
from .game_type_registry import GameTypeRegistry


class GameFactory:
    """游戏工厂 - 简单工厂模式的工厂类，支持动态注册游戏类型"""
    
    @classmethod
    def register_game(cls, game_type, rule_strategy_class, game_state_class=None, memento_class=None, display_name=None, default_board_size=None):
        """
        注册游戏类型
        :param game_type: 游戏类型标识
        :param rule_strategy_class: 游戏规则策略类，必须是GameRuleStrategy的子类
        :param game_state_class: 游戏状态类，必须是GameState的子类
        :param memento_class: 游戏备忘录类，必须是AbstractGameMemento的子类
        :param display_name: 游戏显示名称
        :param default_board_size: 游戏默认棋盘大小
        """
        registry = GameTypeRegistry()
        registry.register_rule_strategy(game_type, rule_strategy_class)
        
        if game_state_class:
            registry.register_game_state(game_type, game_state_class)
        
        if memento_class:
            registry.register_memento_class(game_type, memento_class)
        
        if display_name:
            registry.register_display_name(game_type, display_name)
        
        if default_board_size is not None:
            registry.register_default_board_size(game_type, default_board_size)
    
    @classmethod
    def unregister_game(cls, game_type):
        """
        注销游戏类型
        :param game_type: 游戏类型标识
        """
        registry = GameTypeRegistry()
        registry.unregister_rule_strategy(game_type)
        registry.unregister_game_state(game_type)
        registry.unregister_memento_class(game_type)
    
    @classmethod
    def get_rule_strategy(cls, game_type):
        """
        获取游戏规则策略类
        :param game_type: 游戏类型标识
        :return: 游戏规则策略类
        """
        registry = GameTypeRegistry()
        return registry.get_rule_strategy(game_type)
    
    @classmethod
    def get_game_state_class(cls, game_type):
        """
        获取游戏状态类
        :param game_type: 游戏类型标识
        :return: 游戏状态类
        """
        registry = GameTypeRegistry()
        return registry.get_game_state_class(game_type)
    
    @classmethod
    def create_game(cls, game_type, board_size=15):
        """
        创建游戏实例
        :param game_type: 游戏类型，通过register_game注册的类型
        :param board_size: 棋盘大小
        :return: 游戏模型对象
        """
        # 获取并实例化规则策略
        rule_strategy_class = cls.get_rule_strategy(game_type)
        rule_strategy = rule_strategy_class()
        
        # 创建游戏实例并注入规则策略
        return GameModel(game_type=game_type, board_size=board_size, rule_strategy=rule_strategy)

    @classmethod
    def get_supported_games(cls):
        """
        获取支持的游戏列表
        :return: 支持的游戏列表
        """
        return list(cls._registered_games.keys())
