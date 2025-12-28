from abc import ABC, abstractmethod
import random
import numpy as np
from collections import defaultdict
import copy


class AIStrategy(ABC):
    """AI策略接口 - 定义统一的AI策略标准"""
    
    @abstractmethod
    def get_action(self, board, rule_strategy, color):
        """
        获取AI的下一步动作
        
        :param board: 当前的棋盘快照（Board对象），让AI看到局面
        :param rule_strategy: 规则裁判（GameRuleStrategy对象），让AI知道哪里能下
        :param color: 自己的颜色（Color字符串），让AI知道自己是执黑还是执白
        :return: 坐标(x, y)，或None代表无棋可下/投降
        """
        pass
    
    def get_name(self):
        """
        获取策略名称
        
        :return: 策略名称字符串
        """
        return self.__class__.__name__
    
    def _get_legal_moves(self, board, rule_strategy, color):
        """
        获取所有合法落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 合法落子位置列表 [(x1, y1), (x2, y2), ...]
        """
        legal_moves = []
        for y in range(board.size):
            for x in range(board.size):
                is_valid, _ = rule_strategy.check_valid_move(board, x, y, color)
                if is_valid:
                    legal_moves.append((x, y))
        return legal_moves


class RandomStrategy(AIStrategy):
    """随机策略 - 通用愚蠢型策略
    
    特点：不关心是五子棋还是黑白棋，只要裁判说“这里合法”，我就能下。
    用途：用于“简单”难度，或者作为高阶AI的保底逻辑。
    """
    
    def get_action(self, board, rule_strategy, color):
        """
        随机选择一个合法落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 坐标(x, y)，或None代表无棋可下
        """
        legal_moves = self._get_legal_moves(board, rule_strategy, color)
        if not legal_moves:
            return None
        return random.choice(legal_moves)


class GomokuGreedyStrategy(AIStrategy):
    """五子棋贪心策略 - 专家规则型策略
    
    特点：针对五子棋定制，懂“活三”、“冲四”，通过评分表计算价值。
    用途：用于“普通”难度。
    """
    
    def __init__(self):
        # 五子棋评分表，按棋型价值从高到低排列
        self.score_table = {
            'five': 100000,      # 五连
            'four': 10000,       # 活四
            'blocked_four': 5000, # 冲四
            'three': 1000,       # 活三
            'blocked_three': 500, # 眠三
            'two': 100,          # 活二
            'blocked_two': 50,   # 眠二
            'one': 10            # 活一
        }
        
    def get_action(self, board, rule_strategy, color):
        """
        基于贪心策略选择五子棋的最优落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 坐标(x, y)，或None代表无棋可下
        """
        legal_moves = self._get_legal_moves(board, rule_strategy, color)
        if not legal_moves:
            return None
        
        best_score = -float('inf')
        best_moves = [] # 改为列表，防止只有一个最高分时太死板，或者有多个最优解时随机选
        
        # 确定对手颜色
        opponent_color = "white" if color == "black" else "black"
        
        for move in legal_moves:
            x, y = move
            
            # 1. 进攻分数：对自己有利的程度
            attack_score = self._evaluate_position(board, x, y, color)
            
            # 2. 防守分数：如果不堵这里，对对手有利的程度
            # 只有当防守分非常高（对方要赢了）时，防守才最重要
            defense_score = self._evaluate_position(board, x, y, opponent_color)
            
            # 3. 综合评分
            # 通常防守权重要略高于进攻，或者动态调整
            # 简单的逻辑：谁分数高听谁的，或者加权求和
            score = attack_score + defense_score * 0.8
            
            # 这种加法策略比较简单。更高级的是：
            # if defense_score >= 10000: score = defense_score + 1000 (必须防守)
            # else: score = attack_score + defense_score * 0.5
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else None
    
    def _evaluate_position(self, board, x, y, color):
        """
        评估五子棋某个位置的价值
        
        :param board: 当前的棋盘快照
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 自己的颜色
        :return: 位置的评分
        """
        # 模拟落子
        board.place_piece(x, y, color)
        
        # 检查四个方向的棋型
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        
        for dx, dy in directions:
            # 计算该方向上的棋型
            pattern = self._get_pattern(board, x, y, dx, dy, color)
            # 根据棋型获取评分
            score += self._get_pattern_score(pattern)
        
        # 恢复棋盘
        board.remove_piece(x, y)
        
        return score
    
    def _get_pattern(self, board, x, y, dx, dy, color):
        """
        获取某个位置在特定方向上的棋型
        
        :param board: 当前的棋盘快照
        :param x: 横坐标
        :param y: 纵坐标
        :param dx: 方向的x增量
        :param dy: 方向的y增量
        :param color: 自己的颜色
        :return: 棋型字符串
        """
        # 检查该方向上的连续棋子
        count = 1
        blocked = [False, False]  # [左边是否被阻挡, 右边是否被阻挡]
        
        # 检查正方向
        for i in range(1, 5):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < board.size and 0 <= ny < board.size:
                piece = board.get_piece(nx, ny)
                if piece and piece.color == color:
                    count += 1
                else:
                    blocked[0] = piece is not None
                    break
            else:
                blocked[0] = True
                break
        
        # 检查反方向
        for i in range(1, 5):
            nx, ny = x - dx * i, y - dy * i
            if 0 <= nx < board.size and 0 <= ny < board.size:
                piece = board.get_piece(nx, ny)
                if piece and piece.color == color:
                    count += 1
                else:
                    blocked[1] = piece is not None
                    break
            else:
                blocked[1] = True
                break
        
        # 判断棋型
        if count >= 5:
            return 'five'
        elif count == 4:
            if not any(blocked):
                return 'four'  # 活四
            else:
                return 'blocked_four'  # 冲四
        elif count == 3:
            if not any(blocked):
                return 'three'  # 活三
            else:
                return 'blocked_three'  # 眠三
        elif count == 2:
            if not any(blocked):
                return 'two'  # 活二
            else:
                return 'blocked_two'  # 眠二
        else:
            return 'one'  # 活一
    
    def _get_pattern_score(self, pattern):
        """
        根据棋型获取评分
        
        :param pattern: 棋型字符串
        :return: 评分
        """
        return self.score_table.get(pattern, 0)


