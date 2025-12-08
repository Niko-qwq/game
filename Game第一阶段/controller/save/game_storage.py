import json
from model.board import Board
from model.memento import MementoFactory
from .save_data import GameSaveData

class GameStorage:
    """负责文件的物理读写 (IO层)"""
    
    def save_to_file(self, save_data: GameSaveData, file_path: str):
        """将 GameSaveData 写入文件"""
        try:
            # 调用 Product 自己的序列化方法
            json_data = save_data.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            return True, "保存成功"
        except Exception as e:
            return False, f"保存失败: {str(e)}"

    def load_from_file(self, file_path: str):
        """
        读取文件并解析基础数据
        注意：Builder 模式主要用于构建复杂对象，读取过程通常是解析过程。
        这里为了简单，直接返回解析好的 GameSaveData 对象。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. 解析核心数据
            game_info = data.get("game_info", {})
            board_data = data.get("board_snapshot", [])
            
            # 2. 重建 Memento
            board_size = game_info.get("board_size", 15)
            board = Board(board_size)
            self._fill_board(board, board_data)
            
            memento = MementoFactory.create_memento(
                game_info.get("type", "gomoku"),
                board,
                game_info.get("current_player", "black"),
                pass_count=game_info.get("pass_count", 0)
            )
            
            # 3. 组装结果
            result = GameSaveData()
            result.memento = memento
            result.history = data.get("history", [])
            result.players = data.get("players", {})
            result.metadata = {"timestamp": data.get("timestamp")}
            
            return result, "读取成功"
        except Exception as e:
            return None, f"读取失败: {str(e)}"

    def _fill_board(self, board, board_data):
        """辅助方法：填充棋盘"""
        for y, row_str in enumerate(board_data):
            for x, char in enumerate(row_str):
                if char == 'b': board.place_piece(x, y, "black")
                elif char == 'w': board.place_piece(x, y, "white")