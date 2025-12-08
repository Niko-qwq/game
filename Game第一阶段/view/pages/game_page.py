import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from common.observer import Observer
from view.components.board_frame import BoardFrame
from view.components.buttons_frame import ButtonsFrame
from view.components.info_frame import InfoFrame

class GamePage(tk.Frame, Observer):
    """游戏页面 - 负责显示游戏界面和处理游戏内交互"""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.game_controller = app_controller.get_game_controller()
        self.game_model = None
        
        self.setup_ui()

    def setup_ui(self):
        """设置界面组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 顶部工具栏
        top_bar = ttk.Frame(self.main_frame)
        top_bar.pack(fill=tk.X, pady=5)
        
        # 返回首页按钮
        ttk.Button(top_bar, text="< 返回主菜单", 
                   command=self.app_controller.nav_to_home).pack(side="left", padx=10)
        
        # 重启游戏按钮
        ttk.Button(top_bar, text="重启游戏", 
                   command=self.restart_game).pack(side="left", padx=10)
        
        # 游戏状态显示（顶部工具栏右侧）
        self.status_info = {}
        self.status_info['current_player'] = ttk.Label(top_bar, text="当前回合：黑方", 
                                                     style="Status.TLabel", justify=tk.LEFT)
        self.status_info['current_player'].pack(side="right", padx=10)
        
        # 预留拓展位置
        self.status_info['account'] = ttk.Label(top_bar, text="", 
                                             style="Status.TLabel", justify=tk.LEFT)
        self.status_info['account'].pack(side="right", padx=10)
        
        self.status_info['ai_info'] = ttk.Label(top_bar, text="", 
                                             style="Status.TLabel", justify=tk.LEFT)
        self.status_info['ai_info'].pack(side="right", padx=10)
        
        # 2. 棋盘显示区（中间核心Canvas）
        self.board_frame = BoardFrame(
            parent=self.main_frame,
            on_canvas_click=self.handle_board_click
        )
        self.board_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=5)
        
        # 4. 功能按钮区（中间偏下Frame）
        # 定义按钮数据
        btn_configs = [
            {'text': '悔棋', 'command': self.undo_move, 'name': 'undo'},
            {'text': '认输', 'command': self.resign, 'name': 'resign'},
            {'text': '跳过', 'command': self.pass_move, 'name': 'pass'},
            {'text': '保存', 'command': self.save_game, 'name': 'save'},
            {'text': '读取', 'command': self.load_game, 'name': 'load'},
        ]

        # 实例化通用 Frame
        self.buttons_frame = ButtonsFrame(
            parent=self.main_frame,
            config_list=btn_configs
        )
        self.buttons_frame.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        # 5. 信息提示区（底部Frame）
        self.info_frame = InfoFrame(parent=self.main_frame)
        self.info_frame.pack(fill=tk.X, side=tk.TOP, pady=5)

    def tkraise(self):
        """当页面被提升显示时调用，确保订阅了GameModel"""
        super().tkraise()
        self._ensure_model_subscribed()

    def _ensure_model_subscribed(self):
        """
        确保订阅了GameModel
        """
        model = self.game_controller.get_game_model()
        if model and self.game_model != model:
            # 如果模型已更改或尚未订阅，先取消旧订阅
            if self.game_model:
                self.game_model.detach(self)
            # 保存新模型并订阅
            self.game_model = model
            self.game_model.attach(self)
            # 立即更新一次
            self.update(model)

    def undo_move(self):
        """处理悔棋按钮点击"""
        success, message = self.game_controller.handle_undo()
        self.update_info(message)
    
    def resign(self):
        """处理投子认负按钮点击"""
        if messagebox.askyesno("确认", "确定要投子认负吗？"):
            success, message = self.game_controller.handle_resign()
            self.update_info(message)
    
    def pass_move(self):
        """处理跳过落子按钮点击"""
        if self.game_model:
            success, message = self.game_controller.handle_pass()
            self.update_info(message)
    
    def save_game(self):
        """处理保存局面按钮点击"""
        file_path = filedialog.asksaveasfilename(
            initialfile=f"{datetime.now().strftime('%H%M%S')}",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存局面"
        )
        
        if file_path:
            success, message = self.game_controller.handle_save(file_path)
            self.update_info(message)
    
    def load_game(self):
        """处理读取局面按钮点击"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="读取局面"
        )
        
        if file_path:
            success, message = self.game_controller.handle_load(file_path)
            self._ensure_model_subscribed()
            self.update_info(message)
    
    def restart_game(self):
        """处理重启游戏按钮点击"""
        if messagebox.askyesno("确认", "确定要重启游戏吗？当前进度将丢失。"):
            success, message = self.game_controller.restart_game()
            self._ensure_model_subscribed()
            self.update_info(message)

    def update_info(self, message):
        """更新信息提示区"""
        self.info_frame.update_info(message)

    def handle_board_click(self, x, y):
        """处理棋盘点击事件，中间层用于显示错误信息"""
        success, message = self.game_controller.handle_move(x, y)
        self.update_info(message)

    def update(self, subject, *args, **kwargs):
        """当 GameModel 通知 update 时调用"""
        if subject == self.game_model:
            # 刷新棋盘组件
            self.board_frame.update_model(subject)
            # 更新按钮状态
            self.buttons_frame.update_model(subject)
            # 启用所有按钮
            self.buttons_frame.enable_all_buttons()
            # 更新状态信息区的当前回合
            current_player = "黑方" if subject.get_current_player_color() == "black" else "白方"
            self.status_info['current_player'].config(text=f"当前回合：{current_player}")
            
            # 检查游戏是否结束
            if subject.is_game_over():
                winner = subject.get_winner()
                if winner:
                    winner_cn = "黑方" if winner == "black" else "白方"
                    self.update_info(f"游戏结束！{winner_cn}获胜！")
                    messagebox.showinfo("游戏结束", f"{winner_cn}获胜！")
                else:
                    self.update_info("游戏结束！")
