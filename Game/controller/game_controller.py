from model.game_factory import GameFactory
from view.gui_view import GUIView
from .command import MoveCommand, UndoCommand, ResetCommand
from tkinter import messagebox 

class GameController:
    """游戏控制器 - 控制层"""

    def __init__(self):
        """初始化游戏控制器"""
        self.game_model = None
        self.gui_view = None
        self.command_history = []  # 命令历史记录，用于悔棋
        self.running = False

    def start_game(self, game_type="gomoku", board_size=15):
        """
        开始游戏
        :param game_type: 游戏类型
        :param board_size: 棋盘大小
        """
        # 使用简单工厂创建游戏模型
        self.game_model = GameFactory.create_game(game_type, board_size)

        # 标记游戏运行中
        self.running = True

        # 如果GUI视图不存在，创建并显示
        if not self.gui_view:
            self.gui_view = GUIView(self)
            # 设置模型，让视图观察模型
            self.gui_view.set_model(self.game_model)
            # 运行GUI主循环
            self.gui_view.run()
        else:
            # 直接设置新模型，视图会自动更新
            self.gui_view.set_model(self.game_model)

    def handle_move(self, x, y):
        """
        处理落子事件
        :param x: 横坐标
        :param y: 纵坐标
        """
        if self.game_model and not self.game_model.is_game_over():
            # 创建移动命令
            command = MoveCommand(self.game_model, x, y)
            success, message = command.execute()

            if success:
                # 将命令添加到历史记录
                self.command_history.append(command)
            else:
                # 显示错误信息
                messagebox.showerror("错误", message)

    def handle_undo(self):
        """
        处理悔棋事件
        """
        if self.game_model and not self.game_model.is_game_over():
            if self.command_history:
                # 创建悔棋命令
                command = UndoCommand(self.command_history)
                success, message = command.execute()
                return success, message
            else:
                return False, "没有可悔的棋"
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
                # 清空命令历史
                self.command_history = []

    def exit_game(self):
        """
        退出游戏
        """
        self.running = False
        if self.gui_view:
            self.gui_view.destroy()

    def handle_pass(self):
        """
        处理跳过落子事件
        """
        if self.game_model and not self.game_model.is_game_over():
            # 只有围棋游戏才能跳过落子
            if self.game_model.get_game_type() == "go":
                # 调用模型的pass_move方法
                success, message = self.game_model.pass_move()
                return success, message
            else:
                # 五子棋不支持跳过落子
                return False, "该指令仅支持围棋"

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
            
            # 正确设置游戏结束状态
            self.game_model.game_state.set_game_over(opponent)
            
            return True, (
                f"{current_player_cn}投子认负，"
                f"{opponent_cn}获胜！"
            )
        return False, "游戏已结束"

    def handle_save(self, file_path):
        """
        处理保存局面事件
        :param file_path: 保存文件路径
        :return: (是否成功, 信息)
        """
        if self.game_model:
            try:
                with open(file_path, 'w') as f:
                    # 保存游戏类型
                    f.write(f"game_type:{self.game_model.get_game_type()}\n")
                    # 保存棋盘大小
                    f.write(f"board_size:{self.game_model.get_board().size}\n")
                    # 保存当前玩家
                    f.write(
                        f"current_player:{self.game_model.get_current_player_color()}\n")
                    # 保存连续跳过次数
                    f.write(f"pass_count:{self.game_model.game_state.pass_count}\n")
                    # 保存棋盘状态
                    f.write("board:\n")
                    for y in range(self.game_model.get_board().size):
                        row = []
                        for x in range(self.game_model.get_board().size):
                            piece = self.game_model.get_board().get_piece(x, y)
                            if piece:
                                row.append(piece.color[0])  # b或w
                            else:
                                row.append('.')
                        f.write(''.join(row) + '\n')
                return True, "局面保存成功"
            except Exception as e:
                return False, f"保存失败：{str(e)}"
        return False, "游戏未开始"

    def handle_load(self, file_path):
        """
        处理读取局面事件
        :param file_path: 读取文件路径
        :return: (是否成功, 信息)
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # 解析文件内容
            game_type = None
            board_size = None
            current_player = None
            pass_count = 0
            board_data = []
            reading_board = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line == "board:":
                    reading_board = True
                    continue

                if reading_board:
                    board_data.append(line)
                else:
                    if line.startswith("game_type:"):
                        game_type = line.split(":")[1].strip()
                    elif line.startswith("board_size:"):
                        board_size = int(line.split(":")[1].strip())
                    elif line.startswith("current_player:"):
                        current_player = line.split(":")[1].strip()
                    elif line.startswith("pass_count:"):
                        pass_count = int(line.split(":")[1].strip())

            # 验证数据完整性
            if not all([game_type, board_size, current_player, board_data]):
                return False, "存档格式非法"

            # 创建新的游戏模型
            self.game_model = GameFactory.create_game(game_type, board_size)
            
            # 设置当前玩家和连续跳过次数
            self.game_model.game_state.current_player_color = current_player
            self.game_model.game_state.pass_count = pass_count

            # 恢复棋盘状态
            for y in range(board_size):
                if y >= len(board_data):
                    break
                row = board_data[y]
                for x in range(board_size):
                    if x >= len(row):
                        break
                    piece_char = row[x]
                    if piece_char == 'b':
                        self.game_model.get_board().place_piece(x, y, "black")
                    elif piece_char == 'w':
                        self.game_model.get_board().place_piece(x, y, "white")
            
            # 修正：读取新游戏后，必须清空旧的命令历史
            self.command_history = []

            # 设置新模型，视图会自动更新
            self.gui_view.set_model(self.game_model)
            return True, "局面读取成功"
        except Exception as e:
            return False, f"读取失败：{str(e)}"

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

            # 重启游戏后，清空命令历史
            self.command_history = []

            # 设置新模型，视图会自动更新
            self.gui_view.set_model(self.game_model)
            return True, "游戏重启成功"
        return False, "游戏未开始"

    def get_game_model(self):
        """获取游戏模型"""
        return self.game_model