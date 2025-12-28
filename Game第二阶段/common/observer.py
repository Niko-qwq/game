from functools import wraps

class Subject:
    """被观察者基类，实现观察者模式"""
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, *args, **kwargs):
        """通知所有观察者"""
        for observer in self._observers:
            observer.update(self, *args, **kwargs)


class Observer:
    """观察者基类，实现观察者模式"""
    
    def update(self, subject, *args, **kwargs):
        """当被观察者状态改变时，调用此方法"""
        pass

def auto_notify(func):
    """装饰器：方法执行成功后自动 notify"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # 约定：如果方法返回 False 或 (False, msg)，则不刷新
        # 如果返回 None (无返回值) 或 True 或 (True, msg)，则刷新
        should_notify = True
        if isinstance(result, bool) and not result:
            should_notify = False
        elif isinstance(result, tuple) and len(result) > 0 and result[0] is False:
            should_notify = False
            
        if should_notify:
            self.notify()
        return result
    return wrapper
