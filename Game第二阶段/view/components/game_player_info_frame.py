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


class PlayerProtocol(Protocol):
    """玩家对象协议"""
    def get_name(self) -> str:
        ...
    def get_user(self) -> Optional[UserProtocol]:
        ...
    def is_logged_in(self) -> bool:
        ...


class GamePlayerInfoFrame(ttk.LabelFrame):
    """游戏中玩家信息展示组件"""
    
    # UI配置常量
    UI_CONFIG = {
        "padding": "10",
        "status_label": "状态：",
        "username_label": "用户名：",
        "win_rate_label": "胜率：",
        "total_games_label": "总对局：",
        "wins_label": "胜场：",
        "ai_level_label": "AI等级：",
        "visitor_label": "游客",
        "current_player_highlight": "current_player_highlight",
        "normal_style": "normal_style"
    }
    
    def __init__(self, parent: tk.Widget, player_color: str, config: Dict[str, str] = None):
        """
        初始化游戏玩家信息组件
        :param parent: 父窗口
        :param player_color: 玩家颜色（'black'或'white'）
        :param config: 自定义配置
        """
        self.config = {**self.UI_CONFIG, **(config or {})}
        frame_text = f"{player_color}方玩家" if player_color in ['black', 'white', '黑', '白'] else "玩家信息"
        super().__init__(parent, text=frame_text, padding=self.config["padding"])
        
        # 状态变量
        self.player_color = player_color
        self.is_current_player = False
        
        # 设置组件
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """设置UI组件"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 玩家类型标签
        self.player_type_label = ttk.Label(main_frame, text="", anchor=tk.W)
        self.player_type_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 玩家名称/用户名标签
        self.name_label = ttk.Label(main_frame, text="", anchor=tk.W)
        self.name_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 玩家战绩信息标签
        self.stats_frame = ttk.Frame(main_frame)
        self.stats_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 胜率标签
        self.win_rate_label = ttk.Label(self.stats_frame, text="", anchor=tk.W)
        self.win_rate_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 总对局数标签
        self.total_games_label = ttk.Label(self.stats_frame, text="", anchor=tk.W)
        self.total_games_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 胜场数标签
        self.wins_label = ttk.Label(self.stats_frame, text="", anchor=tk.W)
        self.wins_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 额外信息展示区域
        self.extra_info_label = ttk.Label(main_frame, text="", anchor=tk.W)
        self.extra_info_label.pack(fill=tk.X, padx=5, pady=2)
        
    def update_player_info(self, player: PlayerProtocol, user: Optional[UserProtocol] = None) -> None:
        """
        更新玩家信息
        :param player: 玩家对象
        :param user: 用户对象（可选，仅当玩家是人类玩家时提供）
        """
        player_name = player.get_name()
        
        # 先检查玩家名称是否包含AI字样，判断是否是AI玩家
        if "AI" in player_name:
            # AI玩家
            self.player_type_label.config(text=f"{self.config['status_label']}AI")
            self.name_label.config(text=f"名称：{player_name}")
            self.extra_info_label.config(text="")
            # 隐藏战绩信息
            self.win_rate_label.config(text="")
            self.total_games_label.config(text="")
            self.wins_label.config(text="")
        elif player.is_logged_in() and user is not None:
            # 人类玩家且已登录
            self.player_type_label.config(text=f"{self.config['status_label']}已登录")
            self.name_label.config(text=f"{self.config['username_label']} {user.get_username()}")
            self.win_rate_label.config(text=f"{self.config['win_rate_label']} {user.get_win_rate():.2f}")
            self.total_games_label.config(text=f"{self.config['total_games_label']} {user.total_games}")
            self.wins_label.config(text=f"{self.config['wins_label']} {user.wins}")
            self.extra_info_label.config(text="")
        else:
            # 人类玩家（游客）
            self.player_type_label.config(text=f"{self.config['status_label']}游客")
            self.name_label.config(text=f"名称：{player_name}")
            # 隐藏战绩信息
            self.win_rate_label.config(text="")
            self.total_games_label.config(text="")
            self.wins_label.config(text="")
            self.extra_info_label.config(text="")
        
    def set_game_state(self, game_model) -> None:
        """
        设置游戏状态
        :param game_model: 游戏模型对象
        """
        # 根据游戏状态更新UI
        # 这里可以添加游戏状态相关的UI更新逻辑
        pass
        
    def highlight_current_player(self, is_current_player: bool) -> None:
        """
        高亮当前玩家
        :param is_current_player: 是否为当前玩家
        """
        self.is_current_player = is_current_player
        if is_current_player:
            # 高亮显示该玩家信息 - 使用文字颜色变化代替边框变化，避免尺寸改变
            self.name_label.config(foreground='#0066cc')  # 蓝色文字
            self.player_type_label.config(foreground='#0066cc')  # 蓝色文字
        else:
            # 恢复正常显示
            self.name_label.config(foreground='#000000')  # 黑色文字
            self.player_type_label.config(foreground='#000000')  # 黑色文字
    
    def style_names(self) -> list:
        """
        获取可用的样式名称列表
        """
        try:
            return self.tk.call('style', 'names')
        except Exception:
            return []