class ReversiGreedyStrategy(AIStrategy):
    """黑白棋贪心策略 - 专家规则型策略
    
    特点：针对黑白棋定制，懂“占角”、“少吃子”、“行动力”，有专用的权重矩阵。
    用途：用于“普通”难度。
    """
    
    def __init__(self):
        # 黑白棋位置权重矩阵，角的权重最高，边次之，中心区域较低
        self.weight_matrix = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100]
        ]
    
    def get_action(self, board, rule_strategy, color):
        """
        基于贪心策略选择黑白棋的最优落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 坐标(x, y)，或None代表无棋可下
        """
        legal_moves = self._get_legal_moves(board, rule_strategy, color)
        if not legal_moves:
            return None
        
        best_score = -float('inf')
        best_move = None
        
        for move in legal_moves:
            x, y = move
            # 计算该位置的评分
            score = self._evaluate_position(board, x, y, color, rule_strategy)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _evaluate_position(self, board, x, y, color, rule_strategy):
        """
        评估黑白棋某个位置的价值
        
        :param board: 当前的棋盘快照
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 自己的颜色
        :param rule_strategy: 规则裁判
        :return: 位置的评分
        """
        score = 0
        
        # 1. 位置权重评分（占角、占边）
        # 确保权重矩阵适用于不同大小的棋盘
        matrix_size = len(self.weight_matrix)
        if board.size == matrix_size:
            score += self.weight_matrix[y][x]
        else:
            # 对于其他大小的棋盘，简化处理：角和边的权重更高
            if (x == 0 or x == board.size - 1) and (y == 0 or y == board.size - 1):
                score += 100  # 角
            elif x == 0 or x == board.size - 1 or y == 0 or y == board.size - 1:
                score += 10   # 边
        
        # 2. 翻转棋子数量评分
        # 使用自己实现的翻转检测方法，不依赖规则策略的私有方法
        flippable_count = len(self._simulate_find_flippable(board, x, y, color))
        score += flippable_count * 2
        
        # 3. 行动力评分（后续可下位置数量）
        # 简化处理：对于二级AI，移除复杂的行动力计算以提升性能
        # 若需要保留，建议使用更高效的实现方式
        
        return score
    
    def _simulate_find_flippable(self, board, x, y, color):
        """
        AI自己实现一套简单的翻转检测，解耦对Rule私有方法的依赖
        虽然代码重复，但保证了AI模块的独立性
        
        :param board: 当前的棋盘快照
        :param x: 横坐标
        :param y: 纵坐标
        :param color: 自己的颜色
        :return: 可翻转的棋子位置列表
        """
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        flippable = []
        opponent_color = "white" if color == "black" else "black"

        for dx, dy in directions:
            temp = []
            cur_x, cur_y = x + dx, y + dy
            while 0 <= cur_x < board.size and 0 <= cur_y < board.size:
                piece = board.get_piece(cur_x, cur_y)
                if piece is None:
                    break
                if piece.color == opponent_color:
                    temp.append((cur_x, cur_y))
                elif piece.color == color:
                    if temp:
                        flippable.extend(temp)
                    break
                cur_x += dx
                cur_y += dy
        return flippable


