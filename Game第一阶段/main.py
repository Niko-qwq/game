from controller.app_controller import AppController
from view.main_window import MainWindow

def main():
    # 1. 创建总控制器
    app = AppController()
    
    # 2. 创建主窗口 (注入控制器)
    window = MainWindow(app)
    
    # 3. 绑定应用级观察者 (用于页面跳转)
    app.attach(window)
    
    # 4. 运行
    window.mainloop()

if __name__ == "__main__":
    main()

