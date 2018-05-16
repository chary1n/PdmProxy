# -*- coding: utf-8 -*-
import logging
import socket

from MainWindow import MainWindow
import global_d
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
_logger.addHandler(ch)

global_d._init()
global root
if __name__ == '__main__':
    root = MainWindow(width=500, height=300)
    global_d.set_value('root', root)
    root.thread_it(MainWindow.startServer, root)
    # _logger.error("asdsadas")
    root.mainloop()
    # try:
    #     root.startServer()
    # except socket.error as e:
#     print(u'端口被占用,不能重复启动此程序。')