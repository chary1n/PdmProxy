# -*- coding: utf-8 -*-
import logging
import threading
from Tkinter import Tk, Label

import tornado
from tornado.options import parse_command_line, options, define
# class Singleton(object):
#     def __new__(cls, *args, **kw):
#         if not hasattr(cls, '_instance'):
#             orig = super(Singleton, cls)
#             cls._instance = orig.__new__(cls, *args, **kw)
#         return cls._instance
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
_logger.addHandler(ch)


class MainWindow(object):


    def __init__(self, title="Pdm Proxy", width=500, height=300):
        # self.a = "1111"
        self.main_window = Tk()
        self.main_window.title(title)
        self.center_window(width, height)
        self.label = Label(self.main_window, text=u'代理服务器未开启')
        self.label.pack()
        self.progress = Label(self.main_window, text=u'暂无进行中的操作...')
        self.progress.pack()
        # Button(self.main_window, text=u"开启服务器", command=lambda: self.thread_it(self.startServer)).pack()
        # self.file_progress_label = Label(self.main_window, text=self.a)
        # self.file_progress_label.pack()

    def mainloop(self):
        self.main_window.mainloop()

    def get_screen_size(self, window):
        return window.winfo_screenwidth(),window.winfo_screenheight()

    def get_window_size(self, window):
        return window.winfo_reqwidth(),window.winfo_reqheight()

    def center_window(self, width, height):
        screenwidth = self.main_window.winfo_screenwidth()
        screenheight = self.main_window.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        # print(size)
        self.main_window.geometry(size)

    def thread_it(self, func, *args):
        # 创建
        t = threading.Thread(target=func, args=args)
        # 守护 !!!
        t.setDaemon(True)
        # 启动
        t.start()
        # 阻塞--卡死界面！
        # t.join()

    def startServer(self):
        define('port', default=8088, help='run this port', type=int)
        parse_command_line()
        from Handler import UploadFileHandler, DownloadFileHandler, GetProgress, MainHandler, OpenFileBrowserHandler
        app = tornado.web.Application(
            handlers=[
                ('/', MainHandler),
                ('/uploadfile', UploadFileHandler),
                ('/downloadfile', DownloadFileHandler),
                ('/getprogress', GetProgress),
                ('/open_file_browser', OpenFileBrowserHandler)
            ],
            debug= False,
            )
        self.label['text'] = u'服务器开启中'
        self.main_window.update()
        _logger.info(u"服务器开启中")
        try:
            app.listen(options.port)
        except Exception as e:
            self.label['text'] = e
            self.main_window.update()
        self.label['text'] = u'服务器已开启'
        self.main_window.update()
        # http_server = tornado.httpserver.HTTPServer(app)
        # http_server.bind(options.port)
        # http_server.start(1)
        # print(u'服务器已开启')
        tornado.ioloop.IOLoop.instance().start()

