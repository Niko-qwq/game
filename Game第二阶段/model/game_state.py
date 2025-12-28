from common.observer import Subject
from abc import ABC, abstractmethod


class GameState(Subject, ABC):
    """游戏状态管理基类 - 负责管理游戏的核心状态"""
    
    def __init__(self, game_type="gomoku", board_size=15):
        """
        初始化游戏状态
        :param game_type: 游戏类型，"gomoku"或"go"
        :param board_size: 棋盘大小
        """
        super().__init__()  # 初始化Subject基类
        self.game_type = game_type
        self.board_size = board_size
        self.current_player_color = "black"  # 黑方先行
        self.winner = None
        self.game_over = False
    
    @abstractmethod
    def create_memento(self, board):
        """
        创建备忘录 - 备忘录模式的核心方法
        :param board: 棋盘对象
        :return: 备忘录对象
        """
        pass
    
    @abstractmethod
    def restore_memento(self, memento, board):
        """
        恢复备忘录 - 备忘录模式的核心方法
        :param memento: 备忘录对象
        :param board: 棋盘对象，需要被恢复
        """
        pass
    
    def set_game_over(self, winner=None):
        """
        设置游戏结束
        :param winner: 胜者颜色，"black"或"white"或None
        """
        self.game_over = True
        self.winner = winner
        self.notify()

    def set_current_player_color(self, color):
        """
        设置当前玩家颜色
        :param color: 玩家颜色，"black"或"white"
        """
        self.current_player_color = color
        self.notify()
    
    def toggle_current_player(self):
        """
        切换当前玩家
        """
        self.current_player_color = ("white" if self.current_player_color == "black"
                               else "black")
        self.notify()
    
    def get_game_status(self):
        """
        获取游戏状态
        :return: 游戏状态字典
        """
        return {
            "game_type": self.game_type,
            "current_player": self.current_player_color,
            "winner": self.winner,
            "game_over": self.game_over,
            "board_size": self.board_size
        }
    
    def reset(self):
        """
        重置游戏状态
        """
        self.current_player_color = "black"
        self.winner = None
        self.game_over = False
        self.notify()


from .memento import MementoFactory


class GomokuGameState(GameState):
    """五子棋游戏状态 - 继承自GameState"""
    
    def __init__(self, board_size=15):
        """
        初始化五子棋游戏状态
        :param board_size: 棋盘大小
        """
        super().__init__(game_type="gomoku", board_size=board_size)
    
    def get_game_status(self):
        """
        获取五子棋游戏状态
        :return: 游戏状态字典
        """
        status = super().get_game_status()
        return status
    
    def reset(self):
        """
        重置五子棋游戏状态
        """
        super().reset()
    
    def create_memento(self, board):
        """
        创建五子棋备忘录
        :param board: 棋盘对象
        :return: 备忘录对象
        """
        return MementoFactory.create_memento(
            self.game_type,
            board,
            self.current_player_color
        )
    
    def restore_memento(self, memento, board):
        """
        恢复五子棋备忘录
        :param memento: 备忘录对象
        :param board: 棋盘对象，需要被恢复
        """
        # 恢复棋盘
        board.clear()
        memento_board = memento.get_board()
        for y in range(memento_board.size):
            for x in range(memento_board.size):
                piece = memento_board.get_piece(x, y)
                if piece is not None:
                    board.place_piece(x, y, piece.color)
        
        # 恢复当前玩家
        self.set_current_player_color(memento.get_current_player())
        
        # 重置其他状态
        self.winner = None
        self.game_over = False


