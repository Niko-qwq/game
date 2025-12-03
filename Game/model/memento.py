
class GameMemento:
    """游戏备忘录 - 备忘录模式的备忘录类"""
    def __init__(self, board, current_player, game_type):
        """
        初始化备忘录
        :param board: 棋盘对象
        :param current_player: 当前玩家颜色
        :param game_type: 游戏类型
        """
        # 深拷贝棋盘状态
        self.board = board.clone()
        self.current_player = current_player
        self.game_type = game_type
    
    def get_board(self):
        """获取棋盘状态"""
        return self.board
    
    def get_current_player(self):
        """获取当前玩家"""
        return self.current_player
    
    def get_game_type(self):
        """获取游戏类型"""
        return self.game_type
