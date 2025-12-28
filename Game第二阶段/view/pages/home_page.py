import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from view.components.buttons_frame import ButtonsFrame
from view.components.user_info_frame import UserInfoFrame
from model.user_manager import default_user_manager

class HomePage(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.user_manager = default_user_manager
        self.setup_ui()

    def setup_ui(self):
        # 标题
        title = ttk.Label(self, text="棋类对战平台", font=(
            "微软雅黑", 24, "bold"))
        title.pack(pady=60)

        # 游戏类型选择
        game_type_frame = ttk.Frame(self)
        game_type_frame.pack(pady=10)

        ttk.Label(game_type_frame, text="游戏类型:").pack(side="left", padx=5)
        # 中文到英文游戏类型的映射
        self.game_type_map = {
            "五子棋": "gomoku",
            "围棋": "go",
            "黑白棋": "reversi"
        }
        self.game_type_var = tk.StringVar(value="五子棋")
        game_type_combobox = ttk.Combobox(
            game_type_frame,
            textvariable=self.game_type_var,
            values=list(self.game_type_map.keys()),
            state="readonly"
        )
        game_type_combobox.pack(side="left", padx=5)
        game_type_combobox.bind("<<ComboboxSelected>>", self.on_game_type_change)

        # 棋盘大小设置
        size_frame = ttk.Frame(self)
        size_frame.pack(pady=10)
        
        ttk.Label(size_frame, text="棋盘大小 (8-19):").pack(side="left", padx=5)
        self.board_size_var = tk.StringVar()
        ttk.Entry(size_frame, textvariable=self.board_size_var, width=5).pack(side="left", padx=5)
        
        # 玩家选择框架
        player_selection_frame = ttk.Frame(self)
        player_selection_frame.pack(pady=10)
        
        # 导入新的玩家选择组件
        from view.components.player_selection_frame import PlayerSelectionFrame
        
        # 内部框架，用于居中显示两个玩家选择组件
        inner_player_frame = ttk.Frame(player_selection_frame)
        inner_player_frame.pack()
        
        # 添加黑方玩家选择组件
        self.black_player_selection = PlayerSelectionFrame(
            inner_player_frame, self.app_controller, self.user_manager, "黑"
        )
        self.black_player_selection.pack(side=tk.LEFT, padx=20)
        
        # 添加白方玩家选择组件
        self.white_player_selection = PlayerSelectionFrame(
            inner_player_frame, self.app_controller, self.user_manager, "白"
        )
        self.white_player_selection.pack(side=tk.LEFT, padx=20)
        
        # 初始化棋盘大小为默认游戏类型的默认值
        self.on_game_type_change()

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
        # 居中显示按钮区域，放在玩家选择区域下方
        self.buttons_frame.pack(pady=20)
        
        # 启用所有按钮（覆盖初始禁用状态）
        self.buttons_frame.enable_all_buttons()

    def start_game(self):
        """
        开始游戏，验证棋盘大小，从下拉框获取游戏类型和玩家类型
        """
        try:
            board_size = int(self.board_size_var.get())
            if 8 <= board_size <= 19:
                # 获取用户选择的中文游戏类型，转换为英文标识符
                game_type_chinese = self.game_type_var.get()
                game_type = self.game_type_map[game_type_chinese]
                
                # 获取玩家类型选择
                black_player_type = self.black_player_selection.get_selected_player_type()
                white_player_type = self.white_player_selection.get_selected_player_type()
                
                # 获取关联用户
                black_user = self.black_player_selection.get_associated_user()
                white_user = self.white_player_selection.get_associated_user()
                
                # 调用控制器开始游戏
                self.app_controller.nav_to_game(game_type, board_size, black_player_type, white_player_type, black_user, white_user)
            else:
                messagebox.showerror("错误", "棋盘大小必须在8-19之间")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def on_game_type_change(self, event=None):
        """
        当游戏类型变化时，更新棋盘大小为对应游戏的默认值
        """
        from model.game_type_registry import GameTypeRegistry
        
        # 获取当前选择的中文游戏类型
        game_type_chinese = self.game_type_var.get()
        # 转换为英文标识
        game_type = self.game_type_map[game_type_chinese]
        
        # 获取游戏类型注册表
        registry = GameTypeRegistry()
        # 获取该游戏类型的默认棋盘大小
        default_size = registry.get_default_board_size(game_type)
        
        # 更新棋盘大小输入框的值
        self.board_size_var.set(str(default_size))
    
    def on_load_click(self):
        path = filedialog.askopenfilename(filetypes=[("存档", "*.json")])
        if path:
            self.app_controller.nav_to_load_game(path)
    
    def tkraise(self):
        """
        当页面被提升显示时调用，刷新玩家选择组件的信息
        """
        super().tkraise()
        # 刷新玩家选择组件的信息
        self.black_player_selection.refresh_user_info()
        self.white_player_selection.refresh_user_info()
