import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from view.components.buttons_frame import ButtonsFrame

class HomePage(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.setup_ui()

    def setup_ui(self):
        # 标题
        title = ttk.Label(self, text="棋类对战平台", font=("微软雅黑", 24, "bold"))
        title.pack(pady=80)

        # 棋盘大小设置
        size_frame = ttk.Frame(self)
        size_frame.pack(pady=10)
        
        ttk.Label(size_frame, text="棋盘大小 (8-19):").pack(side="left", padx=5)
        self.board_size_var = tk.StringVar(value="15")
        ttk.Entry(size_frame, textvariable=self.board_size_var, width=5).pack(side="left", padx=5)

        # 游戏类型选择
        game_type_frame = ttk.Frame(self)
        game_type_frame.pack(pady=10)

        ttk.Label(game_type_frame, text="游戏类型:").pack(side="left", padx=5)
        # 中文到英文游戏类型的映射
        self.game_type_map = {
            "五子棋": "gomoku",
            "围棋": "go"
        }
        self.game_type_var = tk.StringVar(value="五子棋")
        game_type_combobox = ttk.Combobox(
            game_type_frame,
            textvariable=self.game_type_var,
            values=list(self.game_type_map.keys()),
            state="readonly"
        )
        game_type_combobox.pack(side="left", padx=5)

        # 按钮区 - 参考game页面实现
        btn_configs = [
            {'text': '开始游戏', 'command': self.start_game, 'name': 'start'},
            {'text': '退出', 'command': self.master.quit, 'name': 'quit'}
        ]

        # 实例化通用 Frame，设置自定义标题
        self.buttons_frame = ButtonsFrame(
            parent=self,
            config_list=btn_configs,
            title=""
        )
        self.buttons_frame.pack(fill=tk.X, side=tk.TOP, pady=20)
        
        # 启用所有按钮（覆盖初始禁用状态）
        self.buttons_frame.enable_all_buttons()

    def start_game(self):
        """
        开始游戏，验证棋盘大小，从下拉框获取游戏类型
        """
        try:
            board_size = int(self.board_size_var.get())
            if 8 <= board_size <= 19:
                # 获取用户选择的中文游戏类型，转换为英文标识符
                game_type_chinese = self.game_type_var.get()
                game_type = self.game_type_map[game_type_chinese]
                self.app_controller.nav_to_game(game_type, board_size)
            else:
                messagebox.showerror("错误", "棋盘大小必须在8-19之间")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def on_load_click(self):
        path = filedialog.askopenfilename(filetypes=[("存档", "*.json")])
        if path:
            self.app_controller.nav_to_load_game(path)
