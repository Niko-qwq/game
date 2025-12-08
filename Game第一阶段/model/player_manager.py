from .player import HumanPlayer


class PlayerManager:
    """玩家管理器 - 负责管理玩家对象"""
    
    def __init__(self):
        """
        初始化玩家管理器
        """
        # 初始化玩家字典
        self.players = {
            "black": HumanPlayer("black"),
            "white": HumanPlayer("white")
        }
    
    def set_player(self, color, player):
        """
        设置玩家
        :param color: 玩家颜色，"black"或"white"
        :param player: 玩家对象
        """
        self.players[color] = player
    
    def get_player(self, color):
        """
        获取玩家
        :param color: 玩家颜色，"black"或"white"
        :return: 玩家对象
        """
        return self.players[color]
    
    def get_current_player(self, current_player_color):
        """
        获取当前玩家对象
        :param current_player_color: 当前玩家颜色，"black"或"white"
        :return: 当前玩家对象
        """
        return self.players[current_player_color]
    
    def reset_players(self):
        """
        重置玩家，恢复为默认的人类玩家
        """
        self.players = {
            "black": HumanPlayer("black"),
            "white": HumanPlayer("white")
        }
