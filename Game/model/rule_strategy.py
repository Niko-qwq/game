from abc import ABC, abstractmethod

class GameStrategy(ABC):
    """
    抽象游戏策略基类
    定义了游戏生命周期中的所有差异化行为
    """

    @abstractmethod
    def initialize_board(self, board):
        """初始化棋盘（例如黑白棋的开局4子）"""
        pass

    @abstractmethod
    def check_valid_move(self, board, x, y, current_color):
        """检查落子是否合法"""
        pass

    @abstractmethod
    def post_move_processing(self, board, x, y, current_color):
        """
        落子后的处理逻辑
        - 五子棋：什么都不做
        - 黑白棋：翻转对方棋子
        - 围棋：提子、判断自杀
        :param board: 棋盘对象
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 棋子颜色
        :return: (是否合法, 错误信息)
        """
        pass

    @abstractmethod
    def check_winner(self, board, last_move):
        """
        检查胜负
        :param board: 棋盘对象
        :param last_move: 最后一步落子位置 (x, y)
        :return: (是否有胜者, 胜者颜色或None)
        """
        pass
    
    @abstractmethod
    def can_pass(self):
        """是否允许手动跳过回合（只有围棋是True）"""
        pass
    
    @abstractmethod
    def get_game_name(self):
        """
        获取游戏名称
        :return: 游戏名称
        """
        pass


class GomokuRuleStrategy(GameStrategy):
    """五子棋规则策略 - 策略模式的具体策略"""
    
    def initialize_board(self, board):
        """五子棋初始化棋盘（空棋盘）"""
        pass
    
    def check_valid_move(self, board, x, y, color):
        """检查五子棋落子是否合法"""
        if not (0 <= x < board.size and 0 <= y < board.size):
            return False, "位置超出棋盘范围"
        if not board.is_empty(x, y):
            return False, "该位置已有棋子"
        return True, ""
    
    def post_move_processing(self, board, x, y, current_color):
        """五子棋落子后无需特殊处理"""
        return True, ""
    
    def check_winner(self, board, last_move=None):
        """检查五子棋胜负"""
        if last_move is None:
            return False, None
        
        x, y = last_move
        piece = board.get_piece(x, y)
        if piece is None:
            return False, None
        
        color = piece.color
        directions = [
            (0, 1),   # 水平方向
            (1, 0),   # 垂直方向
            (1, 1),   # 对角线方向
            (1, -1)   # 反对角线方向
        ]
        
        for dx, dy in directions:
            count = 1
            # 向一个方向延伸
            for step in range(1, 5):
                nx = x + dx * step
                ny = y + dy * step
                if 0 <= nx < board.size and 0 <= ny < board.size:
                    neighbor = board.get_piece(nx, ny)
                    if neighbor and neighbor.color == color:
                        count += 1
                    else:
                        break
                else:
                    break
            
            # 向相反方向延伸
            for step in range(1, 5):
                nx = x - dx * step
                ny = y - dy * step
                if 0 <= nx < board.size and 0 <= ny < board.size:
                    neighbor = board.get_piece(nx, ny)
                    if neighbor and neighbor.color == color:
                        count += 1
                    else:
                        break
                else:
                    break
            
            if count >= 5:
                return True, color
        
        return False, None
    
    def can_pass(self):
        """五子棋不允许手动跳过"""
        return False
    
    def get_game_name(self):
        """获取游戏名称"""
        return "五子棋"


