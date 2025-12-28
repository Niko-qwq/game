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


class UserInfoFrame(ttk.LabelFrame):
    """用户信息展示组件"""
    
    # UI配置常量
    UI_CONFIG = {
        "frame_text": "用户信息",
        "padding": "10",
        "login_text": "登录",
        "register_text": "注册",
        "logout_text": "登出",
        "not_logged_in_text": "未登录",
        "win_rate_format": "胜率：{:.2f}",
        "total_games_format": "总对局：{}",
        "wins_format": "胜场：{}",
        "username_format": "用户名：{}"
    }
    
    def __init__(self, parent: tk.Widget, app_controller: AppControllerProtocol, 
                 user_manager: UserManagerProtocol, config: Dict[str, str] = None):
        """
        初始化用户信息组件
        :param parent: 父窗口
        :param app_controller: 应用控制器
        :param user_manager: 用户管理器
        :param config: 自定义配置
        """
        self.config = {**self.UI_CONFIG, **(config or {})}
        super().__init__(parent, text=self.config["frame_text"], padding=self.config["padding"])
        
        # 依赖注入
        self.app_controller = app_controller
        self.user_manager = user_manager
        
        # 设置组件
        self.setup_widgets()
        
        # 初始更新用户信息
        self.update_user_info()
    
    def setup_widgets(self) -> None:
        """设置组件"""
        # 顶部控件容器
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, expand=True)
        
        # 左侧：用户信息显示
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 用户名标签
        self.username_label = ttk.Label(info_frame, text=self.config["not_logged_in_text"], style="Status.TLabel")
        self.username_label.pack(side=tk.LEFT, padx=5)
        
        # 胜率标签
        self.win_rate_label = ttk.Label(info_frame, text=self.config["win_rate_format"].format(0.00), style="Status.TLabel")
        self.win_rate_label.pack(side=tk.LEFT, padx=5)
        
        # 总对局数标签
        self.games_label = ttk.Label(info_frame, text=self.config["total_games_format"].format(0), style="Status.TLabel")
        self.games_label.pack(side=tk.LEFT, padx=5)
        
        # 胜场数标签
        self.wins_label = ttk.Label(info_frame, text=self.config["wins_format"].format(0), style="Status.TLabel")
        self.wins_label.pack(side=tk.LEFT, padx=5)
        
        # 右侧：登录/登出按钮
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side=tk.RIGHT, padx=10)
        
        # 登录按钮
        self.login_btn = ttk.Button(action_frame, text=self.config["login_text"], command=self.go_to_login)
        self.login_btn.pack(side=tk.RIGHT, padx=5)
        
        # 注册按钮
        self.register_btn = ttk.Button(action_frame, text=self.config["register_text"], command=self.go_to_register)
        self.register_btn.pack(side=tk.RIGHT, padx=5)
        
        # 登出按钮（初始隐藏）
        self.logout_btn = ttk.Button(action_frame, text=self.config["logout_text"], command=self.logout)
    
    def update_user_info(self) -> None:
        """更新用户信息显示"""
        current_user = self.user_manager.get_current_user()
        is_logged_in = bool(current_user)
        
        if is_logged_in:
            # 用户已登录
            assert current_user is not None  # 类型断言
            self.username_label.config(text=self.config["username_format"].format(current_user.get_username()))
            self.win_rate_label.config(text=self.config["win_rate_format"].format(current_user.get_win_rate()))
            self.games_label.config(text=self.config["total_games_format"].format(current_user.total_games))
            self.wins_label.config(text=self.config["wins_format"].format(current_user.wins))
        else:
            # 用户未登录
            self.username_label.config(text=self.config["not_logged_in_text"])
            self.win_rate_label.config(text=self.config["win_rate_format"].format(0.00))
            self.games_label.config(text=self.config["total_games_format"].format(0))
            self.wins_label.config(text=self.config["wins_format"].format(0))
        
        # 更新按钮状态
        self._update_button_visibility(is_logged_in)
    
    def _update_button_visibility(self, is_logged_in: bool) -> None:
        """更新按钮可见性"""
        # 登录/注册按钮
        if is_logged_in:
            self.login_btn.pack_forget()
            self.register_btn.pack_forget()
        else:
            self.login_btn.pack(side=tk.RIGHT, padx=5)
            self.register_btn.pack(side=tk.RIGHT, padx=5)
        
        # 登出按钮
        if is_logged_in:
            self.logout_btn.pack(side=tk.RIGHT, padx=5)
        else:
            self.logout_btn.pack_forget()
    
    def go_to_login(self) -> None:
        """跳转到登录页面"""
        self.app_controller.nav_to_login()
    
    def go_to_register(self) -> None:
        """跳转到注册页面"""
        self.app_controller.nav_to_register()
    
    def logout(self) -> None:
        """处理用户登出"""
        self.user_manager.logout()
        self.update_user_info()
        self.app_controller.nav_to_home()
