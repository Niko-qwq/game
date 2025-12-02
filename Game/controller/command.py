from abc import ABC, abstractmethod
from re import S

class Command(ABC):
    """命令接口 - 命令模式的抽象命令"""
    
    @abstractmethod
    def execute(self):
        """执行命令"""
        pass
    
    @abstractmethod
    def undo(self):
        """撤销命令"""
        pass


class MoveCommand(Command):
    """移动命令 - 命令模式的具体命令"""
    def __init__(self, game_model, x, y):
        """
        初始化移动命令
        :param game_model: 游戏模型对象
        :param x: 横坐标
        :param y: 纵坐标
        """ 
        self.game_model = game_model
        self.x = x
        self.y = y
        self.memento = None  # 用于存储执行前的状态，以便撤销
    
    def execute(self):
        """执行移动命令"""
        # 保存当前状态，用于撤销
        self.memento = self.game_model.create_memento()
        # 执行落子
        return self.game_model.make_move(self.x, self.y)
    
    def undo(self):
        """撤销移动命令"""
        if self.memento:
            self.game_model.restore_memento(self.memento)
            return True, "悔棋成功"
        return False, "没有可悔的棋"


class UndoCommand(Command):
    """悔棋命令 - 命令模式的具体命令"""
    def __init__(self, command_history):
        """
        初始化悔棋命令
        :param command_history: 命令历史记录
        """
        self.command_history = command_history
    
    def execute(self):
        """执行悔棋命令"""
        if self.command_history:
            last_command = self.command_history.pop()
            return last_command.undo()
        return False, "没有可悔的棋"
    
    def undo(self):
        """撤销悔棋命令（不支持）"""
        return False, "悔棋命令不可撤销"

class ResetCommand(Command):
    """重置命令 - 命令模式的具体命令"""
    def __init__(self, game_model):
        """
        初始化重置命令
        :param game_model: 游戏模型对象
        """
        self.game_model = game_model
        self.memento = None
    
    def execute(self):
        """执行重置命令"""
        # 保存当前状态，用于撤销
        self.memento = self.game_model.create_memento()
        # 重置游戏
        self.game_model.reset()
        return True, "游戏已重置"
    
    def undo(self):
        """撤销重置命令"""
        if self.memento:
            self.game_model.restore_memento(self.memento)
            return True, "重置命令已撤销"
        return False, "无法撤销重置命令"
