from common.observer import Subject, auto_notify
from .game_controller import GameController
from model.context_manager import LoginContextManager

class AppController(Subject):
    def __init__(self):
        super().__init__()
        # 默认页面
        self.current_page = "home"
        # 持有游戏控制器
        self.game_controller = GameController()
        # 初始化登录上下文管理器
        self._context_manager = LoginContextManager()

    def get_game_controller(self):
        return self.game_controller

    def get_login_context(self) -> str:
        """
        获取当前登录上下文
        :return: 当前登录上下文（会话ID）
        """
        return self._context_manager.get_context()

    @auto_notify
    def nav_to_game(self, game_type="gomoku", board_size=15, black_player_type="人类玩家", white_player_type="人类玩家", black_user=None, white_user=None):
        """导航到游戏页，并开始新游戏"""
        # 先启动游戏逻辑
        self.game_controller.start_game(game_type, board_size, black_player_type, white_player_type, black_user, white_user)
        # 切换页面状态
        self.current_page = "game"
        # 清除登录上下文
        self._context_manager.clear_context()
        
    @auto_notify
    def nav_to_home(self):
        """返回首页"""
        self.current_page = "home"
        # 清除登录上下文
        self._context_manager.clear_context()
        # 可以在这里做一些清理工作
    
    @auto_notify
    def nav_to_load_game(self, file_path):
        """从文件加载游戏并跳转"""
        success, msg = self.game_controller.handle_load(file_path)
        if success:
            self.current_page = "game"
            # 清除登录上下文
            self._context_manager.clear_context()
        return success, msg
    
    @auto_notify
    def nav_to_login(self, session_id=None):
        """导航到登录页面"""
        # 设置登录上下文
        self._context_manager.set_context(session_id)
        self.current_page = "login_register"
    
    @auto_notify
    def nav_to_register(self, session_id=None):
        """导航到注册页面"""
        # 设置登录上下文
        self._context_manager.set_context(session_id)
        self.current_page = "login_register"
