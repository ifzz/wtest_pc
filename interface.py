#!/usr/bin/python34
#-*-coding:gbk-*-

import os
import re
import json
import dbinit
import config
import asyncio
import autotest
import collections
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox


class App:
    def __init__(self, parent):
        self.scheme_list = config.readschemelist()
        self.current_scheme, self.server_ip, self.server_port, self.qs_id = config.readbackup()
        self.func_object = autotest.Func(self.server_ip, self.server_port, self.qs_id)
        self.func_object.readdict()
        self.func_object.write_json()
        self.mongo_object = dbinit.Mongo(self.current_scheme)
        
        self.parent = parent
        self.value_of_combo2 = '11100客户校验'
        self.ft = font.Font(family = '微软雅黑',size = 9,weight = font.BOLD)
        #self.parent.option_add("*TCombobox*Listbox*Font", self.ft)
        self.parent.option_add("*Font", self.ft)
        self.num = 0

        #-------------------组件使用多列（多行）-------------------------------
        # columnspan：指定使用几列
        # rowspan：指定使用几行
    
        #-------------------设置对齐属性----------------------------------------------
        # sticky：设置组件对齐方式
        # 默认属性下，组件的对齐方式为居中，设置sticky 属性可以控制对齐方式，可用的值
        #（N,S,E,W）及其组合值
    
        self.frame1 = ttk.Frame(self.parent)
        self.frame2 = ttk.Frame(self.parent)
        self.frame3 = ttk.Frame(self.parent, padding=(10,0,0,0))
        self.labelframe1 = ttk.LabelFrame(self.frame1,text = '功能配置')
        self.labelframe2 = ttk.LabelFrame(self.frame2,text = '参数配置')
        self.labelframe3 = ttk.LabelFrame(self.frame2,text = '预留配置')
    
        self.frame1.grid(row=0, rowspan=26, column=0, columnspan=2, sticky=(N, S, W))
        self.frame2.grid(row=0, rowspan=5, column=2, columnspan=4, sticky=(N, E, W)) 
        self.frame3.grid(row=11, rowspan=2, column=2, columnspan=7, sticky=(N, W, E, S)) 
    
        #fram1
        label8 = ttk.Label(self.frame1,text = '功能:',font = self.ft)       
        self.combobox1_value = StringVar()
        self.combobox1 = ttk.Combobox(self.frame1,textvariable=self.combobox1_value,width=40,height=30,font=self.ft)
        self.combobox1.bind("<<ComboboxSelected>>", self.combo1_selection)
        self.combobox1.bind("<Return>", self.search_func)
                
        self.labelframe1.grid(row = 1,rowspan = 30,column = 0,columnspan = 2,padx = 10,pady = 2,sticky = (N, S, W))
        label8.grid(row = 0,column = 0,padx = 10,pady = 2,sticky = W)
        self.combobox1.grid(row = 0,column = 1,padx = 0,pady = 2,sticky = EW)  
    
        #fram2
        label1 = ttk.Label(self.frame2,text = '当前方案:',font = self.ft)
        label2 = ttk.Label(self.labelframe2,text = 'IP地址:',font = self.ft)
        label3 = ttk.Label(self.labelframe2,text = '端口:',font = self.ft)
        label4 = ttk.Label(self.labelframe2,text = '券商ID:',font = self.ft)
        label5 = ttk.Label(self.labelframe2,text = '接收超时(s):',font = self.ft)
        label6 = ttk.Label(self.labelframe2,text = '手机号:',font = self.ft)
        label7 = ttk.Label(self.labelframe2,text = '通讯密码:',font = self.ft)
    
        label11 = ttk.Label(self.labelframe3,text = '预留:',font = self.ft)
        label12 = ttk.Label(self.labelframe3,text = '预留:',font = self.ft)
        label13 = ttk.Label(self.labelframe3,text = '预留:',font = self.ft)
        label14 = ttk.Label(self.labelframe3,text = '预留:',font = self.ft)         
    
        self.combobox2_value = StringVar()
        self.combobox2 = ttk.Combobox(self.frame2, textvariable=self.combobox2_value, state='readonly', font=self.ft)
        self.combobox2.bind("<<ComboboxSelected>>", self.combo2_selection)
        self.combobox2['values'] = self.scheme_list
    
        self.ent1_value = StringVar()
        self.ent2_value = StringVar()
        self.ent3_value = StringVar()
        self.ent4_value = StringVar()
        self.ent5_value = StringVar()
        self.ent6_value = StringVar()
        self.ent1 = ttk.Entry(self.labelframe2,textvariable = self.ent1_value)
        self.ent2 = ttk.Entry(self.labelframe2,textvariable = self.ent2_value)
        self.ent3 = ttk.Entry(self.labelframe2,textvariable = self.ent3_value)
        self.ent4 = ttk.Entry(self.labelframe2,textvariable = self.ent4_value)
        self.ent5 = ttk.Entry(self.labelframe2,textvariable = self.ent5_value)
        self.ent6 = ttk.Entry(self.labelframe2,textvariable = self.ent6_value)
    
        self.button1 = ttk.Button(self.frame2,text = '新增配置',state = 'normal',command = self.addconfig)
        self.button2 = ttk.Button(self.frame2,text = '删除配置',state = 'normal',command = self.delconfig)
        self.button3 = ttk.Button(self.labelframe2,text = '连接',state = 'normal',command = self.connect)
        self.button4 = ttk.Button(self.labelframe2,text = '断开',state = 'disabled',command = self.close)
        
        self.combobox2.set(self.current_scheme)
        self.ent1_value.set(self.server_ip)
        self.ent2_value.set(self.server_port)
        self.ent3_value.set(self.qs_id)
    
        label1.grid(row = 0,column = 2,padx = 10,pady = 10,sticky = (N, W))
        self.combobox2.grid(row = 0,column = 3,padx = 0,pady = 10,sticky = (N, W))
        self.button1.grid(row = 0,column = 4,padx = 10,pady = 10,sticky = (N, W))
        self.button2.grid(row = 0,column = 5,padx = 0,pady = 10,sticky = (N, W))
    
        self.labelframe2.grid(row = 1,rowspan = 4,column = 2,columnspan = 4,padx = 10,pady = 2,sticky = (N, W))
    
        label2.grid(row = 1,column = 2,padx = 10,pady = 2,sticky = (N, W))
        self.ent1.grid(row = 1,column = 3,padx = 0,pady = 2,sticky = (N, W))
        label3.grid(row = 1,column = 4,padx = 10,pady = 2,sticky = (N, W))
        self.ent2.grid(row = 1,column = 5,padx = 0,pady = 2,sticky = (N, W))
    
        label4.grid(row = 2,column = 2,padx = 10,pady = 2,sticky = (N, W))
        self.ent3.grid(row = 2,column = 3,padx = 0,pady = 2,sticky = (N, W))
        label5.grid(row = 2,column = 4,padx = 10,pady = 2,sticky = (N, W))
        self.ent4.grid(row = 2,column = 5,padx = 0,pady = 2,sticky = (N, W))
    
        label6.grid(row = 3,column = 2,padx = 10,pady = 2,sticky = (N, W))
        self.ent5.grid(row = 3,column = 3,padx = 0,pady = 2,sticky = (N, W))
        label7.grid(row = 3,column = 4,padx = 10,pady = 2,sticky = (N, W))
        self.ent6.grid(row = 3,column = 5,padx = 0,pady = 2,sticky = (N, W))
    
        self.button3.grid(row = 4,column = 4,padx = 0,pady = 2,sticky = (N, E))
        self.button4.grid(row = 4,column = 5,padx = 0,pady = 2,sticky = (N, E))
    
        self.labelframe3.grid(row = 5,rowspan = 4,column = 2,columnspan = 4,padx = 10,pady = 2,sticky = (N, W, E, S))
        label11.grid(row = 5,column = 2,padx = 10,pady = 2,sticky = (N, W))
        label12.grid(row = 6,column = 2,padx = 10,pady = 2,sticky = (N, W))
        label13.grid(row = 7,column = 2,padx = 10,pady = 2,sticky = (N, W))
        label14.grid(row = 8,column = 2,padx = 10,pady = 2,sticky = (N, W))
    
        self.lbox = Listbox(self.frame2, height=5, selectmode="extended")
        self.lbox.grid(row=0, rowspan=8, column=6, columnspan=2, padx = 0,pady = 2, sticky=(N, W, E, S))
        scrollbar1 = ttk.Scrollbar(self.frame2, orient=VERTICAL, command=self.lbox.yview)
        scrollbar1.grid(row=0, rowspan=8, column=8, padx = 0,pady = 2, sticky=(N, S))
        self.lbox['yscrollcommand'] = scrollbar1.set
        self.lbox.grid_columnconfigure(6, weight=1)
        self.frame2.grid_columnconfigure(6, weight=1)
        self.lbox.bind("<Double-1>", self.modify_scene)
         #自动初始化listbox列表
        self.lbox_init()
    
        self.button7 = ttk.Button(self.frame2,text = '新增场景',state = 'normal',width = 12, command = self.add_scene)
        self.button8 = ttk.Button(self.frame2,text = '删除场景',state = 'normal',width = 12, command = self.del_scene)  
        self.button7.grid(row = 8,column = 6,padx = 0,pady = 2,sticky = E)
        self.button8.grid(row = 8,column = 7,padx = 0,pady = 2,sticky = (E, W))        
    
        label9 = ttk.Label(self.frame2,text = '请求包:',font = self.ft)
        label10 = ttk.Label(self.frame2,text = '应答包:',font = self.ft)
        self.ent7_value = StringVar()
        self.ent8_value = StringVar()
        self.ent7 = ttk.Entry(self.frame2,textvariable = self.ent7_value)
        self.ent8 = ttk.Entry(self.frame2,textvariable = self.ent8_value)         
        self.button5 = ttk.Button(self.frame2,text = '自动化测试',state = 'normal',command = self.atuo_test)
        self.button6 = ttk.Button(self.frame2,text = '单功能测试',state = 'disabled',
                                  command = lambda: self.functest(self.ent7.get()))                                                       
    
        label9.grid(row = 9,column = 2,padx = 10,pady = 2,sticky = (E, W))
        self.ent7.grid(row = 9,column = 3,columnspan = 4,padx = 0,pady = 2,sticky = (E, W))
        label10.grid(row = 10,column = 2,padx = 10,pady = 0,sticky = (E, W))
        self.ent8.grid(row = 10,column = 3,columnspan = 4,padx = 0,pady = 0,sticky = (E, W))
        self.button5.grid(row = 9,column = 7,padx = 0,pady = 2,sticky = (E, W))
        self.button6.grid(row = 10,column = 7,padx = 0,pady = 2,sticky = (E, W))
    
        #frame3
        self.tree = ttk.Treeview(self.frame3, selectmode="extended")
        scrollbar2 = ttk.Scrollbar(self.frame3, orient=HORIZONTAL, command=self.tree.xview)
        scrollbar3 = ttk.Scrollbar(self.frame3, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(xscroll=scrollbar2.set, yscroll=scrollbar3.set)
        self.tree.bind("<Button-3>", self.copy_value)
    
        self.tree.grid(row = 11,column = 2,columnspan = 6,padx = 0,pady = 2,sticky = (N, S, E, W))
        scrollbar2.grid(row=12, column=2, columnspan = 6, sticky=(E, W))
        scrollbar3.grid(row=11, rowspan=2, column=8, padx = 0,pady = 2, sticky=(N, S))       
    
        self.ent7.grid_columnconfigure(3, weight=1)
        self.ent8.grid_columnconfigure(3, weight=1)
        self.tree.grid_rowconfigure(11, weight=1)
        self.tree.grid_columnconfigure(2, weight=1)
        self.frame3.grid_rowconfigure(11, weight=1)
        self.frame3.grid_columnconfigure(2, weight=1)
        self.parent.grid_rowconfigure(11, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        
        #功能选项界面初始化
        self.init_function()
        
    def lbox_init(self):
        #从mongodb取lbox的items列表
        self.mongo_object.db_init()
        self.lbox.delete(0, 'end')
        for item in self.mongo_object.case:
            self.lbox.insert('end', item["_id"])
    
        # Colorize alternating lines of the listbox
        for i in range(0, len(self.mongo_object.case), 2):
            self.lbox.itemconfigure(i, background='#f0f0ff')
        
    def addconfig(self):
        self.toplevel = Toplevel(self.parent, borderwidth=10)
        self.toplevel.geometry('250x150+560+300')
        self.toplevel.title(string='添加配置方案')
        self.toplevel.iconbitmap('console.ico')
        self.toplevel.resizable(FALSE,FALSE)
    
        label13 = ttk.Label(self.toplevel,text = '新增方案名称:',font = self.ft)
        self.ent9_value = StringVar()
        self.ent9 = ttk.Entry(self.toplevel,textvariable = self.ent9_value,width = 19)
        self.onoff = StringVar()
        self.onoff.set(0)        
        self.checkbutton = ttk.Checkbutton(self.toplevel, variable = self.onoff, text = '保存当前配置')
        self.button11 = ttk.Button(self.toplevel,text = '确定',state = 'normal',command = self.saveconfig)
        self.button12 = ttk.Button(self.toplevel,text = '取消',state = 'normal',command = self.cancel)
        
        label13.grid(row = 0,column = 0,padx = 0,pady = 8,sticky = (N, S, E, W))
        self.ent9.grid(row = 0,column = 1,padx = 0,pady = 8,sticky = (N, S, E, W))
        self.checkbutton.grid(row = 1,column = 0,padx = 0,pady = 8,sticky = (N, S, W))
        self.button11.grid(row = 2,column = 0,padx = 0,pady = 8,sticky = (N, S, W))
        self.button12.grid(row = 2,column = 1,padx = 0,pady = 8,sticky = (N, S, W))
        self.parent.attributes('-disabled', 1)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.cancel)
        self.toplevel.focus_set()
        
    def saveconfig(self):
        self.newly_scheme = self.ent9.get()
        self.server_ip = self.ent1.get()
        self.server_port = self.ent2.get()
        self.qs_id = self.ent3.get()

        if self.newly_scheme == '' or self.server_ip == '' or self.server_port == '' or self.qs_id == '':
            messagebox.showerror(title = '提示', message = '新增方案/IP地址/端口/券商ID不能为空！')
            self.toplevel.deiconify()
        else:
            if self.newly_scheme in self.combobox2['values']:
                messagebox.showerror(title = '提示', message = '新增方案已存在！')
                self.toplevel.deiconify()
            else:
                config.writebackup(self.newly_scheme, self.server_ip, self.server_port, self.qs_id)
                valueslist = list(self.combobox2['values'])
                if self.newly_scheme not in valueslist:
                    valueslist.append(self.newly_scheme)          
                self.combobox2['values'] = valueslist
                self.combobox2.set(self.newly_scheme)
                if self.onoff.get() == 1:
                    import shutil
                    shutil.copyfile("dictionary\\" + self.combobox1.get() + ".ini", 
                                    "dictionary\\" + self.ent9_value.get() + ".ini")
                messagebox.showinfo(title = '提示', message = '券商配置保存成功！')
                self.mongo_object = dbinit.Mongo(self.newly_scheme)
                #自动初始化listbox列表
                self.lbox_init()
                self.parent.attributes('-disabled', 0)
                self.toplevel.destroy()
    
    def delconfig(self):
        if messagebox.askyesno(title = '提示', message = '确认删除？'):
            delvalue = self.combobox2.get()
            valueslist = list(self.combobox2['values'])
            valueslist.remove(delvalue)      
            self.combobox2['values'] = valueslist
            if valueslist != []:
                curvalue = valueslist[-1]
            else:
                curvalue = ''
            _, self.server_ip, self.server_port, self.qs_id = config.readbackup(curvalue)
            self.combobox2.set(curvalue)
            self.ent1_value.set(self.server_ip)
            self.ent2_value.set(self.server_port)
            self.ent3_value.set(self.qs_id)
            config.deletebackup(delvalue, curvalue)
            self.mongo_object = dbinit.Mongo(curvalue)
            #自动初始化listbox列表
            self.lbox_init()            
            
    def copy_value(self, event):
        templist = []
        for s in self.tree.selection():
            item=self.tree.item(s)
            print(item["values"])
            templist.append(item["values"])
        self.tree.clipboard_clear()
        self.tree.clipboard_append(tuple(templist))
        messagebox.showinfo(title='提示', message='已复制到剪切板')
        
    def combo1_selection(self, event):
        items = map(lambda zd: str(zd)+' '+self.func_object.zd_interpret_dic[zd], 
                   self.func_object.request_gn_zd_dict[self.combobox1.get()[:5]])       
        for widget in self.labelframe1.grid_slaves():
            widget.destroy()
            
        self.request_data = ''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(self.combobox1.get()[:5],self.func_object.guid))
        num = 0
        for i in items:
            num = num + 1
            #取备份文件中的value
            tempvalue = config.readfunc(self.combobox2.get(), self.combobox1.get()[:5], i[:4])
            templabel = ttk.Label(self.labelframe1,text = i+':',font = self.ft,width = 20)
            templabel.grid(row = num,column = 0,padx = 2,sticky = W)
            tempentry = ttk.Entry(self.labelframe1,width = 25)        
            tempentry.grid(row = num,column = 1,padx = 2,sticky = E)
            tempentry.insert(0, tempvalue)
            tempentry.bind('<KeyRelease>', self.func_backup)
            self.request_data += '\x01' + i[:4] + '=' + tempvalue
        self.ent7_value.set(self.request_data)
            
    def combo2_selection(self, event):
        self.current_scheme, self.server_ip, self.server_port, self.qs_id = config.readbackup(self.combobox2.get())
        self.func_object = autotest.Func(self.server_ip, self.server_port, self.qs_id)
        self.func_object.readdict()
        self.func_object.write_json()      

        self.ent1_value.set(self.server_ip)
        self.ent2_value.set(self.server_port)
        self.ent3_value.set(self.qs_id)
        self.init_function()
        
        self.mongo_object = dbinit.Mongo(self.current_scheme)
        self.mongo_object.db_init()
        
        self.lbox.delete(0, 'end')
        for item in self.mongo_object.case:
            self.lbox.insert('end', item["_id"])
    
        # Colorize alternating lines of the listbox
        for i in range(0, len(self.mongo_object.case), 2):
            self.lbox.itemconfigure(i, background='#f0f0ff')         
        
    def search_func(self, event):   
        for item in self.combobox1['values']:
            if item.startswith(self.combobox1.get()):
                #取得第一个匹配self.combobox1.get()输入值的values索引
                index = self.combobox1['values'].index(item)
                print(index)
                break
        #切换到index的位置
        self.combobox1.current(index)
        self.combobox1.icursor('end')
        
    def init_function(self):
        ll = []
        for k,v in self.func_object.request_gn_interpret_dict.items():
            ll.append(k + ' ' + v)
        self.combobox1['values'] = tuple(ll)
        
        self.combobox1.set('')
        for widget in self.labelframe1.grid_slaves():
            widget.destroy()
            
        #功能参数初始化
        if self.func_object.request_gn_interpret_dict != {}:
            self.combobox1.current(0)
            self.request_data = ''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(self.combobox1.get()[:5],self.func_object.guid))
            items = map(lambda zd: str(zd)+' '+self.func_object.zd_interpret_dic[zd], 
                       self.func_object.request_gn_zd_dict[self.combobox1.get()[:5]])              
            num = 0
            for i in items:
                num = num + 1
                tempvalue = config.readfunc(self.current_scheme, self.combobox1.get()[:5], i[:4])
                templabel = ttk.Label(self.labelframe1,text = i+':',font = self.ft,width = 20)
                templabel.grid(row = num,column = 0,padx = 2,sticky = W)
                tempentry = ttk.Entry(self.labelframe1,width = 25)
                tempentry.grid(row = num,column = 1,padx = 2,sticky = E)
                tempentry.insert(0, tempvalue)
                tempentry.bind('<KeyRelease>', self.func_backup)
                self.request_data += '\x01' + i[:4] + '=' + tempvalue
            self.ent7_value.set(self.request_data)                
        
    def showscene(self):   
        self.toplevel = Toplevel(self.parent)
        self.toplevel.geometry('600x600+350+50')
        self.toplevel.title(string='测试场景')
        self.toplevel.iconbitmap('console.ico')
        self.text = Text(self.toplevel, font = self.ft)
        self.scrollbar4 = ttk.Scrollbar(self.text)
        self.text.config(yscrollcommand = self.scrollbar4.set)
        self.scrollbar4.config(command = self.text.yview)
        self.button9 = ttk.Button(self.toplevel, text = '退出', state = 'normal', width = 15, command = self.cancel)
        self.button10 = ttk.Button(self.toplevel, text = '保存', state = 'normal', width = 15, command = self.save_scene)

        self.text.pack(expand = YES, fill = BOTH)
        self.scrollbar4.pack(side = RIGHT, fill = Y)
        self.button9.pack(side = RIGHT)
        self.button10.pack(side = RIGHT)
        
        self.parent.attributes('-disabled', 1)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.cancel)
        self.toplevel.focus_set()       
   
    def cancel(self):
        self.toplevel.destroy()
        self.parent.attributes('-disabled', 0)
        #显示父窗口
        self.parent.deiconify()
        
    def modify_scene(self, event):
        self.showscene()
        idxs = self.lbox.selection_get()
        #查库取_id等于idxs的document
        func_dict = self.mongo_object.db_find(self.combobox1.get(), idxs)
        self.text.insert(1.0, json.dumps(collections.OrderedDict(sorted(func_dict.items())), ensure_ascii=False, indent=4))
        
    def save_scene(self):
        #取text中的_id
        idxs = self.text.get(2.0, 3.0).split('": "')[1].split('",')[0]
        self.mongo_object.db_add(self.combobox1.get(), idxs, json.loads(self.text.get(1.0, 'end')))
        if idxs not in self.lbox.get(0, 'end'):   
            self.lbox.insert('end', idxs)
            self.lbox.update_idletasks()
        self.cancel()
        
    def add_scene(self):
        self.showscene()
        entry_list = []
        label_list = []
        func_dict = collections.OrderedDict()
        for widget in self.labelframe1.grid_slaves():
            if str(type(widget)) == "<class 'tkinter.ttk.Entry'>":
                entry_list.append(widget.get())
            else:
                label_list.append(widget['text'])
        func_dict['_id'] = self.combobox1.get() + '_场景XX'
        func_dict['array'] = [{k:v} for k,v in list(zip(list(reversed(label_list)), list(reversed(entry_list))))]
        self.text.insert(1.0, json.dumps(func_dict, ensure_ascii=False, indent=4))
        
    def del_scene(self): 
        items = self.lbox.curselection()
        pos = 0
        for i in items :
            idx = int(i) - pos
            idxs = self.lbox.get(idx)
            self.lbox.delete(idx, idx)
            pos = pos + 1        
            self.mongo_object.db_del(idxs[:10], idxs)
    
    def func_backup(self, event):
        #取焦点控件entry的输入值
        value = self.parent.focus_get().get()
        #取焦点控件entry在labelframe1控件列表中的索引
        index = self.labelframe1.grid_slaves().index(self.parent.focus_get())
        #取entry对应label的字段号
        field = self.labelframe1.grid_slaves()[index+1]['text'][:4]
        self.request_data = self.ent7_value.get()
        
        match = re.search('\x01'+ field + '=' + '[^\x01]*\x01', self.request_data)
        self.ent7_value.set(self.request_data.replace(match.group(), '\x01'+ field + '=' + value + '\x01'))
        config.writefunc(self.combobox2.get(), self.combobox1.get()[:5], field, value)
    
    def atuo_test(self):
        server_ip = self.ent1.get()
        server_port = self.ent2.get()
        qs_id = self.ent3.get()
        self.func_object = autotest.Func(server_ip, server_port, qs_id)
        
        #建立socket连接和AB握手
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.func_object.ABProtocol(loop))
            self.func_object.readdict()
        except OSError as e:
            print(e)
            return
        
        for document in self.mongo_object.case:
            request_data = ''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(document['_id'][:5], self.func_object.guid))
            for field in document['array']:
                item = list(field.items())[0]
                request_data += '\x01' + item[0][:4] + '=' + item[1]
            loop = asyncio.get_event_loop()
            self.func_object.recv_serverdata = loop.run_until_complete(self.func_object.pack_send_data(request_data))
            str_data = self.func_object.unpack_data()
            rec_list = self.func_object.parse_string(str_data)        
        
    def functest(self, request_data):
        print(request_data)
        try:
            loop = asyncio.get_event_loop()
            self.func_object.recv_serverdata = loop.run_until_complete(self.func_object.pack_send_data(request_data))
            str_data = self.func_object.unpack_data()
            self.ent8_value.set(str_data)
            rec_list = self.func_object.parse_string(str_data)
        except ConnectionResetError as e:
            print(e)
            messagebox.showerror(title = '提示', message = '主站通讯断开！')
            self.button3['state'] = 'active'
            self.button4['state'] = 'disabled' 
            self.button5['state'] = 'active'
            self.button6['state'] = 'disabled'
            
        for i in self.tree.get_children(): 
            self.tree.delete(i)
            
        self.tree.heading('#0', text='')
        self.tree.column("#0", width=1000)        
        for i in range(self.num):
            self.tree.heading('#'+str(i+1), text='')
            self.tree.column("#"+str(i+1), width=0)
            
        if rec_list != [] and rec_list != None:
            columns = [str(i) + self.func_object.zd_interpret_dic[i] for i in rec_list[0].keys()]
            self.num = len(columns)
            self.tree['columns'] = columns
            self.tree.heading('#0', text='序号', anchor='center')
            self.tree.column('#0', stretch=NO, minwidth=0, width=50, anchor='w')
            for i in range(self.num):
                self.tree.heading('#'+str(i+1), text=columns[i], anchor='w')  
                self.tree.column('#'+str(i+1), stretch=NO, minwidth=0, width=100, anchor='w')
        
            for i in range(len(rec_list)):
                if i%2 == 0:
                    self.tree.insert('',i,text=str(i+1),values=[j[1] for j in rec_list[i].items()], tags=('oddrow',))
                else:
                    self.tree.insert('',i,text=str(i+1),values=[j[1] for j in rec_list[i].items()], tags=('evenrow',))
            self.tree.tag_configure('evenrow', background='#f0f0ff')
        
    def connect(self):
        self.current_scheme = self.combobox2.get()
        self.server_ip = self.ent1.get()
        self.server_port = self.ent2.get()
        self.qs_id = self.ent3.get()
        self.func_object = autotest.Func(self.server_ip, self.server_port, self.qs_id)
        
        #建立socket连接和AB握手
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.func_object.ABProtocol(loop))
            self.func_object.readdict()
        except OSError as e:
            print(e)
            return
        
        self.button3['state'] = 'disabled'
        self.button4['state'] = 'active'
        self.button5['state'] = 'disabled'
        self.button6['state'] = 'active'
        self.init_function()
        messagebox.showinfo(title = '提示', message = '与服务器握手成功')
        config.writebackup(self.current_scheme, self.server_ip, self.server_port, self.qs_id)
        config.initfunc(self.current_scheme, self.func_object.request_gn_list, self.func_object.request_gn_zd_dict)
        
    
    def close(self):
        print("通讯断开")
        self.func_object.writer.close()
        self.button3['state'] = 'active'
        self.button4['state'] = 'disabled' 
        self.button5['state'] = 'active'
        self.button6['state'] = 'disabled'
        

if __name__ == '__main__':
    root = Tk()
    root.geometry('1100x600+100+50')
    root.title(string='委托服务端测试工具')
    root.iconbitmap('console.ico')
    app = App(root)
    root.mainloop()
    #dbinit.common_init()