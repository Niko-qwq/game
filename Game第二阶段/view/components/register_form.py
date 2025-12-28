import tkinter as tk
from tkinter import ttk
from typing import Protocol, Callable, Dict


class UserManagerProtocol(Protocol):
    """用户管理器协议"""
    def register(self, username: str, password: str) -> tuple[bool, str]:
        ...


class RegisterFormCallbacksProtocol(Protocol):
    """注册表单回调协议"""
    def on_register_success(self) -> None:
        ...
    
    def on_switch_to_login(self) -> None:
        ...


class FormValidator:
    """表单验证器"""
    def __init__(self):
        self.rules = []
    
    def add_rule(self, field: str, validator: Callable[[Dict[str, str]], tuple[bool, str]]):
        """添加验证规则"""
        self.rules.append((field, validator))
    
    def validate(self, data: Dict[str, str]) -> tuple[bool, str]:
        """执行验证"""
        for field, validator in self.rules:
            valid, message = validator(data)
            if not valid:
                return False, message
        return True, ""


class RegisterForm(ttk.LabelFrame):
    """注册表单组件"""
    
    # UI配置常量
    UI_CONFIG = {
        "FRAME_TEXT": "用户注册",
        "PADDING": "20",
        "USERNAME_LABEL": "用户名：",
        "PASSWORD_LABEL": "密码：",
        "CONFIRM_PASSWORD_LABEL": "确认密码：",
        "REGISTER_BUTTON_TEXT": "注册",
        "LOGIN_LINK_TEXT": "已有账号？登录",
        "SUCCESS_MESSAGE": "注册成功！",
        "ERROR_MESSAGE_PREFIX": "注册失败："
    }
    
    def __init__(self, parent: tk.Widget, user_manager: UserManagerProtocol,
                 callbacks: RegisterFormCallbacksProtocol, config: Dict[str, str] = None):
        """
        初始化注册表单组件
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
        self.login_context = None  # 登录上下文，用于保持一致性和未来扩展性
        
        # 设置表单验证器
        self._setup_validator()
        
        # 设置组件
        self.setup_widgets()
    
    def _setup_validator(self) -> None:
        """设置表单验证器"""
        self.validator = FormValidator()
        
        # 用户名验证
        self.validator.add_rule("username", lambda data: (
            bool(data.get("username", "").strip()),
            "请输入用户名"
        ))
        
        self.validator.add_rule("username_length", lambda data: (
            len(data.get("username", "").strip()) >= 3,
            "用户名长度至少为3个字符"
        ))
        
        self.validator.add_rule("username_max_length", lambda data: (
            len(data.get("username", "").strip()) <= 20,
            "用户名长度不能超过20个字符"
        ))
        
        # 密码验证
        self.validator.add_rule("password", lambda data: (
            bool(data.get("password", "").strip()),
            "请输入密码"
        ))
        
        self.validator.add_rule("password_length", lambda data: (
            len(data.get("password", "").strip()) >= 6,
            "密码长度至少为6个字符"
        ))
        
        # 确认密码验证
        self.validator.add_rule("confirm_password", lambda data: (
            bool(data.get("confirm_password", "").strip()),
            "请确认密码"
        ))
        
        self.validator.add_rule("password_match", lambda data: (
            data.get("password", "").strip() == data.get("confirm_password", "").strip(),
            "两次输入的密码不一致"
        ))
    
    def setup_widgets(self) -> None:
        """设置组件"""
        # 表单容器
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self._setup_username_field(form_frame)
        self._setup_password_field(form_frame)
        self._setup_confirm_password_field(form_frame)
        self._setup_error_display(form_frame)
        self._setup_buttons(form_frame)
        self._setup_bindings()
    
    def _setup_username_field(self, parent: ttk.Frame) -> None:
        """设置用户名输入区"""
        username_frame = ttk.Frame(parent)
        username_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(username_frame, text=self.config["USERNAME_LABEL"], width=12).pack(side=tk.LEFT, padx=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _setup_password_field(self, parent: ttk.Frame) -> None:
        """设置密码输入区"""
        password_frame = ttk.Frame(parent)
        password_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(password_frame, text=self.config["PASSWORD_LABEL"], width=12).pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, width=30, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _setup_confirm_password_field(self, parent: ttk.Frame) -> None:
        """设置确认密码输入区"""
        confirm_frame = ttk.Frame(parent)
        confirm_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(confirm_frame, text=self.config["CONFIRM_PASSWORD_LABEL"], width=12).pack(side=tk.LEFT, padx=5)
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = ttk.Entry(confirm_frame, textvariable=self.confirm_password_var, width=30, show="*")
        self.confirm_password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _setup_error_display(self, parent: ttk.Frame) -> None:
        """设置错误信息显示区"""
        self.error_var = tk.StringVar()
        error_label = ttk.Label(parent, textvariable=self.error_var, foreground="red", wraplength=300)
        error_label.pack(fill=tk.X, expand=True, pady=10)
    
    def _setup_buttons(self, parent: ttk.Frame) -> None:
        """设置按钮区"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, expand=True, pady=10)
        
        # 注册按钮
        self.register_button = ttk.Button(button_frame, text=self.config["REGISTER_BUTTON_TEXT"], 
                                        command=self.handle_register, style="Primary.TButton")
        self.register_button.pack(side=tk.LEFT, padx=5)
        
        # 登录链接
        login_link = ttk.Label(button_frame, text=self.config["LOGIN_LINK_TEXT"], 
                              foreground="blue", cursor="hand2")
        login_link.pack(side=tk.RIGHT, padx=5)
        login_link.bind("<Button-1>", lambda _: self.callbacks.on_switch_to_login())
    
    def _setup_bindings(self) -> None:
        """设置事件绑定"""
        # 绑定回车键注册
        self.username_entry.bind("<Return>", lambda _: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda _: self.confirm_password_entry.focus_set())
        self.confirm_password_entry.bind("<Return>", lambda _: self.handle_register())
    
    def handle_register(self) -> None:
        """处理注册逻辑"""
        # 防止重复提交
        if self.is_submitting:
            return
        
        # 清空错误信息
        self.error_var.set("")
        
        # 获取用户输入
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()
        
        # 表单验证
        data = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password
        }
        valid, message = self.validator.validate(data)
        if not valid:
            self.error_var.set(message)
            return
        
        # 设置提交状态
        self.is_submitting = True
        self.register_button.config(state=tk.DISABLED)  # 禁用注册按钮
        
        try:
            # 调用用户管理器进行注册
            success, message = self.user_manager.register(username, password)
            
            if success:
                # 注册成功
                self.error_var.set(self.config["SUCCESS_MESSAGE"])
                self.callbacks.on_register_success()
            else:
                # 注册失败，显示错误信息
                self.error_var.set(f"{self.config['ERROR_MESSAGE_PREFIX']}{message}")
        finally:
            # 恢复状态
            self.is_submitting = False
            self.register_button.config(state=tk.NORMAL)  # 恢复注册按钮
    
    def clear_form(self) -> None:
        """清空表单内容"""
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.error_var.set("")
    
    def focus_username(self) -> None:
        """将焦点设置到用户名输入框"""
        self.username_entry.focus_set()
