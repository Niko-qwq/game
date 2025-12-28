class Piece:
    """棋子类 - 享元模式的具体享元"""

    def __init__(self, color):
        """
        初始化棋子
        :param color: 棋子颜色，'black'或'white'
        """
        self.color = color

    def __str__(self):
        """返回棋子的字符串表示"""
        return '●' if self.color == 'black' else '○'


class PieceFactory:
    """棋子工厂 - 享元模式的工厂类"""
    _pieces = {}

    @classmethod
    def get_piece(cls, color):
        """
        获取棋子实例，如果不存在则创建
        :param color: 棋子颜色，'black'或'white'
        :return: 棋子实例
        """
        if color not in cls._pieces:
            cls._pieces[color] = Piece(color)
        return cls._pieces[color]

    @classmethod
    def get_piece_count(cls):
        """获取当前工厂中棋子实例的数量"""
        return len(cls._pieces)
