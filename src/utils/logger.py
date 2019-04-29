import logging
import sys
from multiprocessing import Queue, Process
from capi.com_types import *

class Test(object):
    def __init__(self):
        self.data = "daaa"

class MyHandlerText(logging.StreamHandler):
    '''put log to Tkinter Text'''
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self) # initialize parent
        self.textctrl = textctrl

    def emit(self, record):
        msg = self.format(record)
        self.textctrl.config(state="normal")
        self.textctrl.insert("end", msg + "\n")
        self.flush()
        self.textctrl.config(state="disabled")

class MyHandlerQueue(logging.StreamHandler):
    def __init__(self, gui_queue, sig_queue, err_queue):
        logging.StreamHandler.__init__(self)  # initialize parent
        self.gui_queue = gui_queue
        self.sig_queue = sig_queue
        self.err_queue = err_queue

    def emit(self, record):
        #最多等待1秒
        # TODO: 先判断msg的消息体（json?)
        target = record.msg[1]
        record.msg = record.msg[0]
        msg = self.format(record)
        if target == EEQU_LOG_TYPE_SIGNAL:
            self.sig_queue.put(msg, block=False, timeout=1)
        elif target == EEQU_LOG_TYPE_ERROR:
            self.err_queue.put(msg, block=False, timeout=1)
        else:
            self.gui_queue.put(msg, block=False, timeout=1)

class Logger(object):
    def __init__(self):
        #process queue
        self.log_queue = Queue()
        self.gui_queue = Queue()
        # 信号队列
        self.sig_queue = Queue()
        self.err_queue = Queue()

        #logger config
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("[%(levelname)7s][%(asctime)-15s]: %(message)s")

        self.level_dict = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARN":logging.WARN, "ERROR":logging.ERROR}
        self.level_func = {"DEBUG":self.logger.debug, "INFO":self.logger.info, "WARN": self.logger.warning, "ERROR": self.logger.error}

    def run(self):
        '''从log_queue中获取日志，刷新到文件和控件上'''
        while True:
            data_list = self.log_queue.get()
            if data_list is None: break
            #数据格式不对
            if len(data_list) !=3: continue
            self.level_func[data_list[0]](data_list[1:])

    def _log(self, level, target, s):
        data = []
        data.append(level)
        data.append(target)
        data.append(s)
        self.log_queue.put(data)

    def get_log_queue(self):
        return self.log_queue

    def getGuiQ(self):
        return self.gui_queue

    def getSigQ(self):
        return self.sig_queue

    def getErrQ(self):
        return self.err_queue

    def add_handler(self):
        #设置文件句柄
        file_handler = logging.FileHandler(r"./log/equant.log", mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        #设置窗口句柄
        gui_handler = MyHandlerQueue(self.gui_queue, self.sig_queue, self.err_queue)
        gui_handler.setLevel(logging.DEBUG)
        gui_handler.setFormatter(self.formatter)
        self.logger.addHandler(gui_handler)
        #设置控制台句柄
        cout_handler = logging.StreamHandler(sys.stdout)
        cout_handler.setLevel(logging.DEBUG)
        cout_handler.setFormatter(self.formatter)
        self.logger.addHandler(cout_handler)

    def debug(self, s, target=""):
        # self._log("DEBUG", s, target)
        pass

    def info(self, s, target=""):
        # self._log("INFO", s, target)
        pass

    def warn(self, s, target=""):
        # self._log("WARN", s, target)
        pass

    def error(self, s, target=""):
        self._log("ERROR", s, target)

    def sig_info(self, s, target=EEQU_LOG_TYPE_SIGNAL):
        self.info(s, target)

    # 策略错误
    def err_error(self, s, target=EEQU_LOG_TYPE_ERROR):
        self.error(s, target)
