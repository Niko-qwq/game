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
        
        # 2. 游戏玩家信息和棋盘区
        game_area_frame = ttk.Frame(self.main_frame)
        game_area_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧：黑方玩家信息
        from view.components.game_player_info_frame import GamePlayerInfoFrame
        self.black_player_info = GamePlayerInfoFrame(game_area_frame, "黑")
        self.black_player_info.pack(side="left", padx=10, fill=tk.Y)
        
        # 中间：棋盘显示区（核心Canvas）
        self.board_frame = BoardFrame(
            parent=game_area_frame,
            on_canvas_click=self.handle_board_click
        )
        self.board_frame.pack(fill=tk.BOTH, expand=True, side="left", pady=5)
        
        # 右侧：白方玩家信息
        self.white_player_info = GamePlayerInfoFrame(game_area_frame, "白")
        self.white_player_info.pack(side="right", padx=10, fill=tk.Y)
        
        # 4. 功能按钮区（中间偏下Frame）
        # 定义按钮数据
        btn_configs = [
            {'text': '悔棋', 'command': self.undo_move, 'name': 'undo'},
            {'text': '认输', 'command': self.resign, 'name': 'resign'},
            {'text': '跳过', 'command': self.pass_move, 'name': 'pass'},
            {'text': '保存', 'command': self.save_game, 'name': 'save'},
            {'text': '读取', 'command': self.load_game, 'name': 'load'},
            {'text': '回放', 'command': self.open_playback_window, 'name': 'playback'},
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
        success, message = self.game_controller.execute_human_move(x, y)
        self.update_info(message)

    def open_playback_window(self):
        """
        打开游戏回放窗口
        """
        from tkinter import filedialog
        from view.pages.playback_window import PlaybackWindow
        
        # 先选择存档文件
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="选择要回放的存档"
        )
        
        if file_path:
            # 打开回放窗口
            playback_window = PlaybackWindow(self, self.app_controller)
            # 加载选定的存档文件
            playback_window.load_save_file_with_path(file_path)
    
    def update(self, subject, *args, **kwargs):
        """当 GameModel 通知 update 时调用"""
        if subject == self.game_model:
            # 1. 先获取所有需要的游戏状态，减少多次调用模型方法
            current_player_color = subject.get_current_player_color()
            current_player = "黑方" if current_player_color == "black" else "白方"
            is_game_over = subject.is_game_over()
            is_ai_turn = not is_game_over and self.game_controller.is_current_player_ai()
            
            # 2. 更新文字信息，避免频繁的UI重绘
            self.status_info['current_player'].config(text=f"当前回合：{current_player}")
            
            # 3. 更新AI状态显示
            if is_ai_turn:
                self.status_info['ai_info'].config(text="AI正在思考...", foreground="red")
            else:
                self.status_info['ai_info'].config(text="", foreground="black")
            
            # 4. 更新玩家信息
            self._update_player_info()
            
            # 4. 高亮当前玩家
            self.black_player_info.highlight_current_player(current_player_color == "black")
            self.white_player_info.highlight_current_player(current_player_color == "white")
            
            # 5. 刷新棋盘组件 - 这是最耗时的操作，放在前面
            self.board_frame.update_model(subject)
            
            # 6. 批量更新按钮状态，避免多次切换
            self.buttons_frame.update_model(subject)
            if is_ai_turn:
                # AI回合：先禁用所有按钮，再启用允许的按钮
                self.buttons_frame.disable_all_buttons()
            else:
                # 人类回合：启用所有按钮
                self.buttons_frame.enable_all_buttons()
                
            # 7. 检查游戏是否结束
            if is_game_over:
                winner = subject.get_winner()
                if winner:
                    winner_cn = "黑方" if winner == "black" else "白方"
                    self.update_info(f"游戏结束！{winner_cn}获胜！")
                    messagebox.showinfo("游戏结束", f"{winner_cn}获胜！")
                    # 更新玩家战绩
                    self.game_controller._update_player_records()
                    # 重新加载用户数据并更新UI
                    self._update_player_info()
                else:
                    self.update_info("游戏结束！")
                # 清除AI状态显示
                self.status_info['ai_info'].config(text="", foreground="black")
            elif is_ai_turn:
                # 使用after(800)延迟执行AI行动，让AI下棋速度变慢，便于观察
                # 这可以避免递归调用和视图更新混乱，同时让用户看清每一步
                self.after(2000, self._execute_ai_move)
    
    def _update_player_info(self):
        """
        更新玩家信息
        """
        # 获取黑方和白方玩家
        black_player = self.game_controller.get_player("black")
        white_player = self.game_controller.get_player("white")
        
        # 更新黑方玩家信息
        self.black_player_info.update_player_info(black_player, black_player.get_user())
        
        # 更新白方玩家信息
        self.white_player_info.update_player_info(white_player, white_player.get_user())
    
    def _check_ai_result(self):
        """
        检查AI思考结果的轮询方法
        """
        # 检查游戏是否已结束
        if not self.game_model or self.game_model.is_game_over():
            return
        
        # 检查当前玩家是否仍然是AI
        if self.game_controller.is_current_player_ai():
            # 检查AI思考结果
            success, message = self.game_controller.check_ai_move_result()
            
            if success:
                # AI落子成功，更新信息
                self.update_info(message)
            else:
                # AI仍在思考，继续轮询
                self.after(100, self._check_ai_result)
    
    def _execute_ai_move(self):
        """
        执行AI行动 - 启动AI思考线程并开始轮询结果
        """
        # 再次检查游戏是否结束，避免在延迟期间游戏已结束
        if not self.game_model or self.game_model.is_game_over():
            return
        
        # 检查当前玩家是否仍然是AI
        if self.game_controller.is_current_player_ai():
            success, message = self.game_controller.execute_ai_move()
            self.update_info(message)
            
            # 开始轮询AI思考结果
            self.after(100, self._check_ai_result)
