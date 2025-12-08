from model.game_factory import GameFactory
from model.player_manager import PlayerManager
from controller.command import MoveCommand, ResetCommand
from controller.command_manager import CommandManager
from controller.save.save_builder import GameSaveBuilder, AbstractGameSaveBuilder
from controller.save.game_storage import GameStorage
from common.observer import Subject, auto_notify


"""
game_controller.py负责一场游戏的控制层逻辑,包括游戏状态的管理、玩家交互、命令执行等，
同时也负责游戏模型与视图的交互。
内部函数有：
- start_game: 开始游戏
- handle_move: 处理玩家落子事件
- handle_undo: 处理玩家悔棋事件
- handle_pass: 处理玩家跳过落子事件
- handle_resign: 处理玩家投子认负事件
- handle_reset: 处理玩家重置游戏事件
- handle_save: 处理玩家保存游戏事件
- handle_load: 处理玩家加载游戏事件
"""
class GameController(Subject):
    """游戏控制器 - 控制层,实现Subject模式"""

    def __init__(self):
        """
        初始化游戏控制器
        """
        super().__init__()  # 初始化Subject
        self.game_model = None
        self.player_manager = PlayerManager()  # 玩家管理器，负责管理Player实例
        self.command_manager = CommandManager()  # 命令管理者，用于管理命令历史
        self.storage = GameStorage()  # 存储服务，用于读写存档

    def start_game(self, game_type="gomoku", board_size=15):
        """
        开始游戏
        :param game_type: 游戏类型
        :param board_size: 棋盘大小
        """
        # 使用工厂模式创建游戏模型
        self.game_model = GameFactory.create_game(game_type, board_size)
        
        # 清空命令历史
        self.command_manager.clear()
        
        return True, "游戏开始"

    def handle_move(self, x, y):
        """
        处理落子事件
        :param x: 横坐标
        :param y: 纵坐标
        """
        if self.game_model and not self.game_model.is_game_over():
            # 创建移动命令
            command = MoveCommand(self.game_model, x, y)
            # 委托给command_manager执行
            success, message = self.command_manager.execute_command(command)
            
            return success, message
        return False, "游戏已结束"

    def handle_undo(self):
        """
        处理悔棋事件
        """
        if self.game_model and not self.game_model.is_game_over():
            # 委托给command_manager执行撤销
            success, message = self.command_manager.undo()
            return success, message
        return False, "游戏已结束"

    def handle_reset(self):
        """
        处理重置游戏事件
        """
        if self.game_model:
            # 创建重置命令
            command = ResetCommand(self.game_model)
            success, message = command.execute()

            if success:
                # 使用command_manager清空历史记录
                self.command_manager.clear()
            return success, message
        return False, "游戏未开始"

    def handle_pass(self):
        """
        处理跳过落子事件
        """
        if self.game_model and not self.game_model.is_game_over():
            # 直接调用模型的pass_move方法，由Model层决定是否支持跳过
            success, message = self.game_model.pass_move()
            return success, message
        return False, "游戏已结束"

    def handle_resign(self):
        """
        处理投子认负事件
        """
        if self.game_model and not self.game_model.is_game_over():
            # 设置对方为获胜者
            current_player_color = self.game_model.get_current_player_color()
            opponent = "white" if current_player_color == "black" else "black"
            
            # 将英文名称转换为中文名称，用于显示
            current_player_cn = "黑方" if current_player_color == "black" else "白方"
            opponent_cn = "白方" if opponent == "white" else "黑方"
            
            # 直接设置游戏结束并指定获胜者
            self.game_model.set_game_over(opponent)
            
            return True, (
                f"{current_player_cn}投子认负，"
                f"{opponent_cn}获胜！"
            )
        return False, "游戏已结束"

    def handle_save(self, file_path, builder: AbstractGameSaveBuilder = None):
        """
        处理保存 - 使用建造者模式 (Director 逻辑)
        
        Args:
            file_path: 保存文件路径
            builder: 可选的建造者实例，默认为 GameSaveBuilder
        """
        if not self.game_model:
            return False, "游戏未开始"
        
        try:
            # 1. 初始化建造者
            save_builder = builder or GameSaveBuilder()
            
            # 2. 指挥构建过程
            # 获取 Model 的快照
            memento = self.game_model.create_memento()
            
            # 链式调用构建各个部分
            save_data = (save_builder 
                .with_memento(memento) 
                .with_history(self.command_manager) # 将 CommandManager 传进去提取历史
                .with_metadata()
                .build())
            
            # 3. 交给存储服务写入硬盘
            return self.storage.save_to_file(save_data, file_path)
            
        except Exception as e:
            return False, f"保存过程出错: {str(e)}"

    def handle_load(self, file_path):
        """
        处理读取
        """
        # 1. 存储服务读取数据
        save_data, message = self.storage.load_from_file(file_path)
        
        if not save_data:
            return False, message

        try:
            # 2. 使用 Factory 创建新模型
            memento = save_data.memento
            self.game_model = GameFactory.create_game(
                memento.get_game_type(),
                memento.get_board().size
            )
            
            # 3. 恢复状态
            self.game_model.restore_memento(memento)
            
            # 4. 处理历史记录 
            self.command_manager.clear()
            
            return True, "读取成功"
        except Exception as e:
            return False, f"恢复游戏失败: {str(e)}"

    def restart_game(self):
        """
        重启游戏
        """
        if self.game_model:
            # 获取当前游戏类型和棋盘大小
            game_type = self.game_model.get_game_type()
            board_size = self.game_model.get_board().size

            # 创建新的游戏模型
            self.game_model = GameFactory.create_game(game_type, board_size)

            # 重启游戏后，清空命令管理器的历史记录
            self.command_manager.clear()
            
            return True, "游戏重启成功"
        return False, "游戏未开始"

    def get_game_model(self):
        """获取游戏模型"""
        return self.game_model
    
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
    
