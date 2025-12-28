from .board import Board
from .rule_strategy import GameRuleStrategy, GomokuRuleStrategy, GoRuleStrategy
from .game_state import GameState



class GameLogic:
    """游戏逻辑类 - 负责处理游戏的核心流程"""
    
    def __init__(self, game_state : GameState, rule_strategy : GameRuleStrategy):
        """
        初始化游戏逻辑
        :param game_state: 游戏状态对象
        :param rule_strategy: 游戏规则策略对象
        """
        self.game_state = game_state
        self.board = Board(game_state.board_size)
        self.rule_strategy = rule_strategy
        # 初始化棋盘
        self.rule_strategy.init_board(self.board)
    def make_move(self, x, y):
        """
        执行落子
        :param x: 横坐标
        :param y: 纵坐标
        :return: (是否成功, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"
        
        

        # 1. 静态检查：位置是否空？是否越界？
        is_valid, message = self.rule_strategy.check_valid_move(
            self.board, x, y, self.game_state.current_player_color)
        if not is_valid:
            return False, message

        # 2. 尝试落子：在克隆的棋盘上进行所有操作
        # 2.0 克隆棋盘，避免直接修改原棋盘
        cloned_board = self.board.clone()
        
        # 2.1 在克隆棋盘上放置棋子
        if not cloned_board.place_piece(x, y, self.game_state.current_player_color):
            return False, "落子失败"

        # 2.2. 在克隆棋盘上进行动态副作用处理
        post_success, post_message = self.rule_strategy.post_move_processing(
            cloned_board, x, y, self.game_state.current_player_color, self.game_state)
        if not post_success:
            # 克隆棋盘上的操作失败，直接返回，不影响原棋盘
            return False, post_message

        # 3. 所有验证都通过，将克隆棋盘的状态复制到原棋盘
        # 清空原棋盘并复制克隆棋盘的状态
        self.board.clear()
        for y_idx in range(cloned_board.size):
            for x_idx in range(cloned_board.size):
                piece = cloned_board.get_piece(x_idx, y_idx)
                if piece is not None:
                    self.board.place_piece(x_idx, y_idx, piece.color)
        
        # 4. 更新游戏状态：委托给规则策略处理，让每个规则可以有不同的实现
        self.rule_strategy.update_game_state(self.game_state)
        
        # 5. 检查胜负
        has_winner, winner = self.rule_strategy.check_winner(
            cloned_board, (x, y))
        if has_winner:
            self.game_state.set_game_over(winner)
            winner_cn = "黑方" if winner == "black" else "白方"
            return True, f"游戏结束，{winner_cn}方获胜！"

        # 6. 切换玩家
        self.game_state.toggle_current_player()
        # 7. 回合开始时处理：检查是否跳过当前回合
        turn_start_result = self.rule_strategy.on_turn_start(
            self.board, self.game_state.current_player_color, self.game_state)
        if turn_start_result["skip_turn"]:
            # 自动跳过当前回合
            return self.pass_move()

        return True, f"落子成功{post_message}"
    
    def can_pass(self):
        """
        检查是否可以跳过落子
        :return: (是否可以跳过, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"

        # 使用策略的can_pass方法检查是否可以跳过
        return self.rule_strategy.can_pass(self.game_state.current_player_color)
    
    def pass_move(self):
        """
        处理跳过落子
        :return: (是否成功, 信息)
        """
        # 1. 检查是否可以跳过
        can_pass, message = self.can_pass()
        if not can_pass:
            return False, message

        # 2. 保存当前玩家颜色，用于提示信息
        current_player_color = self.game_state.current_player_color
        current_player_cn = "黑方" if current_player_color == "black" else "白方"
        
        # 3. 执行跳过操作（策略处理具体逻辑）
        success, handle_message = self.rule_strategy.handle_pass(self.game_state)
        if not success:
            return False, handle_message

        # 4. 切换玩家
        self.game_state.toggle_current_player()
        
        # 5. 检查游戏是否结束
        if self.game_state.game_over:
            return True, handle_message
        
        return True, f"{current_player_cn}跳过，切换到对方回合"
    
    def reset(self):
        """
        重置游戏逻辑
        """
        self.board.clear()
        self.game_state.reset()
        # 保持现有策略不变，不需要重新创建
    
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
