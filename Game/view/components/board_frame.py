import tkinter as tk
from tkinter import ttk


class BoardFrame(ttk.Frame):
    """棋盘显示组件"""
    
    def __init__(self, parent, on_canvas_click):
        """
        初始化棋盘组件
        :param parent: 父窗口
        :param on_canvas_click: 画布点击回调函数
        """
        super().__init__(parent, padding="10")
        
        # 回调函数
        self.on_canvas_click = on_canvas_click
        
        # 游戏模型
        self.game_model = None
        
        # 设置组件
        self.setup_widgets()
    
    def setup_widgets(self):
        """设置组件"""
        # 创建画布用于绘制棋盘和棋子
        self.canvas = tk.Canvas(self, bg="#D2B48C", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标点击事件
        self.canvas.bind("<Button-1>", self.on_canvas_click_wrapper)
    
    def on_canvas_click_wrapper(self, event):
        """画布点击事件包装器"""
        if self.game_model and not self.game_model.is_game_over():
            # 计算点击位置对应的棋盘坐标
            x, y = self.canvas_to_board(event.x, event.y)
            if x >= 0 and y >= 0:
                # 调用回调函数
                self.on_canvas_click(x, y)
    
    def canvas_to_board(self, canvas_x, canvas_y):
        """将画布坐标转换为棋盘坐标"""
        if self.game_model:
            board = self.game_model.get_board()
            board_size = board.size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 计算格子大小
            grid_size = min(canvas_width, canvas_height) / (board_size + 1)
            
            # 计算棋盘坐标
            x = int(round((canvas_x - grid_size / 2) / grid_size))
            y = int(round((canvas_y - grid_size / 2) / grid_size))
            
            # 检查坐标是否在棋盘范围内
            if 0 <= x < board_size and 0 <= y < board_size:
                return x, y
        return -1, -1
    
    def board_to_canvas(self, x, y):
        """将棋盘坐标转换为画布坐标"""
        if self.game_model:
            board = self.game_model.get_board()
            board_size = board.size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 计算格子大小
            grid_size = min(canvas_width, canvas_height) / (board_size + 1)
            
            # 计算画布坐标
            canvas_x = (x + 1) * grid_size
            canvas_y = (y + 1) * grid_size
            
            return canvas_x, canvas_y
        return 0, 0
    
    def draw_board(self):
        """绘制棋盘"""
        if not self.game_model:
            return
        
        # 清空画布
        self.canvas.delete("all")
        
        board = self.game_model.get_board()
        board_size = board.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算格子大小
        grid_size = min(canvas_width, canvas_height) / (board_size + 1)
        
        # 绘制棋盘线
        for i in range(board_size + 1):
            # 横线
            self.canvas.create_line(
                grid_size, grid_size * i, 
                grid_size * board_size, grid_size * i,
                fill="black", width=1
            )
            # 竖线
            self.canvas.create_line(
                grid_size * i, grid_size, 
                grid_size * i, grid_size * board_size,
                fill="black", width=1
            )
        
        # 绘制星位点（仅13x13和15x15棋盘）
        if board_size in [13, 15]:
            star_positions = [3, 7, 11] if board_size == 13 else [3, 7, 11]
            for x in star_positions:
                for y in star_positions:
                    cx, cy = (x + 1) * grid_size, (y + 1) * grid_size
                    self.canvas.create_oval(
                        cx - 3, cy - 3, cx + 3, cy + 3,
                        fill="black"
                    )
        # 19x19棋盘的星位点
        elif board_size == 19:
            star_positions = [3, 9, 15]
            for x in star_positions:
                for y in star_positions:
                    cx, cy = (x + 1) * grid_size, (y + 1) * grid_size
                    self.canvas.create_oval(
                        cx - 3, cy - 3, cx + 3, cy + 3,
                        fill="black"
                    )
        
        # 绘制棋子
        self.draw_pieces()
    
    def draw_pieces(self):
        """绘制棋子"""
        if not self.game_model:
            return
        
        board = self.game_model.get_board()
        board_size = board.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        grid_size = min(canvas_width, canvas_height) / (board_size + 1)
        
        # 遍历棋盘，绘制所有棋子
        for y in range(board_size):
            for x in range(board_size):
                piece = board.get_piece(x, y)
                if piece:
                    cx, cy = (x + 1) * grid_size, (y + 1) * grid_size
                    radius = grid_size / 2 - 2
                    color = "#000000" if piece.color == "black" else "#FFFFFF"
                    
                    # 绘制棋子，带加粗边框
                    self.canvas.create_oval(
                        cx - radius, cy - radius, cx + radius, cy + radius,
                        fill=color, outline="black", width=2
                    )
    
    def update_model(self, game_model):
        """更新游戏模型"""
        self.game_model = game_model
        self.draw_board()
    
    def redraw(self):
        """重新绘制棋盘"""
        self.draw_board()
