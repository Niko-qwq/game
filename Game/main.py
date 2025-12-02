from controller.game_controller import GameController

def main():
    """主程序入口"""
    # 创建游戏控制器
    game_controller = GameController()

    # 启动游戏，默认五子棋，15x15棋盘
    game_controller.start_game(game_type="gomoku", board_size=15)

if __name__ == "__main__":
    main()
