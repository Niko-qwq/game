import tkinter as tk
from tkinter import ttk, messagebox


class ConfigFrame(ttk.LabelFrame):
    """游戏配置组件"""

    def __init__(
            self,
            parent,
            on_start_game,
            on_restart_game,
            on_show_hints_change):
        """
        初始化配置组件
        :param parent: 父窗口
        :param on_start_game: 开始游戏回调函数
        :param on_restart_game: 重启游戏回调函数
        :param on_show_hints_change: 显示提示变化回调函数
        """
        super().__init__(parent, text="游戏配置", padding="10")

        # 游戏配置数据映射
        self.game_config = {
            "五子棋": {"default_size": "15", "type_code": "gomoku"},
            "围棋": {"default_size": "19", "type_code": "go"},
            "黑白棋": {"default_size": "8", "type_code": "reversi"}
        }

        # 回调函数
        self.on_start_game = on_start_game
        self.on_restart_game = on_restart_game
        self.on_show_hints_change = on_show_hints_change

        # 初始化变量
        self.game_type_var = tk.StringVar(value="五子棋")
        self.board_size_var = tk.StringVar(value="15")
        self.show_hints_var = tk.BooleanVar(value=True)

        # 设置组件
        self.setup_widgets()

    def setup_widgets(self):
        """设置组件"""
        # 游戏类型选择
        ttk.Label(
            self,
            text="游戏类型：").grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky=tk.W)
        self.game_type_combo = ttk.Combobox(
            self, textvariable=self.game_type_var,
             values=list(self.game_config.keys()), state="readonly", width=10)
        self.game_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.game_type_combo.bind(
            "<<ComboboxSelected>>",
            self.on_game_type_change)

        # 棋盘大小输入
        ttk.Label(
            self,
            text="棋盘大小：").grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
            sticky=tk.W)
        self.board_size_entry = ttk.Entry(
            self, textvariable=self.board_size_var, width=10)
        self.board_size_entry.grid(
            row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self, text="(8-19)").grid(
            row=0, column=4, padx=5, pady=5, sticky=tk.W)

        # 开始游戏按钮
        self.start_button = ttk.Button(
            self,
            text="开始游戏",
            command=self.start_game,
            style="Accent.TButton")
        self.start_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # 重启游戏按钮
        self.restart_button = ttk.Button(
            self, text="重启游戏", command=self.restart_game)
        self.restart_button.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)

        # 显示操作提示复选框
        self.show_hints_check = ttk.Checkbutton(
            self,
            text="显示操作提示",
            variable=self.show_hints_var,
            command=self.on_show_hints_change)
        self.show_hints_check.grid(
            row=0, column=7, padx=5, pady=5, sticky=tk.W)

    def on_game_type_change(self, event):
        """处理游戏类型改变"""
        # 根据游戏类型调整棋盘大小默认值
        game_type = self.game_type_var.get()
        self.board_size_var.set(self.game_config[game_type]["default_size"])

    def start_game(self):
        """处理开始游戏按钮点击"""
        # 校验棋盘大小
        try:
            board_size = int(self.board_size_var.get())
            if not (8 <= board_size <= 19):
                messagebox.showerror("错误", "棋盘大小需为 8-19")
                return
        except ValueError:
            messagebox.showerror("错误", "棋盘大小需为数字")
            return

        # 获取游戏类型
        game_type_chinese = self.game_type_var.get()
        game_type = self.game_config[game_type_chinese]["type_code"]

        # 调用回调函数
        self.on_start_game(game_type, board_size)

    def restart_game(self):
        """处理重启游戏按钮点击"""
        if messagebox.askyesno("确认", "确定要重启游戏吗？"):
            # 调用回调函数
            self.on_restart_game()

    def get_show_hints(self):
        """获取是否显示提示"""
        return self.show_hints_var.get()
