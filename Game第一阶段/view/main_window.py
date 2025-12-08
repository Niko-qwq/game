import tkinter as tk
from common.observer import Observer
from view.pages.home_page import HomePage
from view.pages.game_page import GamePage

class MainWindow(tk.Tk, Observer):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.title("Python 棋类对战平台")
        self.geometry("960x720")

        # 1. 容器 Frame (用于堆叠页面)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 2. 初始化所有页面
        self.pages = {}
        self._init_pages()

        # 3. 显示默认页面
        self.show_frame("home")

    def _init_pages(self):
        # 首页
        home = HomePage(self.container, self.app_controller)
        self.pages["home"] = home
        home.grid(row=0, column=0, sticky="nsew")

        # 游戏页
        game = GamePage(self.container, self.app_controller)
        self.pages["game"] = game
        game.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.pages[page_name]
        frame.tkraise() # 将该页面提升到最顶层显示

    def update(self, subject, *args, **kwargs):
        """监听 AppController 的页面跳转指令"""
        if subject == self.app_controller:
            target = self.app_controller.current_page
            self.show_frame(target)
