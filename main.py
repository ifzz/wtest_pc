#!/usr/bin/python34
#-*-coding:gbk-*-

import dbinit
import interface
from tkinter import *


if __name__ == '__main__':
    root = Tk()
    root.geometry('1100x600+100+50')
    root.title(string='委托服务端测试工具')
    root.iconbitmap('console.ico')
    app = interface.App(root)
    root.mainloop()
