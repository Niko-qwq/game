class CommandManager:
    """命令管理者 (Invoker)"""
    
    def __init__(self):
        self.history = []     # 撤销栈
        self.redo_stack = []  # 重做栈 (如果以后想做"取消撤销"功能)

    def execute_command(self, command):
        """执行新命令"""
        success, message = command.execute()
        if success:
            # 执行成功，加入历史记录
            self.history.append(command)
            # 一旦有新操作，清空重做栈
            self.redo_stack.clear()
        return success, message

    def undo(self):
        """执行撤销"""
        if not self.history:
            return False, "没有可悔的棋"
        
        # 取出最近一个命令
        command = self.history.pop()
        success, message = command.undo()
        
        if success:
            # 撤销成功，可以放入重做栈（可选）
            self.redo_stack.append(command)
            
        return success, message
        
    def clear(self):
        """清空历史"""
        self.history.clear()
        self.redo_stack.clear()
    
    def get_history_data(self):
        """获取历史记录数据，用于保存"""
        # 简化实现，只返回命令的基本信息
        # 实际项目中可以根据需要返回更详细的信息
        history_data = []
        for command in self.history:
            # 假设命令对象有相应的属性或方法获取数据
            if hasattr(command, 'x') and hasattr(command, 'y'):
                history_data.append({
                    'type': 'move',
                    'x': command.x,
                    'y': command.y,
                    'player': command.player_color if hasattr(command, 'player_color') else 'unknown'
                })
        return history_data