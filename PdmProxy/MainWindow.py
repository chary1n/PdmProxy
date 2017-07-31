# -*- coding: utf-8 -*-
import threading
from Tkinter import Tk, Label, StringVar

import tornado
from tornado.options import parse_command_line, options, define
# class Singleton(object):
#     def __new__(cls, *args, **kw):
#         if not hasattr(cls, '_instance'):
#             orig = super(Singleton, cls)
#             cls._instance = orig.__new__(cls, *args, **kw)
#         return cls._instance


class MainWindow(object):


    def __init__(self, title="Pdm Proxy", width=500, height=300):
        # self.a = "1111"
        self.main_window = Tk()
        self.main_window.title(title)
        self.center_window(width, height)
        Label(self.main_window, text=u'代理服务器已开启').pack()
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
        from Handler import UploadFileHandler, DownloadFileHandler, GetProgress, MainHandler
        app = tornado.web.Application(
            handlers=[
                ('/',MainHandler),
                ('/uploadfile', UploadFileHandler),
                ('/downloadfile', DownloadFileHandler),
                ('/getprogress', GetProgress)
            ],
            debug= False,
            )
        print(u'服务器开启中')
        app.listen(options.port)
        # http_server = tornado.httpserver.HTTPServer(app)
        # http_server.bind(options.port)
        # http_server.start(1)
        print(u'服务器已开启')
        tornado.ioloop.IOLoop.instance().start()
