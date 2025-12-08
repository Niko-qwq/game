from common.observer import Subject, auto_notify
from .game_state import GameState
from .game_logic import GameLogic
from .memento import MementoFactory
from .game_type_registry import GameTypeRegistry


class GameModel(Subject):
    """游戏模型 - 实现Subject模式和备忘录模式"""

    def __init__(self, game_type="gomoku", board_size=15, rule_strategy=None):
        """
        初始化游戏模型
        :param game_type: 游戏类型
        :param board_size: 棋盘大小
        :param rule_strategy: 游戏规则策略实例，由GameFactory提供
        """
        super().__init__()  # 初始化Subject基类
        
        # 使用GameTypeRegistry获取游戏状态类，替代if-else逻辑
        registry = GameTypeRegistry()
        game_state_class = registry.get_game_state_class(game_type)
        
        if not game_state_class:
            raise ValueError(f"不支持的游戏类型: {game_type}")
        
        # 实例化游戏状态类
        self.game_state = game_state_class(board_size)
        
        # 使用传入的规则策略，确保非空
        if rule_strategy is None:
            raise ValueError("规则策略不能为空")
        self.rule_strategy = rule_strategy
        
        # 创建游戏逻辑，注入策略
        self.game_logic = GameLogic(self.game_state, self.rule_strategy)
        
        # 将GameState的通知转发给GameModel的观察者
        self.game_state.attach(self)
    
    def get_current_player_color(self):
        """
        获取当前玩家颜色
        :return: 当前玩家颜色
        """
        return self.game_state.current_player_color
    
    def create_memento(self):
        """
        创建备忘录 - 备忘录模式的核心方法
        委托给GameState实现，支持不同游戏的个性化备忘录
        """
        return self.game_state.create_memento(self.game_logic.get_board())

    def restore_memento(self, memento):
        """
        恢复备忘录 - 备忘录模式的核心方法
        委托给GameState实现，支持不同游戏的个性化备忘录恢复
        """
        # 获取备忘录中的游戏类型和棋盘大小
        memento_game_type = memento.get_game_type()
        memento_board_size = memento.get_board().size
        
        # 检查当前游戏类型与备忘录中的游戏类型是否相同
        if self.game_state.game_type != memento_game_type or self.game_state.board_size != memento_board_size:
            # 游戏类型或棋盘大小改变，重新创建对象
            from .game_factory import GameFactory
            
            # 从GameFactory获取规则策略类并实例化
            rule_strategy_class = GameFactory.get_rule_strategy(memento_game_type)
            self.rule_strategy = rule_strategy_class()
            
            # 使用GameTypeRegistry获取游戏状态类
            registry = GameTypeRegistry()
            game_state_class = registry.get_game_state_class(memento_game_type)
            
            if not game_state_class:
                raise ValueError(f"不支持的游戏类型: {memento_game_type}")
            
            # 实例化游戏状态类
            new_game_state = game_state_class(memento_board_size)
            
            # 将旧GameState的观察者转移到新GameState
            # 使用受保护的_observers属性，因为Subject类没有提供获取所有观察者的方法
            for observer in self.game_state._observers:
                new_game_state.attach(observer)
            
            # 更新GameState引用
            self.game_state = new_game_state
            
            # 创建新的游戏逻辑，注入策略
            self.game_logic = GameLogic(self.game_state, self.rule_strategy)
        
        # 委托给GameState恢复备忘录
        self.game_state.restore_memento(memento, self.game_logic.get_board())
        
        # 通知观察者状态已更新
        self.notify()

    def make_move(self, x, y):
        """
        执行落子
        :param x: 横坐标
        :param y: 纵坐标
        :return: (是否成功, 信息)
        """
        return self.game_logic.make_move(x, y)

    def get_game_status(self):
        """
        获取游戏状态
        :return: 游戏状态字典
        """
        return self.game_state.get_game_status()

    @auto_notify
    def pass_move(self):
        """
        处理跳过落子
        :return: (是否成功, 信息)
        """
        return self.game_logic.pass_move()

    def reset(self):
        """
        重置游戏
        """
        # 重置游戏逻辑
        self.game_logic.reset()
    
    def get_board(self):
        """
        获取棋盘对象
        :return: 棋盘对象
        """
        return self.game_logic.get_board()
    
    def get_game_type(self):
        """
        获取游戏类型
        :return: 游戏类型
        """
        return self.game_state.game_type
    
    def get_winner(self):
        """
        获取胜者
        :return: 胜者颜色或None
        """
        return self.game_state.winner
    
    def is_game_over(self):
        """
        检查游戏是否结束
        :return: 游戏是否结束
        """
        return self.game_state.game_over
    
    def can_pass(self):
        """
        检查游戏是否支持跳过
        :return: 是否支持跳过
        """
        # 调用GameLogic的can_pass方法，避免重复逻辑
        can_pass, _ = self.game_logic.can_pass()
        return can_pass
    
    def set_game_over(self, winner=None):
        """
        设置游戏结束
        :param winner: 胜者颜色或None
        """
        self.game_state.set_game_over(winner)
    
    def update(self, subject, *args, **kwargs):
        """
        观察者模式的更新方法，当被观察者状态改变时调用
        这里主要是转发GameState的通知给GameModel的观察者
        :param subject: 被观察者对象
        :param args: 可变参数
        :param kwargs: 关键字参数
        """
        # 转发通知给GameModel的观察者
        self.notify(*args, **kwargs)