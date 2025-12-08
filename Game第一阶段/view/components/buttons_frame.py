import tkinter as tk
from tkinter import ttk

class ButtonsFrame(ttk.LabelFrame):
    """通用功能按钮组件"""
    
    def __init__(self, parent, config_list, title="功能按钮"):
        """
        初始化通用功能按钮组件
        :param parent: 父窗口
        :param config_list: 按钮配置列表，格式：[{'text': '按钮文本', 'command': 回调函数, 'name': '唯一标识'}, ...]
        :param title: 框架标题，默认"功能按钮"
        """
        super().__init__(parent, text=title, padding="10")
        
        # 按钮字典，用于存储按钮引用
        self.buttons = {}
        # 游戏模型
        self.game_model = None
        # 设置组件
        self.setup_buttons(config_list)
        
        # 初始状态：禁用部分按钮
        self.disable_all_buttons()
    
    def setup_buttons(self, config_list):
        """根据配置列表设置按钮"""
        # 创建一个内部容器框架，用于居中显示按钮
        btn_container = ttk.Frame(self)
        btn_container.pack(anchor=tk.CENTER, pady=5)
        
        for item in config_list:
            text = item['text']
            command = item['command']
            name = item.get('name', text)  # 使用文本作为默认名称
            
            # 创建按钮，将按钮放在容器中
            btn = ttk.Button(btn_container, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
            
            # 保存引用
            self.buttons[name] = btn
    
    def get_button(self, name):
        """获取按钮引用"""
        return self.buttons.get(name)
    
    def update_pass_button_state(self):
        """更新跳过按钮状态"""
        pass_btn = self.get_button('pass') or self.get_button('跳过')
        if pass_btn:
            if self.game_model and self.game_model.can_pass():
                pass_btn.config(state=tk.NORMAL)
            else:
                pass_btn.config(state=tk.DISABLED)
    
    def enable_all_buttons(self):
        """启用所有游戏按钮"""
        for btn in self.buttons.values():
            btn.config(state=tk.NORMAL)
        self.update_pass_button_state()
    
    def disable_all_buttons(self):
        """禁用所有游戏按钮"""
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)
    
    def set_button_state(self, name, state):
        """设置单个按钮状态"""
        btn = self.get_button(name)
        if btn:
            btn.config(state=state)
    
    def update_model(self, game_model):
        """更新游戏模型"""
        self.game_model = game_model
        self.update_pass_button_state()