class GoRuleStrategy(GameStrategy):
    """围棋规则策略 - 策略模式的具体策略"""
    
    def initialize_board(self, board):
        """围棋初始化棋盘（空棋盘）"""
        pass
    
    def post_move_processing(self, board, x, y, current_color):
        """围棋落子后处理：移除无气棋子，检查自杀"""
        # 移除对方无气棋子
        self.remove_dead_stones(board, current_color)

        # 检查己方刚落的棋子是否还有气（防止自杀）
        if not self.has_liberties(board, x, y):
            # 移除刚落的棋子（自杀不允许）
            return False, "落子后无气（自杀）"
        return True, ""
    
    def can_pass(self):
        """围棋允许手动跳过"""
        return True
    
    def has_liberties(self, board, x, y, checked=None):
        """
        检查棋子是否有气
        :param board: 棋盘对象
        :param x: 横坐标
        :param y: 纵坐标
        :param checked: 已检查的位置集合
        :return: 是否有气
        """
        if checked is None:
            checked = set()
        
        # 获取当前位置的棋子
        current_piece = board.get_piece(x, y)
        if current_piece is None:
            return False
        
        color = current_piece.color
        
        # 如果已经检查过这个位置，返回False
        if (x, y) in checked:
            return False
        checked.add((x, y))
        
        # 检查相邻四个方向
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 检查边界
            if 0 <= nx < board.size and 0 <= ny < board.size:
                neighbor_piece = board.get_piece(nx, ny)
                # 如果相邻位置为空，说明有气
                if neighbor_piece is None:
                    return True
                # 如果相邻位置是同色棋子，递归检查
                elif neighbor_piece.color == color:
                    if self.has_liberties(board, nx, ny, checked):
                        return True
        
        # 四个方向都没有气
        return False
    
    def remove_dead_stones(self, board, player_color):
        """
        移除无气棋子
        :param board: 棋盘对象
        :param player_color: 当前玩家颜色，用于区分对方棋子
        :return: 移除的棋子数量
        """
        to_remove = []
        
        # 遍历棋盘，找出所有无气的对方棋子
        for y in range(board.size):
            for x in range(board.size):
                piece = board.get_piece(x, y)
                if piece is not None and piece.color != player_color:
                    if not self.has_liberties(board, x, y):
                        to_remove.append((x, y))
        
        # 移除无气棋子
        for x, y in to_remove:
            board.remove_piece(x, y)
        
        return len(to_remove)
    
    def check_valid_move(self, board, x, y, color):
        """检查围棋落子是否合法"""
        # 检查边界和是否已有棋子
        if not (0 <= x < board.size and 0 <= y < board.size):
            return False, "位置超出棋盘范围"
        if not board.is_empty(x, y):
            return False, "该位置已有棋子"
        
        # 临时放置棋子，检查是否有气
        board.place_piece(x, y, color)
        
        # 检查新落的棋子是否有气
        has_liberty = self.has_liberties(board, x, y)
        
        # 检查是否能提掉对方棋子
        can_capture = self.remove_dead_stones(board, color) > 0
        
        # 恢复棋盘状态
        board.remove_piece(x, y)
        
        # 如果新落的棋子有气，或者能提掉对方棋子，则落子合法
        if has_liberty or can_capture:
            return True, ""
        else:
            return False, "落子后无气且无法提子"
    
    def check_winner(self, board, last_move=None):
        """检查围棋胜负（简化版，基于棋子数量和连续跳过）"""
        # 统计双方棋子数量和空点数量
        black_count = 0
        white_count = 0
        empty_count = 0
        
        for y in range(board.size):
            for x in range(board.size):
                piece = board.get_piece(x, y)
                if piece:
                    if piece.color == "black":
                        black_count += 1
                    else:
                        white_count += 1
                else:
                    empty_count += 1
        
        # 简化的胜负判断逻辑：
        # 1. 只有当空点数量少于棋盘的10%，或者双方连续跳过落子时，才判断胜负
        # 2. 基于棋子数量判断胜负（实际围棋应该计算领地和提子数）
        total_points = board.size * board.size
        
        # 这里我们只实现基于棋子数量的胜负判断
        # 连续跳过落子的逻辑在game_model.py的pass_move方法中处理
        
        # 只有当棋盘接近填满时才判断胜负
        if empty_count < total_points * 0.1:
            if black_count > white_count:
                return True, "black"
            elif white_count > black_count:
                return True, "white"
            else:
                # 平局
                return True, "draw"
        
        # 否则游戏继续
        return False, None
    
    def get_game_name(self):
        """获取游戏名称"""
        return "围棋"


