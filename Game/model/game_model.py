from observer import Subject, Observer
from .game_state import GameState
from .player_manager import PlayerManager
from .game_logic import GameLogic
from .memento import GameMemento
from .rule_strategy import GomokuRuleStrategy, GoRuleStrategy


class GameModel(Subject, Observer):
    """游戏模型 - 核心协调类，实现观察者模式和备忘录模式"""

    def __init__(self, game_type="gomoku", board_size=15):
        """
        初始化游戏模型
        :param game_type: 游戏类型，"gomoku"或"go"或"reversi"
        :param board_size: 棋盘大小
        """
        super().__init__()  # 初始化Subject基类
        
        # 创建游戏状态
        self.game_state = GameState(game_type, board_size)
        
        # 创建玩家管理器
        self.player_manager = PlayerManager()
        
        # 根据游戏类型创建对应的策略
        if game_type == "gomoku":
            strategy = GomokuRuleStrategy()
        elif game_type == "go":
            strategy = GoRuleStrategy()
        elif game_type == "reversi":
            strategy = ReversiRuleStrategy()
        else:
            raise ValueError(f"不支持的游戏类型: {game_type}")
        
        # 创建游戏逻辑
        self.game_logic = GameLogic(self.game_state, strategy)
        
        # 将GameState的通知转发给GameModel的观察者
        self.game_state.attach(self)
    
    def set_player(self, color, player):
        """
        设置玩家
        :param color: 玩家颜色，"black"或"white"
        :param player: 玩家对象
        """
        self.player_manager.set_player(color, player)
    
    def get_player(self, color):
        """
        获取玩家
        :param color: 玩家颜色，"black"或"white"
        :return: 玩家对象
        """
        return self.player_manager.get_player(color)
    
    def get_current_player(self):
        """
        获取当前玩家对象
        :return: 当前玩家对象
        """
        return self.player_manager.get_current_player(self.game_state.current_player_color)
    
    def get_current_player_color(self):
        """
        获取当前玩家颜色
        :return: 当前玩家颜色
        """
        return self.game_state.current_player_color
    
    def create_memento(self):
        """
        创建备忘录 - 备忘录模式的核心方法
        """
        return GameMemento(
            self.game_logic.get_board(), 
            self.game_state.current_player_color, 
            self.game_state.game_type
        )

    def restore_memento(self, memento):
        """
        恢复备忘录 - 备忘录模式的核心方法
        """
        # 重新创建游戏状态
        game_type = memento.get_game_type()
        self.game_state = GameState(
            game_type, 
            memento.get_board().size
        )
        
        # 根据游戏类型创建对应的策略
        if game_type == "gomoku":
            strategy = GomokuRuleStrategy()
        elif game_type == "go":
            strategy = GoRuleStrategy()
        elif game_type == "reversi":
            strategy = ReversiRuleStrategy()
        else:
            raise ValueError(f"不支持的游戏类型: {game_type}")
        
        # 重新创建游戏逻辑
        self.game_logic = GameLogic(self.game_state, strategy)
        
        # 恢复棋盘和当前玩家
        self.game_logic.board = memento.get_board()
        self.game_state.set_current_player_color(memento.get_current_player())
        
        # 重置其他状态
        self.game_state.winner = None
        self.game_state.game_over = False
        
        # 将GameState的通知转发给GameModel的观察者
        self.game_state.attach(self)
        
        # 通知观察者
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
        
        # 重置玩家
        self.player_manager.reset_players()
    
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
    
    def notify(self, **kwargs):
        """
        通知观察者 - 重写Subject的notify方法，添加game_model参数
        """
        super().notify(game_model=self, **kwargs)
    
    def update(self, subject, *args, **kwargs):
        """
        观察者模式的更新方法，当被观察者状态改变时调用
        这里主要是转发GameState的通知给GameModel的观察者
        """
        # 转发通知给GameModel的观察者
        self.notify(**kwargs)
