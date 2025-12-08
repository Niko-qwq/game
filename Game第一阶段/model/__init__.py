from .game_factory import GameFactory
from .rule_strategy import GomokuRuleStrategy, GoRuleStrategy
from .game_state import GomokuGameState, GoGameState
from .memento import GomokuMemento, GoMemento, MementoFactory
from .game_type_registry import GameTypeRegistry

# 获取游戏类型注册表单例
registry = GameTypeRegistry()

# 自动注册默认游戏类型及其组件

# 1. 注册五子棋组件
registry.register_rule_strategy("gomoku", GomokuRuleStrategy)
registry.register_game_state("gomoku", GomokuGameState)
registry.register_memento_class("gomoku", GomokuMemento)
registry.register_display_name("gomoku", "五子棋")
registry.register_default_board_size("gomoku", 15)

# 2. 注册围棋组件
registry.register_rule_strategy("go", GoRuleStrategy)
registry.register_game_state("go", GoGameState)
registry.register_memento_class("go", GoMemento)
registry.register_display_name("go", "围棋")
registry.register_default_board_size("go", 19)

# 兼容旧代码，通过GameFactory注册规则策略和游戏状态
GameFactory.register_game("gomoku", GomokuRuleStrategy, GomokuGameState, GomokuMemento, "五子棋", 15)
GameFactory.register_game("go", GoRuleStrategy, GoGameState, GoMemento, "围棋", 19)

# 注册备忘录类到MementoFactory
MementoFactory.register_memento_class("gomoku", GomokuMemento)
MementoFactory.register_memento_class("go", GoMemento)
