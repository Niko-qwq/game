from .player import HumanPlayer, AIPlayer


class PlayerFactory:
    """玩家工厂 - 用于根据玩家类型创建玩家对象"""
    
    def __init__(self):
        # 玩家类型映射：{玩家类型字符串: (工厂方法, 参数)}
        self.player_type_map = {
            "人类玩家": self._create_human_player,
            "一级AI": self._create_ai_player_easy,
            "二级AI": self._create_ai_player_normal,
            "三级AI": self._create_ai_player_hard
        }
    
    def create_player(self, player_type, color, game_type="gomoku"):
        """
        根据玩家类型创建玩家对象
        
        :param player_type: 玩家类型字符串（如"人类玩家", "一级AI"等）
        :param color: 玩家颜色（"black"或"white"）
        :param game_type: 游戏类型（如"gomoku", "reversi", "go"）
        :return: Player实例
        :raises ValueError: 如果玩家类型不支持
        """
        if player_type not in self.player_type_map:
            raise ValueError(f"不支持的玩家类型: {player_type}")
        
        # 获取对应的工厂方法
        create_func = self.player_type_map[player_type]
        # 调用工厂方法创建玩家
        return create_func(color, game_type)
    
    def _create_human_player(self, color, game_type="gomoku"):
        """创建人类玩家"""
        return HumanPlayer(color)
    
    def _create_ai_player_easy(self, color, game_type="gomoku"):
        """创建简单难度AI玩家"""
        return AIPlayer(color, game_type=game_type, difficulty="easy")
    
    def _create_ai_player_normal(self, color, game_type="gomoku"):
        """创建普通难度AI玩家"""
        return AIPlayer(color, game_type=game_type, difficulty="normal")
    
    def _create_ai_player_hard(self, color, game_type="gomoku"):
        """创建困难难度AI玩家"""
        return AIPlayer(color, game_type=game_type, difficulty="hard")
    
    def register_player_type(self, player_type, create_func):
        """
        注册新的玩家类型
        
        :param player_type: 玩家类型字符串
        :param create_func: 玩家创建函数，签名为 (color, game_type) -> Player
        :return: None
        """
        self.player_type_map[player_type] = create_func
    
    def get_supported_player_types(self):
        """
        获取支持的玩家类型列表
        
        :return: 玩家类型字符串列表
        """
        return list(self.player_type_map.keys())