class MCTSNode:
    """
    MCTS树节点类
    """
    def __init__(self, board, rule_strategy, color, parent=None, parent_action=None):
        """
        初始化MCTS节点
        
        :param board: 当前棋盘状态
        :param rule_strategy: 游戏规则策略
        :param color: 当前玩家颜色
        :param parent: 父节点
        :param parent_action: 父节点的动作
        """
        self.board = copy.deepcopy(board)  # 深拷贝棋盘，避免影响原始状态
        self.rule_strategy = rule_strategy  # 游戏规则策略
        self.color = color  # 当前玩家颜色
        self.parent = parent  # 父节点
        self.parent_action = parent_action  # 父节点的动作
        self.children = []  # 子节点列表
        self._untried_actions = None  # 未尝试的动作
        self._untried_actions = self._get_legal_actions()  # 获取所有合法动作
        self._number_of_visits = 0  # 访问次数
        self._results = defaultdict(int)  # 结果统计
        self._results[1] = 0  # 获胜次数
        self._results[-1] = 0  # 失败次数
        self._results[0] = 0  # 和棋次数
    
    def q(self):
        """
        获取节点的价值（获胜次数 - 失败次数）
        
        :return: 节点价值
        """
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
    
    def n(self):
        """
        获取节点的访问次数
        
        :return: 访问次数
        """
        return self._number_of_visits
    
    def expand(self):
        """
        扩展节点，选择一个未尝试的动作并创建子节点
        
        :return: 新创建的子节点
        """
        action = self._untried_actions.pop()
        next_board = copy.deepcopy(self.board)
        next_board.place_piece(action[0], action[1], self.color)
        
        # 切换玩家颜色
        next_color = "white" if self.color == "black" else "black"
        
        child_node = MCTSNode(next_board, self.rule_strategy, next_color, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node
    
    def _get_legal_actions(self):
        """
        获取当前状态下的所有合法动作
        
        :return: 合法动作列表 [(x1, y1), (x2, y2), ...]
        """
        legal_actions = []
        for y in range(self.board.size):
            for x in range(self.board.size):
                is_valid, _ = self.rule_strategy.check_valid_move(self.board, x, y, self.color)
                if is_valid:
                    legal_actions.append((x, y))
        return legal_actions
    
    def is_terminal_node(self):
        """
        检查节点是否为终端节点（游戏结束）
        
        :return: 是否为终端节点
        """
        has_winner, winner = self.rule_strategy.check_winner(self.board)
        return has_winner
    
    def is_fully_expanded(self):
        """
        检查节点是否已完全扩展
        
        :return: 是否已完全扩展
        """
        return len(self._untried_actions) == 0
    
    def best_child(self, c_param=1.4):
        """
        使用UCB1算法选择最优子节点
        
        :param c_param: 探索参数
        :return: 最优子节点
        """
        choices_weights = [
            (child.q() / child.n()) + c_param * np.sqrt((2 * np.log(self.n()) / child.n()))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]
    
    def rollout(self):
        """
        模拟随机落子，直到游戏结束
        
        :return: 模拟结果（1: 胜利, -1: 失败, 0: 和棋）
        """
        current_rollout_board = copy.deepcopy(self.board)
        current_rollout_color = self.color
        
        while True:
            # 检查游戏是否结束
            has_winner, winner = self.rule_strategy.check_winner(current_rollout_board)
            if has_winner:
                return 1 if winner == self.color else -1
            
            # 获取当前玩家的合法动作
            legal_actions = []
            for y in range(current_rollout_board.size):
                for x in range(current_rollout_board.size):
                    is_valid, _ = self.rule_strategy.check_valid_move(current_rollout_board, x, y, current_rollout_color)
                    if is_valid:
                        legal_actions.append((x, y))
            
            # 如果没有合法动作，和棋
            if not legal_actions:
                return 0
            
            # 随机选择一个动作
            action = random.choice(legal_actions)
            current_rollout_board.place_piece(action[0], action[1], current_rollout_color)
            
            # 切换玩家颜色
            current_rollout_color = "white" if current_rollout_color == "black" else "black"
    
    def backpropagate(self, result):
        """
        回溯更新节点信息
        
        :param result: 模拟结果
        """
        self._number_of_visits += 1
        self._results[result] += 1
        
        if self.parent:
            self.parent.backpropagate(result)
    
    def _tree_policy(self):
        """
        树策略：选择要扩展的节点
        
        :return: 要扩展的节点
        """
        current_node = self
        
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        
        return current_node
    
    def best_action(self, simulations_number=1000):
        """
        执行MCTS搜索，返回最优动作
        
        :param simulations_number: 模拟次数
        :return: 最优动作
        """
        for _ in range(simulations_number):
            # 选择要扩展的节点
            v = self._tree_policy()
            
            # 模拟落子
            reward = v.rollout()
            
            # 回溯更新
            v.backpropagate(reward)
        
        # 返回最优动作
        return self.best_child(c_param=0).parent_action


class GomokuMCTSStrategy(AIStrategy):
    """
    五子棋MCTS策略 - 基于蒙特卡洛树搜索的高级策略
    
    特点：通过模拟落子和回溯更新，搜索最优策略
    用途：用于“困难”难度
    """
    
    def __init__(self, simulations_number=100):
        """
        初始化MCTS策略
        
        :param simulations_number: 模拟次数
        """
        self.simulations_number = simulations_number
    
    def get_action(self, board, rule_strategy, color):
        """
        基于MCTS算法选择五子棋的最优落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 坐标(x, y)，或None代表无棋可下
        """
        # 获取所有合法动作
        legal_moves = self._get_legal_moves(board, rule_strategy, color)
        if not legal_moves:
            return None
        
        # 如果只有一个合法动作，直接返回
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # 创建根节点
        root = MCTSNode(board, rule_strategy, color)
        
        # 执行MCTS搜索，获取最优动作
        best_move = root.best_action(self.simulations_number)
        
        return best_move


class ReversiMCTSStrategy(AIStrategy):
    """
    黑白棋MCTS策略 - 基于蒙特卡洛树搜索的高级策略
    
    特点：通过模拟落子和回溯更新，搜索最优策略
    用途：用于“困难”难度
    """
    
    def __init__(self, simulations_number=100):
        """
        初始化MCTS策略
        
        :param simulations_number: 模拟次数
        """
        self.simulations_number = simulations_number
    
    def get_action(self, board, rule_strategy, color):
        """
        基于MCTS算法选择黑白棋的最优落子位置
        
        :param board: 当前的棋盘快照
        :param rule_strategy: 规则裁判
        :param color: 自己的颜色
        :return: 坐标(x, y)，或None代表无棋可下
        """
        # 获取所有合法动作
        legal_moves = self._get_legal_moves(board, rule_strategy, color)
        if not legal_moves:
            return None
        
        # 如果只有一个合法动作，直接返回
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # 创建根节点
        root = MCTSNode(board, rule_strategy, color)
        
        # 执行MCTS搜索，获取最优动作
        best_move = root.best_action(self.simulations_number)
        
        return best_move
