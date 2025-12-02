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
