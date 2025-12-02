import tkinter as tk
from tkinter import ttk


class ButtonsFrame(ttk.LabelFrame):
    """功能按钮组件"""
    
    def __init__(self, parent, on_undo, on_resign, on_pass, on_save, on_load):
        """
        初始化功能按钮组件
        :param parent: 父窗口
        :param on_undo: 悔棋回调函数
        :param on_resign: 投子认负回调函数
        :param on_pass: 围棋虚着回调函数
        :param on_save: 保存局面回调函数
        :param on_load: 读取局面回调函数
        """
        super().__init__(parent, text="功能按钮", padding="10")
        
        # 回调函数
        self.on_undo = on_undo
        self.on_resign = on_resign
        self.on_pass = on_pass
        self.on_save = on_save
        self.on_load = on_load
        
        # 游戏模型
        self.game_model = None
        
        # 设置组件
        self.setup_widgets()
    
    def setup_widgets(self):
        """设置组件"""
        # 悔棋按钮
        self.undo_button = ttk.Button(self, text="悔棋", command=self.undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 投子认负按钮
        self.resign_button = ttk.Button(self, text="投子认负", command=self.resign)
        self.resign_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 围棋虚着按钮（仅围棋可用）
        self.pass_button = ttk.Button(self, text="围棋虚着", command=self.pass_move)
        self.pass_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 保存局面按钮
        self.save_button = ttk.Button(self, text="保存局面", command=self.save_game)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 读取局面按钮
        self.load_button = ttk.Button(self, text="读取局面", command=self.load_game)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 初始状态：禁用部分按钮
        self.disable_all_buttons()
    
    def undo_move(self):
        """处理悔棋按钮点击"""
        self.on_undo()
    
    def resign(self):
        """处理投子认负按钮点击"""
        self.on_resign()
    
    def pass_move(self):
        """处理围棋虚着按钮点击"""
        self.on_pass()
    
    def save_game(self):
        """处理保存局面按钮点击"""
        self.on_save()
    
    def load_game(self):
        """处理读取局面按钮点击"""
        self.on_load()
    
    def update_pass_button_state(self):
        """更新虚着按钮状态"""
        if self.game_model and self.game_model.get_game_type() == "go":
            self.pass_button.config(state=tk.NORMAL)
        else:
            self.pass_button.config(state=tk.DISABLED)
    
    def enable_all_buttons(self):
        """启用所有游戏按钮"""
        self.undo_button.config(state=tk.NORMAL)
        self.resign_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.update_pass_button_state()
    
    def disable_all_buttons(self):
        """禁用所有游戏按钮"""
        self.undo_button.config(state=tk.DISABLED)
        self.resign_button.config(state=tk.DISABLED)
        self.pass_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
    
    def update_model(self, game_model):
        """更新游戏模型"""
        self.game_model = game_model
        self.update_pass_button_state()
