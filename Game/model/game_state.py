from observer import Subject


class GameState(Subject):
    """游戏状态管理类 - 负责管理游戏的核心状态"""
    
    def __init__(self, game_type="gomoku", board_size=15):
        """
        初始化游戏状态
        :param game_type: 游戏类型，"gomoku"或"go"
        :param board_size: 棋盘大小
        """
        super().__init__()  # 初始化Subject基类
        self.game_type = game_type
        self.board_size = board_size
        self.current_player_color = "black"  # 黑方先行
        self.winner = None
        self.game_over = False
        self.pass_count = 0  # 连续跳过落子的次数
    
    def set_game_over(self, winner=None):
        """
        设置游戏结束
        :param winner: 胜者颜色，"black"或"white"或None
        """
        self.game_over = True
        self.winner = winner
        self.notify()
    
    def set_current_player_color(self, color):
        """
        设置当前玩家颜色
        :param color: 玩家颜色，"black"或"white"
        """
        self.current_player_color = color
        self.notify()
    
    def toggle_current_player(self):
        """
        切换当前玩家
        """
        self.current_player_color = ("white" if self.current_player_color == "black"
                               else "black")
        self.notify()
    
    def increment_pass_count(self):
        """
        增加连续跳过次数
        """
        self.pass_count += 1
    
    def reset_pass_count(self):
        """
        重置连续跳过次数
        """
        self.pass_count = 0
    
    def get_game_status(self):
        """
        获取游戏状态
        :return: 游戏状态字典
        """
        return {
            "game_type": self.game_type,
            "current_player": self.current_player_color,
            "winner": self.winner,
            "game_over": self.game_over,
            "board_size": self.board_size,
            "pass_count": self.pass_count
        }
    
    def reset(self):
        """
        重置游戏状态
        """
        self.current_player_color = "black"
        self.winner = None
        self.game_over = False
        self.pass_count = 0
        self.notify()
