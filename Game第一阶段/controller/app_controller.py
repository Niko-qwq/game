from common.observer import Subject, auto_notify
from .game_controller import GameController

class AppController(Subject):
    def __init__(self):
        super().__init__()
        # 默认页面
        self.current_page = "home"
        # 持有游戏控制器
        self.game_controller = GameController()

    def get_game_controller(self):
        return self.game_controller

    @auto_notify
    def nav_to_game(self, game_type="gomoku", board_size=15):
        """导航到游戏页，并开始新游戏"""
        # 先启动游戏逻辑
        self.game_controller.start_game(game_type, board_size)
        # 切换页面状态
        self.current_page = "game"
        
    @auto_notify
    def nav_to_home(self):
        """返回首页"""
        self.current_page = "home"
        # 可以在这里做一些清理工作
    
    @auto_notify
    def nav_to_load_game(self, file_path):
        """从文件加载游戏并跳转"""
        success, msg = self.game_controller.handle_load(file_path)
        if success:
            self.current_page = "game"
        return success, msg
