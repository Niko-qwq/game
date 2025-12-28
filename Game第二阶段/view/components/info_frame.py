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
        # 顶部控件容器
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, expand=True)
        
        # 信息提示标签
        self.info_label = ttk.Label(top_frame, text="欢迎使用棋类对战平台！", style="Status.TLabel", 
                                  wraplength=800, justify=tk.LEFT)
        self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 操作提示显示/隐藏切换按钮
        self.toggle_hint_btn = ttk.Button(top_frame, text="隐藏操作提示", command=self.toggle_hint)
        self.toggle_hint_btn.pack(side=tk.RIGHT, padx=10)
        
        # 操作提示区域
        self.hint_frame = ttk.Frame(self)
        self.hint_frame.pack(fill=tk.X, expand=True, pady=5)
        
        self.hint_text = "操作提示：\n"
        self.hint_text += "1. 点击棋盘落子\n"
        self.hint_text += "2. 悔棋：撤销上一步操作\n"
        self.hint_text += "3. 认输：结束当前游戏，对方获胜\n"
        self.hint_text += "4. 围棋虚着：跳过当前回合\n"
        self.hint_text += "5. 保存局面：将当前游戏状态保存到文件\n"
        self.hint_text += "6. 读取局面：从文件加载游戏状态\n"
        self.hint_text += "7. < 返回主菜单：回到首页\n"
        self.hint_text += "8. 重启游戏：重新开始当前游戏\n"
        
        self.hint_label = ttk.Label(self.hint_frame, text=self.hint_text, 
                                   style="Hint.TLabel", wraplength=800, justify=tk.LEFT)
        self.hint_label.pack(fill=tk.X, expand=True)
    
    def update_info(self, message):
        """更新信息提示"""
        self.info_label.config(text=message)
    
    def toggle_hint(self):
        """切换操作提示的显示/隐藏"""
        if self.hint_frame.winfo_viewable():
            # 当前可见，隐藏它
            self.hint_frame.pack_forget()
            self.toggle_hint_btn.config(text="显示操作提示")
        else:
            # 当前隐藏，显示它
            self.hint_frame.pack(fill=tk.X, expand=True, pady=5)
            self.toggle_hint_btn.config(text="隐藏操作提示")
