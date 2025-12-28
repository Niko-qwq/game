import tkinter as tk
from tkinter import ttk
from typing import Callable

from model.user_manager import default_user_manager
from view.components.login_form import LoginForm, LoginFormCallbacksProtocol
from view.components.register_form import RegisterForm, RegisterFormCallbacksProtocol


class LoginRegisterPage(tk.Frame):
    """登录注册页面"""
    
    def __init__(self, parent: tk.Widget, app_controller):
        """
        初始化登录注册页面
        :param parent: 父窗口
        :param app_controller: 应用控制器
        """
        super().__init__(parent)
        self.app_controller = app_controller
        self.user_manager = default_user_manager
        
        # 表单状态：'login' 或 'register'
        self.current_form = "login"
        
        # 设置组件
        self.setup_widgets()
    
    def setup_widgets(self) -> None:
        """设置组件"""
        # 顶部导航栏
        self._setup_navigation()
        
        # 表单容器
        self.form_container = ttk.Frame(self)
        self.form_container.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)
        
        # 初始化登录和注册表单
        self._init_forms()
        
        # 显示初始表单（登录表单）
        self.show_login_form()
    
    def _setup_navigation(self) -> None:
        """设置顶部导航栏"""
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 返回首页按钮
        back_btn = ttk.Button(nav_frame, text="< 返回首页", 
                            command=lambda: self.app_controller.nav_to_home())
        back_btn.pack(side=tk.LEFT)
        
        # 页面标题
        title_label = ttk.Label(nav_frame, text="用户认证", 
                              font=('微软雅黑', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=20)
    
    def _init_forms(self) -> None:
        """初始化登录和注册表单"""
        # 登录表单回调
        login_callbacks = LoginCallbacks(self)
        
        # 注册表单回调
        register_callbacks = RegisterCallbacks(self)
        
        # 创建登录表单
        self.login_form = LoginForm(
            parent=self.form_container,
            user_manager=self.user_manager,
            callbacks=login_callbacks
        )
        
        # 创建注册表单
        self.register_form = RegisterForm(
            parent=self.form_container,
            user_manager=self.user_manager,
            callbacks=register_callbacks
        )
    
    def tkraise(self):
        """
        当页面被提升显示时调用，获取并传递登录上下文
        """
        super().tkraise()
        # 从AppController获取登录上下文
        login_context = self.app_controller.get_login_context()
        # 将上下文传递给登录和注册表单
        if hasattr(self, 'login_form'):
            self.login_form.login_context = login_context
        if hasattr(self, 'register_form'):
            self.register_form.login_context = login_context
    
    def show_login_form(self) -> None:
        """显示登录表单"""
        self.current_form = "login"
        self.register_form.pack_forget()
        self.login_form.pack(fill=tk.BOTH, expand=True)
        self.login_form.clear_form()
        self.login_form.focus_username()
    
    def show_register_form(self) -> None:
        """显示注册表单"""
        self.current_form = "register"
        self.login_form.pack_forget()
        self.register_form.pack(fill=tk.BOTH, expand=True)
        self.register_form.clear_form()
        self.register_form.focus_username()
    
    def handle_login_success(self) -> None:
        """处理登录成功事件"""
        # 登录成功，跳转到首页
        self.app_controller.nav_to_home()
    
    def handle_register_success(self) -> None:
        """处理注册成功事件"""
        # 注册成功，切换到登录表单，方便用户直接登录
        self.show_login_form()
        # 可以添加注册成功的提示
        self.login_form.error_var.set("注册成功，请使用新账号登录")


class LoginCallbacks(LoginFormCallbacksProtocol):
    """登录表单回调实现"""
    
    def __init__(self, page: LoginRegisterPage):
        """
        初始化登录回调
        :param page: 登录注册页面实例
        """
        self.page = page
    
    def on_login_success(self) -> None:
        """登录成功回调"""
        self.page.handle_login_success()
    
    def on_switch_to_register(self) -> None:
        """切换到注册表单回调"""
        self.page.show_register_form()


class RegisterCallbacks(RegisterFormCallbacksProtocol):
    """注册表单回调实现"""
    
    def __init__(self, page: LoginRegisterPage):
        """
        初始化注册回调
        :param page: 登录注册页面实例
        """
        self.page = page
    
    def on_register_success(self) -> None:
        """注册成功回调"""
        self.page.handle_register_success()
    
    def on_switch_to_login(self) -> None:
        """切换到登录表单回调"""
        self.page.show_login_form()
