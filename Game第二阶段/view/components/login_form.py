import tkinter as tk
from tkinter import ttk
from typing import Protocol, Callable, Dict


class FormValidator:
    """表单验证器"""
    def __init__(self):
        self.rules = []
    
    def add_rule(self, field: str, validator: Callable[[str], tuple[bool, str]]):
        """添加验证规则"""
        self.rules.append((field, validator))
    
    def validate(self, data: Dict[str, str]) -> tuple[bool, str]:
        """执行验证"""
        for field, validator in self.rules:
            valid, message = validator(data.get(field, ""))
            if not valid:
                return False, message
        return True, ""


class UserManagerProtocol(Protocol):
    """用户管理器协议"""
    def login(self, username: str, password: str, session_id: str = None) -> tuple[bool, str]:
        ...


class LoginFormCallbacksProtocol(Protocol):
    """登录表单回调协议"""
    def on_login_success(self) -> None:
        ...
    
    def on_switch_to_register(self) -> None:
        ...


class LoginForm(ttk.LabelFrame):
    """登录表单组件"""
    
    # UI配置常量
    UI_CONFIG = {
        "FRAME_TEXT": "用户登录",
        "PADDING": "20",
        "USERNAME_LABEL": "用户名：",
        "PASSWORD_LABEL": "密码：",
        "LOGIN_BUTTON_TEXT": "登录",
        "REGISTER_LINK_TEXT": "没有账号？注册",
        "SUCCESS_MESSAGE": "登录成功！",
        "ERROR_MESSAGE_PREFIX": "登录失败："
    }
    
    def __init__(self, parent: tk.Widget, user_manager: UserManagerProtocol,
                 callbacks: LoginFormCallbacksProtocol, config: Dict[str, str] = None):
        """
        初始化登录表单组件
        :param parent: 父窗口
        :param user_manager: 用户管理器
        :param callbacks: 回调函数集合
        :param config: 自定义配置
        """
        self.config = {**self.UI_CONFIG, **(config or {})}
        super().__init__(parent, text=self.config["FRAME_TEXT"], padding=self.config["PADDING"])
        
        # 依赖注入
        self.user_manager = user_manager
        self.callbacks = callbacks
        self.is_submitting = False  # 表单提交状态
        self.login_context = None  # 登录上下文，用于标识不同玩家会话
        
        # 设置表单验证器
        self._setup_validator()
        
        # 设置组件
        self.setup_widgets()
    
    def _setup_validator(self) -> None:
        """设置表单验证器"""
        self.validator = FormValidator()
        self.validator.add_rule("username", lambda v: (bool(v.strip()), "请输入用户名"))
        self.validator.add_rule("password", lambda v: (bool(v.strip()), "请输入密码"))
    
    def setup_widgets(self) -> None:
        """设置组件"""
        # 表单容器
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self._setup_username_field(form_frame)
        self._setup_password_field(form_frame)
        self._setup_error_display(form_frame)
        self._setup_buttons(form_frame)
        self._setup_bindings()
    
    def _setup_username_field(self, parent: ttk.Frame) -> None:
        """设置用户名输入区"""
        username_frame = ttk.Frame(parent)
        username_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(username_frame, text=self.config["USERNAME_LABEL"], width=10).pack(side=tk.LEFT, padx=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _setup_password_field(self, parent: ttk.Frame) -> None:
        """设置密码输入区"""
        password_frame = ttk.Frame(parent)
        password_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(password_frame, text=self.config["PASSWORD_LABEL"], width=10).pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, width=30, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _setup_error_display(self, parent: ttk.Frame) -> None:
        """设置错误信息显示区"""
        self.error_var = tk.StringVar()
        error_label = ttk.Label(parent, textvariable=self.error_var, foreground="red", wraplength=300)
        error_label.pack(fill=tk.X, expand=True, pady=10)
    
    def _setup_buttons(self, parent: ttk.Frame) -> None:
        """设置按钮区"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, expand=True, pady=10)
        
        # 登录按钮
        self.login_button = ttk.Button(button_frame, text=self.config["LOGIN_BUTTON_TEXT"], 
                                      command=self.handle_login, style="Primary.TButton")
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # 注册链接
        register_link = ttk.Label(button_frame, text=self.config["REGISTER_LINK_TEXT"], 
                                 foreground="blue", cursor="hand2")
        register_link.pack(side=tk.RIGHT, padx=5)
        register_link.bind("<Button-1>", lambda _: self.callbacks.on_switch_to_register())
    
    def _setup_bindings(self) -> None:
        """设置事件绑定"""
        # 绑定回车键登录
        self.username_entry.bind("<Return>", lambda _: self.handle_login())
        self.password_entry.bind("<Return>", lambda _: self.handle_login())
    
    def handle_login(self) -> None:
        """处理登录逻辑"""
        # 防止重复提交
        if self.is_submitting:
            return
        
        # 清空错误信息
        self.error_var.set("")
        
        # 获取用户输入
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # 表单验证
        data = {"username": username, "password": password}
        valid, message = self.validator.validate(data)
        if not valid:
            self.error_var.set(message)
            return
        
        # 设置提交状态
        self.is_submitting = True
        self.login_button.config(state=tk.DISABLED)  # 禁用登录按钮
        
        try:
            # 调用用户管理器进行登录，传递登录上下文作为会话ID
            success, message = self.user_manager.login(username, password, self.login_context)
            
            if success:
                # 登录成功
                self.error_var.set(self.config["SUCCESS_MESSAGE"])
                self.callbacks.on_login_success()
            else:
                # 登录失败，显示错误信息
                self.error_var.set(f"{self.config['ERROR_MESSAGE_PREFIX']}{message}")
        finally:
            # 恢复状态
            self.is_submitting = False
            self.login_button.config(state=tk.NORMAL)  # 恢复登录按钮
    
    def clear_form(self) -> None:
        """清空表单内容"""
        self.username_var.set("")
        self.password_var.set("")
        self.error_var.set("")
    
    def focus_username(self) -> None:
        """将焦点设置到用户名输入框"""
        self.username_entry.focus_set()
