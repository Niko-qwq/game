import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from view.components.board_frame import BoardFrame
from controller.record_controller import RecordController

class PlaybackWindow(tk.Toplevel):
    """
    回放窗口 - 负责显示游戏回放内容
    """
    
    def __init__(self, parent, app_controller):
        """
        初始化回放窗口
        
        Args:
            parent: 父窗口
            app_controller: 应用控制器
        """
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.game_controller = app_controller.get_game_controller()
        self.record_controller = self.game_controller.get_record_controller()
        
        self.title("游戏回放")
        self.geometry("480x480")
        self.resizable(True, True)
        
        self.setup_ui()
        self.current_file = None
    
    def setup_ui(self):
        """
        设置回放窗口的UI组件
        """
        # 创建主框架
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 顶部工具栏
        top_bar = ttk.Frame(self.main_frame)
        top_bar.pack(fill=tk.X, pady=5)
        
        # 加载存档按钮
        ttk.Button(top_bar, text="加载存档", 
                   command=self.load_save_file).pack(side="left", padx=10)
        
        # 关闭按钮
        ttk.Button(top_bar, text="关闭窗口", 
                   command=self.destroy).pack(side="right", padx=10)
        
        # 2. 回放状态显示
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        # 步数显示
        self.step_var = tk.StringVar(value="当前步数: 0 / 0")
        ttk.Label(status_frame, textvariable=self.step_var, 
                 font=("微软雅黑", 12)).pack(side="left", padx=10)
        
        # 执行步骤显示
        self.info_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.info_var, 
                 font=("微软雅黑", 10), foreground="blue").pack(side="left", padx=10)
        
        # 3. 棋盘显示区
        self.board_frame = BoardFrame(
            parent=self.main_frame,
            on_canvas_click=lambda x, y: None  # 空的回调函数，不执行任何操作
        )
        self.board_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=5)
        
        # 4. 回放控制按钮区
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, side=tk.TOP, pady=10)
        
        # 跳转控制
        ttk.Label(control_frame, text="跳转到步数:").pack(side="left", padx=10)
        
        self.jump_step_var = tk.IntVar(value=1)
        self.jump_entry = ttk.Entry(control_frame, textvariable=self.jump_step_var, 
                                   width=10, justify=tk.CENTER)
        self.jump_entry.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="跳转", 
                  command=self.jump_to_step).pack(side="left", padx=5, pady=5)
        
        # 回放控制按钮（放在跳转控制右边）
        # 添加一个分隔符
        ttk.Separator(control_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # 定义控制按钮
        control_btns = [
            {'text': '上一步', 'command': self.step_backward},
            {'text': '下一步', 'command': self.step_forward},
        ]
        
        for btn_config in control_btns:
            ttk.Button(control_frame, text=btn_config['text'], 
                      command=btn_config['command']).pack(side="left", padx=5, pady=5)
        

    
    def load_save_file(self):
        """
        加载存档文件
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="选择要回放的存档"
        )
        
        if file_path:
            self._load_save_file_internal(file_path)
    
    def load_save_file_with_path(self, file_path):
        """
        直接加载指定路径的存档文件
        
        Args:
            file_path: 存档文件路径
        """
        self._load_save_file_internal(file_path)
    
    def _load_save_file_internal(self, file_path):
        """
        内部方法：加载指定路径的存档文件
        
        Args:
            file_path: 存档文件路径
        """
        # 注意：这里不使用game_controller的handle_load方法，
        # 因为它会修改当前游戏状态，我们需要独立的回放
        from controller.save.game_storage import GameStorage
        storage = GameStorage()
        save_data, message = storage.load_from_file(file_path)
        
        if save_data:
            # 使用record_controller加载历史记录
            success, msg = self.record_controller.load_history(save_data)
            if success:
                self.current_file = file_path
                self.update_playback_info()
                self.update_board()
                # 重置执行步骤显示
                self.info_var.set("")
            else:
                messagebox.showerror("错误", f"加载历史记录失败: {msg}")
        else:
            messagebox.showerror("错误", f"读取存档失败: {message}")
    
    def step_forward(self):
        """
        前进一格（播放下一步）
        """
        if not self.record_controller.is_playback_available():
            messagebox.showwarning("提示", "请先加载存档")
            return
        
        success, message = self.record_controller.step_forward()
        if success:
            self.update_playback_info()
            self.update_board()
            if message.startswith("执行移动: "):
                self.info_var.set(message[6:])
            else:
                self.info_var.set(message)
        else:
            self.info_var.set(f"播放失败: {message}")
    
    def step_backward(self):
        """
        后退一格（回退一步）
        """
        if not self.record_controller.is_playback_available():
            messagebox.showwarning("提示", "请先加载存档")
            return
        
        success, message = self.record_controller.step_backward()
        if success:
            self.update_playback_info()
            self.update_board()
            self.info_var.set("回退一步")
        else:
            self.info_var.set(f"回退失败: {message}")
    
    def jump_to_step(self):
        """
        跳转到指定步数
        """
        if not self.record_controller.is_playback_available():
            messagebox.showwarning("提示", "请先加载存档")
            return
        
        try:
            target_step = self.jump_step_var.get() - 1  # 转换为从0开始的索引
            total_steps = self.record_controller.get_total_steps()
            
            if 0 <= target_step < total_steps:
                success, message = self.record_controller.jump_to_step(target_step)
                if success:
                    self.update_playback_info()
                    self.update_board()
                    if message.startswith("已跳转到第"):
                        self.info_var.set(message)
                    elif message.startswith("执行移动: "):
                        self.info_var.set(message[6:])
                    else:
                        self.info_var.set(message)
                else:
                    self.info_var.set(f"跳转失败: {message}")
            else:
                messagebox.showwarning("提示", f"请输入1-{total_steps}之间的步数")
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字")
    

    
    def update_playback_info(self):
        """
        更新回放信息（步数等）
        """
        current_step = self.record_controller.get_current_step()
        total_steps = self.record_controller.get_total_steps()
        self.step_var.set(f"当前步数: {current_step} / {total_steps}")
        self.jump_step_var.set(current_step)
    
    def update_board(self):
        """
        更新棋盘显示
        """
        playback_model = self.record_controller.get_playback_model()
        if playback_model:
            self.board_frame.update_model(playback_model)
            # 根据棋盘大小动态调整窗口大小
            self.adjust_window_size()
    
    def adjust_window_size(self):
        """
        根据棋盘大小调整窗口大小
        """
        playback_model = self.record_controller.get_playback_model()
        if playback_model:
            board = playback_model.get_board()
            board_size = board.size
            
            # 计算棋盘需要的画布大小（每个格子30像素，边缘留出一个格子的空间）
            grid_size = 30
            canvas_size = (board_size + 1) * grid_size
            
            # 计算窗口需要的总大小（画布大小 + 其他组件的高度）
            # 其他组件包括：顶部工具栏(约50px)、状态显示(约30px)、控制按钮(约80px)、跳转控制(约50px)、信息提示(约30px)
            other_components_height = 50 + 30 + 80 + 50 + 30
            
            # 计算窗口的总宽度和高度
            window_width = max(canvas_size + 40, 600)  # 40px是左右边距
            window_height = canvas_size + other_components_height + 40  # 40px是上下边距
            
            # 调整窗口大小
            self.geometry(f"{window_width}x{window_height}")
    
    def destroy(self):
        """
        关闭窗口时的清理工作
        """
        super().destroy()
