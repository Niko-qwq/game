import tkinter as tk
from tkinter import ttk


class InfoFrame(ttk.LabelFrame):
    """信息提示组件"""
    
    def __init__(self, parent):
        """
        初始化信息提示组件
        :param parent: 父窗口
        """
        super().__init__(parent, text="信息提示", padding="10")
        
        # 设置组件
        self.setup_widgets()
    
    def setup_widgets(self):
        """设置组件"""
        # 信息提示标签
        self.info_label = ttk.Label(self, text="欢迎使用棋类对战平台！", style="Status.TLabel", 
                                  wraplength=800, justify=tk.LEFT)
        self.info_label.pack(fill=tk.X, expand=True)
    
    def update_info(self, message):
        """更新信息提示"""
        self.info_label.config(text=message)
