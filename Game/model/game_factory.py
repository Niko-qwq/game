from .game_model import GameModel


class GameFactory:
    """游戏工厂 - 简单工厂模式的工厂类"""

    @staticmethod
    def create_game(game_type, board_size=15):
        """
        创建游戏实例
        :param game_type: 游戏类型，"gomoku"或"go"
        :param board_size: 棋盘大小
        :return: 游戏模型对象
        """
        if game_type == "gomoku":
            return GameModel(game_type="gomoku", board_size=board_size)
        elif game_type == "go":
            return GameModel(game_type="go", board_size=board_size)
        else:
            raise ValueError(f"不支持的游戏类型: {game_type}")

    @staticmethod
    def get_supported_games():
        """
        获取支持的游戏列表
        :return: 支持的游戏列表
        """
        return ["gomoku", "go"]
