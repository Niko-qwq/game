from .board import Board


class GameLogic:
    """游戏逻辑类 - 负责处理游戏的核心逻辑"""
    
    def __init__(self, game_state, strategy):
        """
        初始化游戏逻辑
        :param game_state: 游戏状态对象
        :param strategy: 游戏策略对象
        """
        self.game_state = game_state
        self.board = Board(game_state.board_size)
        self.strategy = strategy  # 依赖注入具体的策略
        
        # 初始化棋盘布局 - 委托给策略
        self.strategy.initialize_board(self.board)
    
    def make_move(self, x, y):
        """
        执行落子
        :param x: 横坐标
        :param y: 纵坐标
        :return: (是否成功, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"

        current_color = self.game_state.current_player_color

        # 1. 检查合法性 (多态)
        is_valid, message = self.strategy.check_valid_move(
            self.board, x, y, current_color)
        if not is_valid:
            return False, message

        # 2. 物理落子 (通用)
        if not self.board.place_piece(x, y, current_color):
            return False, "落子失败"

        # 3. 落子后处理
        success, msg = self.strategy.post_move_processing(
            self.board, x, y, current_color)
            
        if not success:
            # 如果后处理失败（例如围棋自杀），回滚落子
            self.board.remove_piece(x, y)
            return False, msg

        self.game_state.reset_pass_count()

        # 4. 检查胜负 (多态)
        has_winner, winner = self.strategy.check_winner(self.board, (x, y))
        if has_winner:
            self.game_state.set_game_over(winner)
            return True, f"游戏结束，{winner}方获胜！"

        # 5. 切换玩家 (通用)
        self.game_state.toggle_current_player()
        
        return True, "落子成功"
    
    def pass_move(self):
        """
        处理跳过落子
        :return: (是否成功, 信息)
        """
        if self.game_state.game_over:
            return False, "游戏已结束"

        # 检查当前规则是否允许手动跳过
        if not self.strategy.can_pass():
            return False, "当前规则不允许手动跳过"

        # 保存当前玩家颜色，用于提示信息
        current_player_color = self.game_state.current_player_color
        current_player_cn = "黑方" if current_player_color == "black" else "白方"
        
        # 增加连续跳过次数
        self.game_state.increment_pass_count()

        # 如果双方连续跳过，游戏结束
        if self.game_state.pass_count >= 2:
            # 检查胜负
            has_winner, winner = self.strategy.check_winner(self.board, None)
            if has_winner:
                self.game_state.set_game_over(winner)
                return True, f"游戏结束，{winner}方获胜！"
            else:
                self.game_state.set_game_over()
                return True, "双方连续跳过，游戏结束"

        # 切换玩家
        self.game_state.toggle_current_player()
        return True, f"{current_player_cn}选择跳过，切换到对方回合"
    
    def reset(self):
        """
        重置游戏逻辑
        """
        # 清空棋盘
        self.board.clear()
        
        # 重置游戏状态
        self.game_state.reset()
        
        # 使用当前策略重新初始化棋盘布局
        self.strategy.initialize_board(self.board)
    
    def get_board(self):
        """
        获取棋盘对象
        :return: 棋盘对象
        """
        return self.board
    
    def get_strategy(self):
        """
        获取游戏策略对象
        :return: 游戏策略对象
        """
        return self.strategy