class ReversiRuleStrategy(GameStrategy):
    """黑白棋规则策略 - 策略模式的具体策略"""
    
    def __init__(self):
        """初始化黑白棋规则策略"""
        # 八个方向：水平、垂直、斜向
        self.directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1),          (0, 1),
                          (1, -1),  (1, 0), (1, 1)]
    
    def initialize_board(self, board):
        """黑白棋初始化棋盘：中央放置4子"""
        mid = board.size // 2
        board.place_piece(mid - 1, mid - 1, "white")
        board.place_piece(mid, mid, "white")
        board.place_piece(mid - 1, mid, "black")
        board.place_piece(mid, mid - 1, "black")
    
    def post_move_processing(self, board, x, y, current_color):
        """黑白棋落子后处理：翻转对方棋子"""
        # 获取可以翻转的棋子位置
        flip_positions = self.get_flip_positions(board, x, y, current_color)
        # 翻转对方棋子
        self.flip_pieces(board, flip_positions, current_color)
        return True, ""
    
    def can_pass(self):
        """黑白棋不允许手动跳过"""
        return False
    
    def get_flip_positions(self, board, x, y, color):
        """
        获取当前落子可以翻转的棋子位置
        :param board: 棋盘对象
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 落子颜色
        :return: 可以翻转的棋子位置列表
        """
        flip_positions = []
        
        # 检查八个方向
        for dx, dy in self.directions:
            # 检查该方向是否有可翻转的棋子
            self._check_direction(board, x, y, dx, dy, color, flip_positions)
        
        return flip_positions
    
    def _check_direction(self, board, x, y, dx, dy, color, flip_positions):
        """
        检查指定方向上是否有可翻转的棋子
        :param board: 棋盘对象
        :param x: 起始横坐标
        :param y: 起始纵坐标
        :param dx: x方向增量
        :param dy: y方向增量
        :param color: 落子颜色
        :param flip_positions: 存储可翻转棋子位置的列表
        """
        current_flips = []
        nx, ny = x + dx, y + dy
        
        # 沿着方向查找
        while 0 <= nx < board.size and 0 <= ny < board.size:
            piece = board.get_piece(nx, ny)
            if piece is None:
                # 遇到空位置，该方向无效
                return
            elif piece.color == color:
                # 找到己方棋子，该方向有效，记录所有中间棋子
                flip_positions.extend(current_flips)
                return
            else:
                # 找到对方棋子，记录位置
                current_flips.append((nx, ny))
                nx += dx
                ny += dy
    
    def check_valid_move(self, board, x, y, color):
        """检查黑白棋落子是否合法"""
        # 检查边界
        if not (0 <= x < board.size and 0 <= y < board.size):
            return False, "位置超出棋盘范围"
        # 检查该位置是否为空
        if not board.is_empty(x, y):
            return False, "该位置已有棋子"
        # 检查是否能翻转对方棋子
        flip_positions = self.get_flip_positions(board, x, y, color)
        if not flip_positions:
            return False, "该位置无法翻转对方棋子"
        return True, ""
    
    def flip_pieces(self, board, flip_positions, color):
        """
        翻转对方棋子
        :param board: 棋盘对象
        :param flip_positions: 要翻转的棋子位置列表
        :param color: 己方颜色
        """
        for x, y in flip_positions:
            # 移除旧棋子，放置新颜色的棋子
            board.remove_piece(x, y)
            board.place_piece(x, y, color)
    
    def has_valid_move(self, board, color):
        """
        检查当前玩家是否有合法落子
        :param board: 棋盘对象
        :param color: 玩家颜色
        :return: 是否有合法落子
        """
        for y in range(board.size):
            for x in range(board.size):
                if board.is_empty(x, y):
                    is_valid, _ = self.check_valid_move(board, x, y, color)
                    if is_valid:
                        return True
        return False
    
    def check_winner(self, board, last_move=None):
        """检查黑白棋胜负"""
        # 统计双方棋子数量
        black_count = 0
        white_count = 0
        has_empty = False
        
        for y in range(board.size):
            for x in range(board.size):
                piece = board.get_piece(x, y)
                if piece:
                    if piece.color == "black":
                        black_count += 1
                    else:
                        white_count += 1
                else:
                    has_empty = True
        
        # 检查棋盘是否填满
        if not has_empty:
            if black_count > white_count:
                return True, "black"
            elif white_count > black_count:
                return True, "white"
            else:
                return True, "draw"
        
        # 检查双方是否都没有合法落子
        black_has_move = self.has_valid_move(board, "black")
        white_has_move = self.has_valid_move(board, "white")
        
        if not black_has_move and not white_has_move:
            # 双方都没有合法落子，游戏结束
            if black_count > white_count:
                return True, "black"
            elif white_count > black_count:
                return True, "white"
            else:
                return True, "draw"
        
        # 否则游戏继续
        return False, None
    
    def get_game_name(self):
        """获取游戏名称"""
        return "黑白棋"
