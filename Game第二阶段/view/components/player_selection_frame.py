import tkinter as tk
from tkinter import ttk
from typing import Optional, Protocol, Dict


class UserProtocol(Protocol):
    """用户对象协议"""
    def get_username(self) -> str:
        ...
    def get_win_rate(self) -> float:
        ...
    @property
    def total_games(self) -> int:
        ...
    @property
    def wins(self) -> int:
        ...


class UserManagerProtocol(Protocol):
    """用户管理器协议"""
    def get_current_user(self) -> Optional[UserProtocol]:
        ...
    def logout(self) -> None:
        ...


class AppControllerProtocol(Protocol):
    """应用控制器协议"""
    def nav_to_login(self) -> None:
        ...
    def nav_to_register(self) -> None:
        ...
    def nav_to_home(self) -> None:
        ...


class PlayerSelectionFrame(ttk.LabelFrame):
    """玩家选择组件，包含玩家类型选择和登录/注册按钮"""
    
    # UI配置常量
    UI_CONFIG = {
        "padding": "10",
        "login_text": "登录",
        "register_text": "注册",
        "logout_text": "登出",
        "player_type_label": "玩家类型：",
        "player_types": ["人类玩家", "一级AI", "二级AI", "三级AI"]
    }
    
    def __init__(self, parent: tk.Widget, app_controller: AppControllerProtocol, 
                 user_manager: UserManagerProtocol, player_color: str, config: Dict[str, str] = None):
        """
        初始化玩家选择组件
        :param parent: 父窗口
        :param app_controller: 应用控制器
        :param user_manager: 用户管理器
        :param player_color: 玩家颜色（'black'或'white'）
        :param config: 自定义配置
        """
        self.config = {**self.UI_CONFIG, **(config or {})}
        frame_text = f"{player_color}方玩家选择" if player_color in ['black', 'white', '黑', '白'] else "玩家选择"
        super().__init__(parent, text=frame_text, padding=self.config["padding"])
        
        # 依赖注入
        self.app_controller = app_controller
        self.user_manager = user_manager
        self.player_color = player_color
        
        # 状态变量
        self.player_type_var = tk.StringVar(value="人类玩家")
        self.current_user = None
        
        # 设置组件
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """设置UI组件"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, expand=True)
        
        # 玩家类型选择
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(type_frame, text=self.config["player_type_label"]).pack(side=tk.LEFT, padx=5)
        
        # 创建玩家类型下拉框
        self.player_type_combobox = ttk.Combobox(
            type_frame,
            textvariable=self.player_type_var,
            values=self.config["player_types"],
            state="readonly"
        )
        self.player_type_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.player_type_combobox.bind("<<ComboboxSelected>>", self.on_player_type_change)
        
        # 登录/注册按钮框架
        self.login_register_frame = ttk.Frame(main_frame)
        self.login_register_frame.pack(fill=tk.X, expand=True, pady=5)
        
        # 登录按钮
        self.login_btn = ttk.Button(self.login_register_frame, text=self.config["login_text"], command=self.go_to_login)
        self.login_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 注册按钮
        self.register_btn = ttk.Button(self.login_register_frame, text=self.config["register_text"], command=self.go_to_register)
        self.register_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 玩家信息展示框架
        self.player_info_frame = ttk.LabelFrame(main_frame, text="玩家信息", padding="5")
        self.player_info_frame.pack(fill=tk.X, expand=True, pady=5)
        
        # 玩家信息标签
        self.username_label = ttk.Label(self.player_info_frame, text="未登录")
        self.username_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.win_rate_label = ttk.Label(self.player_info_frame, text="胜率：0.00")
        self.win_rate_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.games_label = ttk.Label(self.player_info_frame, text="总对局：0")
        self.games_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.wins_label = ttk.Label(self.player_info_frame, text="胜场：0")
        self.wins_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 初始更新UI
        self.on_player_type_change()
        
    def on_player_type_change(self, event=None) -> None:
        """玩家类型变化时的处理"""
        player_type = self.player_type_var.get()
        
        if player_type == "人类玩家":
            # 显示登录/注册按钮
            self.login_register_frame.pack(fill=tk.X, expand=True, pady=5)
            # 更新玩家信息
            self.update_player_info()
        else:
            # 隐藏登录/注册按钮
            self.login_register_frame.pack_forget()
            # 清除玩家信息
            self.username_label.config(text="AI")
            self.win_rate_label.config(text="")
            self.games_label.config(text="")
            self.wins_label.config(text="")
        
    def update_player_info(self) -> None:
        """更新玩家信息展示"""
        self.current_user = self.user_manager.get_current_user()
        is_logged_in = bool(self.current_user)
        
        if is_logged_in:
            # 用户已登录
            assert self.current_user is not None  # 类型断言
            self.username_label.config(text=f"用户名：{self.current_user.get_username()}")
            self.win_rate_label.config(text=f"胜率：{self.current_user.get_win_rate():.2f}")
            self.games_label.config(text=f"总对局：{self.current_user.total_games}")
            self.wins_label.config(text=f"胜场：{self.current_user.wins}")
        else:
            # 用户未登录
            self.username_label.config(text="未登录")
            self.win_rate_label.config(text="")
            self.games_label.config(text="")
            self.wins_label.config(text="")
        
    def get_selected_player_type(self) -> str:
        """获取选择的玩家类型"""
        return self.player_type_var.get()
        
    def get_associated_user(self) -> Optional[UserProtocol]:
        """获取关联的用户对象"""
        player_type = self.player_type_var.get()
        if player_type == "人类玩家":
            return self.current_user
        return None
    
    def go_to_login(self) -> None:
        """跳转到登录页面"""
        # 传递会话ID，使用玩家颜色作为会话标识
        session_id = f"player_{self.player_color}" if self.player_color in ['black', 'white', '黑', '白'] else f"player_{self.player_color}"
        self.app_controller.nav_to_login(session_id)
    
    def go_to_register(self) -> None:
        """跳转到注册页面"""
        # 传递会话ID，使用玩家颜色作为会话标识
        session_id = f"player_{self.player_color}" if self.player_color in ['black', 'white', '黑', '白'] else f"player_{self.player_color}"
        self.app_controller.nav_to_register(session_id)
    
    def refresh_user_info(self) -> None:
        """刷新用户信息"""
        self.update_player_info()
    
    def update_player_info(self) -> None:
        """更新玩家信息展示"""
        # 构造会话ID
        session_id = f"player_{self.player_color}" if self.player_color in ['black', 'white', '黑', '白'] else f"player_{self.player_color}"
        # 获取对应会话的用户
        self.current_user = self.user_manager.get_current_user(session_id)
        is_logged_in = bool(self.current_user)
        
        if is_logged_in:
            # 用户已登录
            assert self.current_user is not None  # 类型断言
            self.username_label.config(text=f"用户名：{self.current_user.get_username()}")
            self.win_rate_label.config(text=f"胜率：{self.current_user.get_win_rate():.2f}")
            self.games_label.config(text=f"总对局：{self.current_user.total_games}")
            self.wins_label.config(text=f"胜场：{self.current_user.wins}")
        else:
            # 用户未登录
            self.username_label.config(text="未登录")
            self.win_rate_label.config(text="")
            self.games_label.config(text="")
            self.wins_label.config(text="")
