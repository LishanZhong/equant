import threading
import time

class QuantThread(threading.Thread):
    '''程序化线程类，支持启动/暂停/恢复/停止'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flag = threading.Event()     # 用于暂停线程的标识
        self._flag.set()                   # 设置为True
        self._running = threading.Event()  # 用于停止线程的标识
        self._running.set()                # 将running设置为True
        self._terminate = False
        
    def handle(self):
        #不能直接调用super().run()，有bug
        if self._target:
            self._target(*self._args, **self._kwargs)
        
    def terminate(self):
        return self._terminate

    def run(self):
        while self._running.isSet():
            self._flag.wait()              # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            self.handle()
            
    def pause(self):
        self._terminate = True
        self._flag.clear()                 # 设置为False, 让线程阻塞

    def resume(self):
        self._terminate = False
        self._flag.set()                   # 设置为True, 让线程停止阻塞

    def stop(self):
        self._terminate = True
        self._flag.set()                   # 将线程从暂停状态恢复, 如何已经暂停的话
        self._running.clear()              # 设置为False