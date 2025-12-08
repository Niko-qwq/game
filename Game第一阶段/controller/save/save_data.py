from abc import ABC, abstractmethod


class AbstractGameSaveData(ABC):
    """抽象产品接口 - 定义存档数据的通用接口"""
    
    @abstractmethod
    def to_dict(self):
        """将存档数据转换为可序列化的字典"""
        pass


class GameSaveData(AbstractGameSaveData):
    """存档数据对象 (Product) - 包含存储所需的所有信息"""
    def __init__(self):
        self.memento = None       # Model 状态
        self.history = []         # 命令历史
        self.metadata = {}        # 元数据 (时间、版本)
        self.players = {}         # 玩家信息 
        
    def to_dict(self):
        """将存档数据转换为可序列化的字典"""
        # 序列化 Board
        board_data = []
        if self.memento:
            board = self.memento.get_board()
            for y in range(board.size):
                row = ""
                for x in range(board.size):
                    piece = board.get_piece(x, y)
                    row += piece.color[0] if piece else "."
                board_data.append(row)

        # 构建基础字典
        save_dict = {
            "version": self.metadata.get("version", "2.0"),
            "timestamp": self.metadata.get("timestamp", ""),
            "game_info": {
                "type": self.memento.get_game_type() if self.memento else "gomoku",
                "board_size": self.memento.get_board().size if self.memento else 15,
                "current_player": self.memento.get_current_player() if self.memento else "black",
            },
            "players": self.players,
            "board_snapshot": board_data,
            "history": self.history
        }

        # 根据游戏类型添加特定字段
        if self.memento:
            game_type = self.memento.get_game_type()
            
            # 围棋特定字段
            if game_type == "go":
                # 检查memento是否有这些方法，避免AttributeError
                if hasattr(self.memento, "get_pass_count"):
                    save_dict["game_info"]["pass_count"] = self.memento.get_pass_count()
                if hasattr(self.memento, "get_count_black_pieces"):
                    save_dict["game_info"]["count_black_pieces"] = self.memento.get_count_black_pieces()
                if hasattr(self.memento, "get_count_white_pieces"):
                    save_dict["game_info"]["count_white_pieces"] = self.memento.get_count_white_pieces()

        return save_dict