class GoGameState(GameState):
    """围棋游戏状态 - 继承自GameState，包含围棋特有的属性"""
    
    def __init__(self, board_size=19):
        """
        初始化围棋游戏状态
        :param board_size: 棋盘大小
        """
        super().__init__(game_type="go", board_size=board_size)
        self.pass_count = 0  # 连续跳过落子的次数 - 围棋特有的属性
        self.count_black_pieces = 0
        self.count_white_pieces = 0
    
    def increment_pass_count(self):
        """
        增加连续跳过次数
        """
        self.pass_count += 1
        self.notify()
    
    def reset_pass_count(self):
        """
        重置连续跳过次数
        """
        self.pass_count = 0
        self.notify()
    
    def get_game_status(self):
        """
        获取围棋游戏状态
        :return: 游戏状态字典
        """
        status = super().get_game_status()
        status["pass_count"] = self.pass_count
        return status
    
    def reset(self):
        """
        重置围棋游戏状态
        """
        super().reset()
        self.pass_count = 0
        self.count_black_pieces = 0
        self.count_white_pieces = 0
        self.notify()
    
    def create_memento(self, board):
        """
        创建围棋备忘录
        :param board: 棋盘对象
        :return: 备忘录对象
        """
        return MementoFactory.create_memento(
            self.game_type,
            board,
            self.current_player_color,
            pass_count=self.pass_count,
            count_black_pieces=self.count_black_pieces,
            count_white_pieces=self.count_white_pieces
        )
    
    def restore_memento(self, memento, board):
        """
        恢复围棋备忘录
        :param memento: 备忘录对象
        :param board: 棋盘对象，需要被恢复
        """
        # 恢复棋盘
        board.clear()
        memento_board = memento.get_board()
        for y in range(memento_board.size):
            for x in range(memento_board.size):
                piece = memento_board.get_piece(x, y)
                if piece is not None:
                    board.place_piece(x, y, piece.color)
        
        # 恢复当前玩家
        self.set_current_player_color(memento.get_current_player())
        
        # 恢复跳过次数
        if hasattr(memento, 'get_pass_count'):
            self.pass_count = memento.get_pass_count()
        
        # 恢复提子数
        if hasattr(memento, 'get_count_black_pieces'):
            self.count_black_pieces = memento.get_count_black_pieces()
        if hasattr(memento, 'get_count_white_pieces'):
            self.count_white_pieces = memento.get_count_white_pieces()
        
        # 重置其他状态
        self.winner = None
        self.game_over = False


class ReversiGameState(GameState):
    """黑白棋游戏状态 - 继承自GameState，包含黑白棋特有的属性"""
    
    def __init__(self, board_size=8):
        """
        初始化黑白棋游戏状态
        :param board_size: 棋盘大小，默认为8x8
        """
        super().__init__(game_type="reversi", board_size=board_size)
        self.pass_count = 0  # 连续跳过落子的次数
    
    def increment_pass_count(self):
        """
        增加连续跳过次数
        """
        self.pass_count += 1
        self.notify()
    
    def reset_pass_count(self):
        """
        重置连续跳过次数
        """
        self.pass_count = 0
        self.notify()
    
    def get_game_status(self):
        """
        获取黑白棋游戏状态
        :return: 游戏状态字典
        """
        status = super().get_game_status()
        status["pass_count"] = self.pass_count
        return status
    
    def reset(self):
        """
        重置黑白棋游戏状态
        """
        super().reset()
        self.pass_count = 0
        self.notify()
    
    def create_memento(self, board):
        """
        创建黑白棋备忘录
        :param board: 棋盘对象
        :return: 备忘录对象
        """
        return MementoFactory.create_memento(
            self.game_type,
            board,
            self.current_player_color,
            pass_count=self.pass_count
        )
    
    def restore_memento(self, memento, board):
        """
        恢复黑白棋备忘录
        :param memento: 备忘录对象
        :param board: 棋盘对象，需要被恢复
        """
        # 恢复棋盘
        board.clear()
        memento_board = memento.get_board()
        for y in range(memento_board.size):
            for x in range(memento_board.size):
                piece = memento.get_board().get_piece(x, y)
                if piece is not None:
                    board.place_piece(x, y, piece.color)
        
        # 恢复当前玩家
        self.set_current_player_color(memento.get_current_player())
        
        # 恢复跳过次数
        if hasattr(memento, 'get_pass_count'):
            self.pass_count = memento.get_pass_count()
        
        # 重置其他状态
        self.winner = None
        self.game_over = False
