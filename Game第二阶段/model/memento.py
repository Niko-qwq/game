
import copy
from abc import ABC, abstractmethod


class AbstractGameMemento(ABC):
    """抽象游戏备忘录接口 - 定义备忘录的通用方法"""
    
    @abstractmethod
    def get_board(self):
        """获取棋盘状态"""
        pass
    
    @abstractmethod
    def get_current_player(self):
        """获取当前玩家"""
        pass
    
    @abstractmethod
    def get_game_type(self):
        """获取游戏类型"""
        pass
    
    @abstractmethod
    def get_state(self):
        """获取完整状态字典"""
        pass


class GomokuMemento(AbstractGameMemento):
    """五子棋专用备忘录 - 只存储五子棋需要的状态"""
    
    def __init__(self, board, current_player, game_type, **kwargs):
        # 深拷贝棋盘
        self.board = board.clone() if hasattr(board, 'clone') else copy.deepcopy(board)
        self.current_player = current_player
        self.game_type = game_type
    
    # Getters
    def get_board(self): 
        return self.board
        
    def get_current_player(self): 
        return self.current_player
        
    def get_game_type(self): 
        return self.game_type
        
    def get_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_type': self.game_type
        }


class GoMemento(AbstractGameMemento):
    """围棋专用备忘录 - 只存储围棋需要的状态"""
    
    def __init__(self, board, current_player, game_type, pass_count=0, count_black_pieces=0, count_white_pieces=0):
        # 深拷贝棋盘
        self.board = board.clone() if hasattr(board, 'clone') else copy.deepcopy(board)
        self.current_player = current_player
        self.game_type = game_type
        self.pass_count = pass_count
        self.count_black_pieces = count_black_pieces  # 黑棋的提子数
        self.count_white_pieces = count_white_pieces  # 白棋的提子数
    
    # Getters
    def get_board(self): 
        return self.board
        
    def get_current_player(self): 
        return self.current_player
        
    def get_game_type(self): 
        return self.game_type
        
    def get_pass_count(self): 
        return self.pass_count
        
    def get_count_black_pieces(self):
        return self.count_black_pieces
        
    def get_count_white_pieces(self):
        return self.count_white_pieces
        
    def get_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_type': self.game_type,
            'pass_count': self.pass_count,
            'count_black_pieces': self.count_black_pieces,
            'count_white_pieces': self.count_white_pieces
        }


class ReversiMemento(AbstractGameMemento):
    """黑白棋专用备忘录 - 只存储黑白棋需要的状态"""
    
    def __init__(self, board, current_player, game_type, pass_count=0):
        # 深拷贝棋盘
        self.board = board.clone() if hasattr(board, 'clone') else copy.deepcopy(board)
        self.current_player = current_player
        self.game_type = game_type
        self.pass_count = pass_count
    
    # Getters
    def get_board(self): 
        return self.board
        
    def get_current_player(self): 
        return self.current_player
        
    def get_game_type(self): 
        return self.game_type
        
    def get_pass_count(self): 
        return self.pass_count
        
    def get_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_type': self.game_type,
            'pass_count': self.pass_count
        }


class MementoFactory:
    """备忘录工厂 - 用于创建不同游戏的备忘录"""
    
    @staticmethod
    def create_memento(game_type, board, current_player, **kwargs):
        """
        创建指定游戏类型的备忘录
        
        :param game_type: 游戏类型
        :param board: 棋盘对象
        :param current_player: 当前玩家
        :param kwargs: 其他游戏特有参数
        :return: 对应游戏类型的备忘录对象
        """
        from .game_type_registry import GameTypeRegistry
        registry = GameTypeRegistry()
        memento_class = registry.get_memento_class(game_type)
        
        if memento_class:
            # 使用注册的备忘录类
            return memento_class(board, current_player, game_type, **kwargs)
        else:
            # 对于未明确指定的游戏类型，使用通用的状态存储
            # 收集所有关键字参数并存储
            memento = type(f"{game_type.capitalize()}Memento", 
                          (AbstractGameMemento,), 
                          {
                              '__init__': lambda self, b, cp, gt, **kw: (
                                  setattr(self, 'board', b.clone() if hasattr(b, 'clone') else copy.deepcopy(b)),
                                  setattr(self, 'current_player', cp),
                                  setattr(self, 'game_type', gt),
                                  [setattr(self, k, v) for k, v in kw.items()]
                              ),
                              'get_board': lambda self: self.board,
                              'get_current_player': lambda self: self.current_player,
                              'get_game_type': lambda self: self.game_type,
                              'get_state': lambda self: {
                                  attr: getattr(self, attr)
                                  for attr in dir(self)
                                  if not attr.startswith('__')
                              }
                          })
            return memento(board, current_player, game_type, **kwargs)
    
    @staticmethod
    def register_memento_class(game_type, memento_class):
        """
        注册备忘录类到全局注册表
        :param game_type: 游戏类型标识
        :param memento_class: 备忘录类
        """
        from .game_type_registry import GameTypeRegistry
        registry = GameTypeRegistry()
        registry.register_memento_class(game_type, memento_class)


# class GameMemento(AbstractGameMemento):
#     """通用游戏备忘录 - 用于存储通用游戏状态"""
    
#     def __init__(self, board, current_player, game_type, pass_count=0, count_black_pieces=0, count_white_pieces=0):
#         # 深拷贝棋盘
#         self.board = board.clone() if hasattr(board, 'clone') else copy.deepcopy(board)
#         self.current_player = current_player
#         self.game_type = game_type
#         self.pass_count = pass_count
#         self.count_black_pieces = count_black_pieces  # 黑棋的提子数
#         self.count_white_pieces = count_white_pieces  # 白棋的提子数
    
#     # Getters
#     def get_board(self): return self.board
#     def get_current_player(self): return self.current_player
#     def get_game_type(self): return self.game_type
#     def get_pass_count(self): return self.pass_count
#     def get_count_black_pieces(self): return self.count_black_pieces
#     def get_count_white_pieces(self): return self.count_white_pieces
#     def get_state(self):
#         return {
#             'board': self.board,
#             'current_player': self.current_player,
#             'game_type': self.game_type,
#             'pass_count': self.pass_count,
#             'count_black_pieces': self.count_black_pieces,
#             'count_white_pieces': self.count_white_pieces
#         }
