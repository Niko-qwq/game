from .piece import PieceFactory


class Board:
    """棋盘类 - 负责维护棋子的位置信息"""

    def __init__(self, size=15):
        """
        初始化棋盘
        :param size: 棋盘大小，默认为15x15
        """
        self.size = size
        # 棋盘数据结构：二维列表，存储棋子对象或None
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.piece_factory = PieceFactory()

    def place_piece(self, x, y, color):
        """
        在指定位置放置棋子
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 棋子颜色
        :return: 是否放置成功
        """
        if (0 <= x < self.size and 0 <= y < self.size
                and self.grid[y][x] is None):
            piece = self.piece_factory.get_piece(color)
            self.grid[y][x] = piece
            return True
        return False

    def remove_piece(self, x, y):
        """
        移除指定位置的棋子
        :param x: 横坐标
        :param y: 纵坐标
        :return: 是否移除成功
        """
        if (0 <= x < self.size and 0 <= y < self.size
                and self.grid[y][x] is not None):
            self.grid[y][x] = None
            return True
        return False

    def get_piece(self, x, y):
        """
        获取指定位置的棋子
        :param x: 横坐标
        :param y: 纵坐标
        :return: 棋子对象或None
        """
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x]
        return None

    def is_empty(self, x, y):
        """
        检查指定位置是否为空
        :param x: 横坐标
        :param y: 纵坐标
        :return: 是否为空
        """
        return self.get_piece(x, y) is None

    def clear(self):
        """清空棋盘"""
        self.grid = [[None for _ in range(self.size)]
                     for _ in range(self.size)]

    def clone(self):
        """
        深拷贝棋盘
        :return: 新的棋盘实例
        """
        new_board = Board(self.size)
        for y in range(self.size):
            for x in range(self.size):
                piece = self.grid[y][x]
                if piece is not None:
                    new_board.grid[y][x] = self.piece_factory.get_piece(
                        piece.color)
        return new_board
