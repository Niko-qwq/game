from abc import ABC, abstractmethod


class Player(ABC):
    """玩家抽象基类 - 定义玩家的基本接口"""
    
    def __init__(self, color):
        """
        初始化玩家
        :param color: 玩家颜色，"black"或"white"
        """
        self.color = color
        self.name = ""
    
    @abstractmethod
    def make_move(self, game_model):
        """
        执行落子
        :param game_model: 游戏模型对象
        :return: (是否成功, 信息, x, y) 或 None(如果是异步落子)
        """
        pass
    
    def get_color(self):
        """
        获取玩家颜色
        :return: 玩家颜色
        """
        return self.color
    
    def set_name(self, name):
        """
        设置玩家名称
        :param name: 玩家名称
        """
        self.name = name
    
    def get_name(self):
        """
        获取玩家名称
        :return: 玩家名称
        """
        return self.name


class HumanPlayer(Player):
    """人类玩家 - 具体玩家实现"""
    
    def __init__(self, color):
        """
        初始化人类玩家
        :param color: 玩家颜色，"black"或"white"
        """
        super().__init__(color)
        self.name = "人类玩家"
    
    def make_move(self, game_model):
        """
        人类玩家的通过GUI交互落子,此方法不直接调用
        :param game_model: 游戏模型对象
        :return: None
        """
        # 人类玩家通过GUI交互落子，此方法不直接调用
        return None

