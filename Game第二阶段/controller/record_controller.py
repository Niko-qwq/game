from controller.command import MoveCommand
from controller.command_manager import CommandManager
from model.game_factory import GameFactory


class RecordController:
    """
    录像控制器 - 负责游戏录像的记录和回放功能
    """
    
    def __init__(self):
        """
        初始化录像控制器
        """
        self.playback_model = None  # 用于回放的游戏模型
        self.playback_history = []  # 回放的历史记录
        self.playback_index = -1    # 当前回放的索引位置
        
    def load_history(self, save_data):
        """
        加载历史记录到回放控制器
        
        Args:
            save_data: 从存档中加载的游戏数据
        """
        if not save_data or not save_data.history:
            return False, "没有可用的历史记录"
        
        try:
            # 1. 创建新的游戏模型用于回放
            memento = save_data.memento
            self.playback_model = GameFactory.create_game(
                memento.get_game_type(),
                memento.get_board().size
            )
            
            # 2. 加载历史记录
            self.playback_history = save_data.history
            self.playback_index = -1  # 重置索引
            
            return True, "历史记录加载成功"
            
        except Exception as e:
            return False, f"加载历史记录失败: {str(e)}"
    

    
    def step_forward(self):
        """
        前进一格（播放下一步）
        """
        if not self.playback_model or not self.playback_history:
            return False, "没有可用的回放数据"
        
        if self.playback_index < len(self.playback_history) - 1:
            self.playback_index += 1
            move = self.playback_history[self.playback_index]
            return self._execute_move(move)
        
        return False, "已经是最后一步"
    
    def step_backward(self):
        """
        后退一格（回退一步）
        """
        if not self.playback_model or not self.playback_history:
            return False, "没有可用的回放数据"
        
        if self.playback_index > 0:
            # 重置模型并重新执行到上一步
            self._reset_playback_model()
            self.playback_index -= 1
            
            # 重新执行从第一步到当前步的所有移动
            for i in range(self.playback_index + 1):
                move = self.playback_history[i]
                success, message = self._execute_move(move)
                if not success:
                    return success, message
            
            return True, "回退成功"
        
        return False, "已经是第一步"
    
    def jump_to_step(self, step):
        """
        跳转到指定步数
        
        Args:
            step: 目标步数（从0开始）
        """
        if not self.playback_model or not self.playback_history:
            return False, "没有可用的回放数据"
        
        if 0 <= step < len(self.playback_history):
            # 重置模型
            self._reset_playback_model()
            
            # 执行到指定步数
            for i in range(step + 1):
                move = self.playback_history[i]
                success, message = self._execute_move(move)
                if not success:
                    return success, message
            
            self.playback_index = step
            return True, f"已跳转到第{step + 1}步"
        
        return False, "无效的步数"
    
    def get_current_step(self):
        """
        获取当前回放步数
        """
        return self.playback_index + 1 if self.playback_index >= 0 else 0
    
    def get_total_steps(self):
        """
        获取总步数
        """
        return len(self.playback_history)
    
    def is_playback_available(self):
        """
        检查是否可以回放
        """
        return bool(self.playback_model and self.playback_history)
    
    def get_playback_model(self):
        """
        获取回放模型
        """
        return self.playback_model
    
    def _reset_playback_model(self):
        """
        重置回放模型到初始状态
        """
        if self.playback_model:
            # 创建新的游戏模型，重置到初始状态
            game_type = self.playback_model.get_game_type()
            board_size = self.playback_model.get_board().size
            self.playback_model = GameFactory.create_game(game_type, board_size)
    
    def _execute_move(self, move):
        """
        执行单个移动
        
        Args:
            move: 移动数据，包含x, y等信息
        """
        if not self.playback_model:
            return False, "回放模型不存在"
        
        try:
            # 确保游戏未结束
            if self.playback_model.is_game_over():
                return False, "游戏已结束"
            
            # 创建并执行移动命令
            x = move.get('x')
            y = move.get('y')
            
            if x is None or y is None:
                return False, "移动数据无效"
            
            # 直接执行移动，不记录到命令管理器
            # GameModel类使用make_move方法来处理落子
            if hasattr(self.playback_model, 'make_move'):
                success, message = self.playback_model.make_move(x, y)
                if success:
                    return True, f"执行移动: ({x}, {y})"
                else:
                    return False, f"移动无效: ({x}, {y}) - {message}"
            else:
                return False, "游戏模型不支持落子操作"
                
        except Exception as e:
            return False, f"执行移动时出错: {str(e)}"
