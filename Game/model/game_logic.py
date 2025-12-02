from .board import Board
from .rule_strategy import GomokuRuleStrategy, GoRuleStrategy


class GameLogic:
    """游戏逻辑类 - 负责处理游戏的核心逻辑"""
    
    def __init__(self, game_state):
        """
        初始化游戏逻辑
        :param game_state: 游戏状态对象
        """
        self.game_state = game_state
        self.board = Board(game_state.board_size)
        
        # 根据游戏类型选择规则策略
        if game_state.game_type == "gomoku":
            self.rule_strategy = GomokuRuleStrategy()
        elif game_state.game_type == "go":
            self.rule_strategy = GoRuleStrategy()
        else:
            raise ValueError(f"不支持的游戏类型: {game_state.game_type}")
    
    def make_move(self, x, y):
        """
        执行落子
        :param x: 横坐标
        :param y: 纵坐标
        :return: (是否成功, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"

        # 检查落子是否合法
        is_valid, message = self.rule_strategy.check_valid_move(
            self.board, x, y, self.game_state.current_player_color)
        if not is_valid:
            return False, message

        # 放置棋子
        if not self.board.place_piece(x, y, self.game_state.current_player_color):
            return False, "落子失败"

        # 重置连续跳过次数，因为有玩家落子了
        self.game_state.reset_pass_count()

        # 对于围棋，移除无气棋子
        if self.game_state.game_type == "go":
            # 移除对方无气棋子
            self.rule_strategy.remove_dead_stones(
                self.board, self.game_state.current_player_color)

            # 检查己方刚落的棋子是否还有气（防止自杀）
            if hasattr(self.rule_strategy, 'has_liberties'):
                if not self.rule_strategy.has_liberties(self.board, x, y):
                    # 移除刚落的棋子（自杀不允许）
                    self.board.remove_piece(x, y)
                    return False, "落子后无气（自杀）"

        # 检查胜负
        has_winner, winner = self.rule_strategy.check_winner(
            self.board, (x, y))
        if has_winner:
            self.game_state.set_game_over(winner)
            return True, f"游戏结束，{winner}方获胜！"

        # 切换玩家
        self.game_state.toggle_current_player()
        return True, "落子成功"
    
    def pass_move(self):
        """
        处理跳过落子
        :return: (是否成功, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"

        # 只有围棋游戏才能跳过落子
        if self.game_state.game_type != "go":
            return False, "只有围棋游戏才能跳过落子"

        # 保存当前玩家颜色，用于提示信息
        current_player_color = self.game_state.current_player_color
        current_player_cn = "黑方" if current_player_color == "black" else "白方"
        
        # 增加连续跳过次数
        self.game_state.increment_pass_count()

        # 如果双方连续跳过，游戏结束
        if self.game_state.pass_count >= 2:
            self.game_state.set_game_over()
            return True, "双方连续跳过，游戏结束"

        # 切换玩家
        self.game_state.toggle_current_player()
        return True, f"{current_player_cn}选择跳过，切换到对方回合"
    
    def reset(self):
        """
        重置游戏逻辑
        """
        self.board.clear()
        self.game_state.reset()
        
        # 根据游戏类型重新选择规则策略
        if self.game_state.game_type == "gomoku":
            self.rule_strategy = GomokuRuleStrategy()
        elif self.game_state.game_type == "go":
            self.rule_strategy = GoRuleStrategy()
        else:
            raise ValueError(f"不支持的游戏类型: {self.game_state.game_type}")
    
    def get_board(self):
        """
        获取棋盘对象
        :return: 棋盘对象
        """
        return self.board
    
    def get_rule_strategy(self):
        """
        获取规则策略对象
        :return: 规则策略对象
        """
        return self.rule_strategy
