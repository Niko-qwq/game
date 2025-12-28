from model.game_factory import GameFactory
from model.player_manager import PlayerManager
from controller.command import MoveCommand, ResetCommand
from controller.command_manager import CommandManager
from controller.save.save_builder import GameSaveBuilder, AbstractGameSaveBuilder
from controller.save.game_storage import GameStorage
from controller.record_controller import RecordController
from common.observer import Subject, auto_notify
import threading
import queue


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
        self.record_controller = RecordController()  # 录像控制器，负责游戏录像和回放
        self.ai_move_queue = queue.Queue()  # AI思考结果队列
        self.ai_thread = None  # AI思考线程

    def start_game(self, game_type="gomoku", board_size=15, black_player_type="人类玩家", white_player_type="人类玩家", black_user=None, white_user=None):
        """
        开始游戏
        :param game_type: 游戏类型
        :param board_size: 棋盘大小
        :param black_player_type: 黑方玩家类型
        :param white_player_type: 白方玩家类型
        :param black_user: 黑方玩家关联的用户对象
        :param white_user: 白方玩家关联的用户对象
        """
        # 使用工厂模式创建游戏模型
        self.game_model = GameFactory.create_game(game_type, board_size)
        
        # 清空命令历史
        self.command_manager.clear()
        
        # 设置玩家
        self._set_players(black_player_type, white_player_type, black_user, white_user)
        
        return True, "游戏开始"
    
    def _set_players(self, black_player_type, white_player_type, black_user=None, white_user=None):
        """
        设置玩家类型
        :param black_player_type: 黑方玩家类型
        :param white_player_type: 白方玩家类型
        :param black_user: 黑方玩家关联的用户对象
        :param white_user: 白方玩家关联的用户对象
        """
        from model.player_factory import PlayerFactory
        
        # 获取当前游戏类型
        game_type = self.game_model.get_game_type()
        
        # 创建玩家工厂
        player_factory = PlayerFactory()
        
        # 设置黑方玩家
        try:
            black_player = player_factory.create_player(black_player_type, "black", game_type)
        except ValueError:
            # 如果玩家类型不支持，默认创建人类玩家
            black_player = player_factory.create_player("人类玩家", "black", game_type)
        
        # 设置黑方玩家关联的用户
        if black_user is not None:
            black_player.set_user(black_user)
        
        # 设置白方玩家
        try:
            white_player = player_factory.create_player(white_player_type, "white", game_type)
        except ValueError:
            # 如果玩家类型不支持，默认创建人类玩家
            white_player = player_factory.create_player("人类玩家", "white", game_type)
        
        # 设置白方玩家关联的用户
        if white_user is not None:
            white_player.set_user(white_user)
        
        # 设置玩家
        self.set_player("black", black_player)
        self.set_player("white", white_player)

    def handle_move(self, x, y):
        """
        处理落子事件（原子操作）
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
    
    def execute_human_move(self, x, y):
        """
        执行人类玩家落子
        :param x: 横坐标
        :param y: 纵坐标
        """
        if self.game_model and not self.game_model.is_game_over():
            # 获取当前玩家颜色
            current_player_color = self.game_model.get_game_status()["current_player"]
            # 获取当前玩家
            current_player = self.get_player(current_player_color)
            
            # 只有人类玩家可以执行此操作
            from model.player import HumanPlayer
            if isinstance(current_player, HumanPlayer):
                return self.handle_move(x, y)
            else:
                return False, "当前是AI玩家回合，人类玩家不能落子"
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

    def _update_player_records(self):
        """
        更新玩家战绩
        """
        if self.game_model and self.game_model.is_game_over():
            winner = self.game_model.get_winner()
            if winner:
                # 获取双方玩家
                black_player = self.get_player("black")
                white_player = self.get_player("white")
                
                # 更新战绩
                from model.user_manager import UserManager
                user_manager = UserManager()
                
                # 黑方获胜
                if winner == "black":
                    user_manager.update_player_record(black_player, True)
                    user_manager.update_player_record(white_player, False)
                # 白方获胜
                elif winner == "white":
                    user_manager.update_player_record(black_player, False)
                    user_manager.update_player_record(white_player, True)
                
                # 重新加载最新的用户数据并更新到玩家对象
                if hasattr(black_player, 'user') and black_player.user is not None:
                    # 从存储中加载最新的用户数据
                    updated_black_user = user_manager.get_user_by_username(black_player.user.get_username())
                    if updated_black_user:
                        black_player.user = updated_black_user
                
                if hasattr(white_player, 'user') and white_player.user is not None:
                    # 从存储中加载最新的用户数据
                    updated_white_user = user_manager.get_user_by_username(white_player.user.get_username())
                    if updated_white_user:
                        white_player.user = updated_white_user
    
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
            
            # 更新玩家战绩
            self._update_player_records()
            
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
            
            # 5. 加载历史记录到录像控制器，支持回放功能
            self.record_controller.load_history(save_data)

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
    
    def get_current_player_info(self):
        """
        获取当前玩家信息
        :return: dict，包含当前玩家颜色和类型信息
        """
        if not self.game_model or self.game_model.is_game_over():
            return None
        
        current_color = self.game_model.get_game_status()["current_player"]
        current_player = self.get_player(current_color)
        
        from model.player import HumanPlayer
        is_ai = not isinstance(current_player, HumanPlayer)
        
        return {
            "color": current_color,
            "is_ai": is_ai,
            "player_obj": current_player
        }
    
    def is_current_player_ai(self):
        """
        判断当前玩家是否是AI
        :return: bool
        """
        player_info = self.get_current_player_info()
        return player_info["is_ai"] if player_info else False
    
    def get_current_player_color(self):
        """
        获取当前玩家颜色
        :return: str，"black"或"white"
        """
        if not self.game_model or self.game_model.is_game_over():
            return None
        return self.game_model.get_game_status()["current_player"]
    
    def get_game_status(self):
        """
        获取当前游戏状态
        :return: dict，包含游戏状态信息
        """
        if not self.game_model:
            return None
        return self.game_model.get_game_status()
    
    def _ai_thinking(self, current_player, game_model):
        """
        AI思考的辅助方法，在子线程中执行
        
        :param current_player: 当前AI玩家
        :param game_model: 游戏模型
        """
        # 获取AI行动
        action = current_player.get_action(game_model)
        # 将结果放入队列
        self.ai_move_queue.put(action)
    
    def execute_ai_move(self):
        """
        执行当前AI玩家的落子 - 使用子线程执行AI思考
        """
        if self.game_model and not self.game_model.is_game_over():
            # 获取当前玩家颜色
            current_player_color = self.game_model.get_game_status()["current_player"]
            
            # 获取当前玩家
            current_player = self.get_player(current_player_color)
            
            # 启动AI思考线程
            self.ai_thread = threading.Thread(
                target=self._ai_thinking,
                args=(current_player, self.game_model),
                daemon=True
            )
            self.ai_thread.start()
            
            return True, "AI正在思考..."
        
        return False, "游戏已结束"
    
    def check_ai_move_result(self):
        """
        检查AI思考结果队列
        
        :return: (success, message) - 是否成功执行落子，以及相关信息
        """
        if not self.ai_move_queue.empty():
            # 获取AI思考结果
            action = self.ai_move_queue.get()
            
            if action is not None:
                x, y = action
                # 执行落子
                success, message = self.handle_move(x, y)
                
                # 如果落子失败，处理跳过落子情况
                if not success:
                    self.handle_pass()
                
                return success, message
            else:
                # AI无法落子，跳过
                return self.handle_pass()
        
        return False, ""
    
    
    # 录像与回放相关方法
    def get_record_controller(self):
        """
        获取录像控制器
        """
        return self.record_controller
    
    def step_forward(self):
        """
        前进一格（播放下一步）
        """
        return self.record_controller.step_forward()
    
    def step_backward(self):
        """
        后退一格（回退一步）
        """
        return self.record_controller.step_backward()
    
    def jump_to_step(self, step):
        """
        跳转到指定步数
        
        Args:
            step: 目标步数（从1开始）
        """
        # 转换为从0开始的索引
        return self.record_controller.jump_to_step(step - 1)
    
    def get_current_playback_step(self):
        """
        获取当前回放步数
        """
        return self.record_controller.get_current_step()
    
    def get_total_playback_steps(self):
        """
        获取总回放步数
        """
        return self.record_controller.get_total_steps()
    
    def is_playback_available(self):
        """
        检查是否可以回放
        """
        return self.record_controller.is_playback_available()
    
    def get_playback_model(self):
        """
        获取回放模型
        """
        return self.record_controller.get_playback_model()
        