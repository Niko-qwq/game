import datetime
from abc import ABC, abstractmethod
from .save_data import GameSaveData, AbstractGameSaveData


class AbstractGameSaveBuilder(ABC):
    """抽象建造者 - 定义构建游戏存档的抽象接口"""
    
    @abstractmethod
    def with_memento(self, memento):
        """抽象方法：添加游戏状态"""
        pass
    
    @abstractmethod
    def with_history(self, history_provider):
        """抽象方法：添加历史记录"""
        pass
    
    @abstractmethod
    def with_metadata(self):
        """抽象方法：添加元数据"""
        pass
    
    @abstractmethod
    def build(self) -> AbstractGameSaveData:
        """抽象方法：构建并返回最终产品"""
        pass


class GameSaveBuilder(AbstractGameSaveBuilder):
    """存档建造者 (Builder) - 负责组装 GameSaveData"""
    
    def __init__(self):
        self.save_data = GameSaveData()

    def with_memento(self, memento):
        """步骤1：注入游戏核心状态"""
        self.save_data.memento = memento
        return self # 支持链式调用
    
    def with_history(self, history_provider):
        """步骤2：注入历史记录"""
        # 从历史记录提供者提取数据，依赖抽象而非具体实现
        self.save_data.history = history_provider.get_history_data()
        return self

    def with_metadata(self):
        """步骤3：注入元数据"""
        self.save_data.metadata["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_data.metadata["version"] = "2.0"
        return self


    def build(self) -> AbstractGameSaveData:
        """返回构建好的 Product"""
        return self.save_data