import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from observer import Observer
from view.components.config_frame import ConfigFrame
from view.components.board_frame import BoardFrame
from view.components.buttons_frame import ButtonsFrame
from view.components.info_frame import InfoFrame


class GUIView(tk.Tk, Observer):
    """图形界面视图 - MVC架构的视图层，实现观察者模式"""
    
    def __init__(self, game_controller):
        """
        初始化图形界面
        :param game_controller: 游戏控制器对象
        """
        super().__init__()
        self.game_controller = game_controller
        self.game_model = None
        
        # 设置窗口属性
        self.title("棋类对战平台")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # 设置样式
        self.setup_style()
        
        # 初始化组件
        self.setup_ui()
    
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        style.configure("Status.TLabel", font=("Arial", 10), foreground="#333333")
    
    def setup_ui(self):
        """设置界面组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 配置与控制区（顶部Frame）
        self.config_frame = ConfigFrame(
            parent=self.main_frame,
            on_start_game=self.start_game,
            on_restart_game=self.restart_game,
            on_show_hints_change=self.on_show_hints_change
        )
        self.config_frame.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        # 2. 棋盘显示区（中间核心Canvas）
        self.board_frame = BoardFrame(
            parent=self.main_frame,
            on_canvas_click=self.on_canvas_click
        )
        self.board_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=5)
        
        # 3. 功能按钮区（中间偏下Frame）
        self.buttons_frame = ButtonsFrame(
            parent=self.main_frame,
            on_undo=self.undo_move,
            on_resign=self.resign,
            on_pass=self.pass_move,
            on_save=self.save_game,
            on_load=self.load_game
        )
        self.buttons_frame.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        # 4. 信息提示区（底部Frame）
        self.info_frame = InfoFrame(parent=self.main_frame)
        self.info_frame.pack(fill=tk.X, side=tk.TOP, pady=5)
    
    def start_game(self, game_type, board_size):
        """处理开始游戏按钮点击"""
        # 调用控制器开始游戏
        self.game_controller.start_game(game_type, board_size)
        
        # 更新按钮状态
        self.buttons_frame.enable_all_buttons()
        
        # 显示初始信息
        self.update_info("游戏开始！黑方先行")
    
    def restart_game(self):
        """处理重启游戏按钮点击"""
        # 调用控制器重启游戏
        self.game_controller.restart_game()
        
        # 显示信息
        self.update_info("游戏重启！黑方先行")
    
    def on_show_hints_change(self):
        """处理显示操作提示复选框变化"""
        if self.config_frame.get_show_hints():
            # 显示提示区
            self.info_frame.pack(fill=tk.X, side=tk.TOP, pady=5)
        else:
            # 隐藏提示区
            self.info_frame.pack_forget()
    
    def on_canvas_click(self, x, y):
        """处理画布点击事件"""
        # 调用控制器处理落子
        self.game_controller.handle_move(x, y)
    
    def set_model(self, new_model):
        """切换观察的Model"""
        # 1. 如果旧模型存在，先取消订阅
        if self.game_model:
            self.game_model.detach(self)
        
        # 2. 绑定新模型
        self.game_model = new_model
        if self.game_model:
            self.game_model.attach(self)
            
            # 3. 立即刷新一次视图
            self.update_view(self.game_model)

    def update(self, subject, game_model=None, **kwargs):
        """统一的数据接收口"""
        # 更加健壮的写法：
        # 如果 subject 是 GameModel，直接用
        if isinstance(subject, type(self.game_model)) and self.game_model:
            self.update_view(subject)
        # 或者兼容其他方式传递的游戏模型
        elif 'game_model' in kwargs:
            self.update_view(kwargs['game_model'])
    
    def update_view(self, game_model):
        """更新视图"""
        self.game_model = game_model
        
        # 更新棋盘
        self.board_frame.update_model(game_model)
        
        # 更新按钮状态
        self.buttons_frame.update_model(game_model)
        
        # 更新当前玩家信息
        current_player = "黑方" if game_model.get_current_player_color() == "black" else "白方"
        self.update_info(f"当前回合：{current_player}")
        
        # 检查游戏是否结束
        if game_model.is_game_over():
            winner = game_model.get_winner()
            if winner:
                winner_cn = "黑方" if winner == "black" else "白方"
                self.update_info(f"游戏结束！{winner_cn}获胜！")
                messagebox.showinfo("游戏结束", f"{winner_cn}获胜！")
            else:
                self.update_info("游戏结束！")
    
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
        if self.game_model and self.game_model.get_game_type() == "go":
            success, message = self.game_controller.handle_pass()
            self.update_info(message)
        else:
            self.update_info("该指令仅支持围棋")
    
    def save_game(self):
        """处理保存局面按钮点击"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存局面"
        )
        
        if file_path:
            success, message = self.game_controller.handle_save(file_path)
            self.update_info(message)
    
    def load_game(self):
        """处理读取局面按钮点击"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="读取局面"
        )
        
        if file_path:
            success, message = self.game_controller.handle_load(file_path)
            self.update_info(message)
    
    def update_info(self, message):
        """更新信息提示区"""
        if self.config_frame.get_show_hints():
            self.info_frame.update_info(message)
    
    def run(self):
        """运行图形界面"""
        self.mainloop()

