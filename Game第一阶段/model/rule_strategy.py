from abc import ABC, abstractmethod

class GameRuleStrategy(ABC):
    """游戏规则策略接口 - 策略模式的抽象策略"""
    
    @abstractmethod
    def check_valid_move(self, board, x, y, color):
        """
        检查落子是否合法
        :param board: 棋盘对象
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 棋子颜色
        :return: (是否合法, 错误信息)
        """
        pass
    
    @abstractmethod
    def post_move_processing(self, board, x, y, color, game_state=None):
        """
        落子后处理（提子、翻转等）
        :param board: 棋盘对象
        :param x: 落子横坐标
        :param y: 落子纵坐标
        :param color: 落子颜色
        :param game_state: 游戏状态对象（可选）
        :return: (是否成功, 错误信息)
        """
        pass
    
    @abstractmethod
    def can_pass(self, current_color):
        """
        检查是否可以跳过
        :param current_color: 当前玩家颜色
        :return: (是否可以跳过, 错误信息)
        """
        pass
    
    @abstractmethod
    def handle_pass(self, game_state):
        """
        处理跳过操作
        :param game_state: 游戏状态对象
        :return: (是否成功, 错误信息)
        """
        pass
    
    @abstractmethod
    def check_winner(self, board, last_move=None):
        """
        检查胜负
        :param board: 棋盘对象
        :param last_move: 最后一步落子位置 (x, y)
        :return: (是否有胜者, 胜者颜色或None)
        """
        pass
    
    @abstractmethod
    def get_game_name(self):
        """
        获取游戏名称
        :return: 游戏名称
        """
        pass
    
    @abstractmethod
    def on_turn_start(self, board, color, game_state=None):
        """
        回合开始时的处理
        :param board: 棋盘对象
        :param color: 当前回合玩家颜色
        :param game_state: 游戏状态对象（可选）
        :return: 包含回合开始处理结果的字典
                 可能包含的键：
                 - skip_turn: bool，是否需要跳过当前玩家回合
                 - message: str，处理的信息或提示
                 - any other custom keys for specific game rules
        """
        pass
    
    @abstractmethod
    def update_game_state(self, game_state):
        """
        更新游戏状态，处理落子后的状态变化
        :param game_state: 游戏状态对象，需要被更新
        :return: None
        """
        pass
    
    @abstractmethod
    def init_board(self, board):
        """
        初始化棋盘
        :param board: 棋盘对象，需要被初始化
        :return: None
        """
        pass


class GomokuRuleStrategy(GameRuleStrategy):
    """五子棋规则策略 - 策略模式的具体策略"""
    
    def check_valid_move(self, board, x, y, color):
        """检查五子棋落子是否合法"""
        if not (0 <= x < board.size and 0 <= y < board.size):
            return False, "位置超出棋盘范围"
        if not board.is_empty(x, y):
            return False, "该位置已有棋子"
        return True, ""
    
    def post_move_processing(self, board, x, y, color, game_state):
        """五子棋落子后处理"""
        return True, ""
    
    def can_pass(self, current_color):
        """检查是否可以跳过"""
        # 五子棋不允许跳过
        return False, "五子棋不允许跳过"
    
    def handle_pass(self, game_state):
        """处理跳过操作"""
        # 五子棋不允许跳过，直接返回失败
        return False, "五子棋不允许跳过"
    
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
    
    def get_game_name(self):
        """获取游戏名称"""
        return "五子棋"
    
    def on_turn_start(self, board, color, game_state=None):
        """
        五子棋回合开始时的处理
        :param board: 棋盘对象
        :param color: 当前回合玩家颜色
        :param game_state: 游戏状态对象（可选）
        :return: 包含回合开始处理结果的字典
        """
        # 五子棋回合开始时不需要特殊处理
        return {
            "skip_turn": False,
            "message": ""
        }
    
    def update_game_state(self, game_state):
        """
        更新五子棋游戏状态
        :param game_state: 游戏状态对象，需要被更新
        :return: None
        """
        # 五子棋不支持跳过操作，所以落子后不需要更新特殊状态
        pass
    
    def init_board(self, board):
        """
        初始化五子棋棋盘
        :param board: 棋盘对象，需要被初始化
        :return: None
        """
        # 五子棋初始化时棋盘为空，不需要特殊处理
        pass


class GoRuleStrategy(GameRuleStrategy):
    """围棋规则策略 - 策略模式的具体策略"""
    
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
        return True, ""
    
    def post_move_processing(self, board, x, y, color, game_state):
        """围棋落子后处理"""
        # 移除对方无气棋子
        captured = self.remove_dead_stones(board, color)
        
         # 检查己方刚落的棋子是否还有气（防止自杀）
        if not self.has_liberties(board, x, y):
            return False, "落子后无气（自杀）"
        if color == "black":
            game_state.count_black_pieces += captured
        else:
            game_state.count_white_pieces += captured
        
        # 返回提子数信息
        current_captured = game_state.count_black_pieces if color == 'black' else game_state.count_white_pieces
        return True, f"提子{captured}颗，本局提子数：{current_captured}颗"
    
    def can_pass(self, current_color):
        """检查是否可以跳过"""
        # 围棋允许跳过
        return True, ""
    
    def handle_pass(self, game_state):
        """处理跳过操作"""
        # 增加连续跳过次数（确保游戏状态支持此方法）
        if hasattr(game_state, 'increment_pass_count'):
            game_state.increment_pass_count()
        
        # 如果双方连续跳过，游戏结束
        if hasattr(game_state, 'pass_count') and game_state.pass_count >= 2:
            game_state.set_game_over()
            return True, "双方连续跳过，游戏结束"
        
        return True, ""
    
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
        # 连续跳过落子的逻辑在handle_pass方法中处理
        
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
    
    def on_turn_start(self, board, color, game_state=None):
        """
        围棋回合开始时的处理
        :param board: 棋盘对象
        :param color: 当前回合玩家颜色
        :param game_state: 游戏状态对象（可选）
        :return: 包含回合开始处理结果的字典
        """
        # 围棋回合开始时不需要特殊处理
        return {
            "skip_turn": False,
            "message": ""
        }
    
    def update_game_state(self, game_state):
        """
        更新围棋游戏状态
        :param game_state: 游戏状态对象，需要被更新
        :return: None
        """
        # 围棋中落子后需要重置连续跳过次数
        if hasattr(game_state, 'reset_pass_count'):
            game_state.reset_pass_count()
    
    def init_board(self, board):
        """
        初始化围棋棋盘
        :param board: 棋盘对象，需要被初始化
        :return: None
        """
        # 围棋初始化时棋盘为空，不需要特殊处理
        pass
