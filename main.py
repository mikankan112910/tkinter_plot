#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ctypes 
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from tkinter import messagebox
from tkinter import colorchooser
import json
import pathlib as pl
import pprint
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backends.backend_pdf import PdfPages
import pq_class10 as pqc

class Application():

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1900x950")
        self.root.title("test")
        # self.root.state('zoomed')

        # Menubar追加
        self.set_menubar()

        self.notebook = ttk.Notebook(self.root)

        # tab1, tab2追加
        self.add_tab()
        self.add_tab()

    def mainloop(self):
        self.root.mainloop()

    def set_menubar(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='read previous work', command=self.read_restart)
        file_menu.add_command(label='write for restart', command=self.write_for_restart)

        tab_menu = tk.Menu(menubar, tearoff=0)
        tab_menu.add_command(label='add tab', command=self.add_tab)
        tab_menu.add_command(label='del tab', command=self.del_tab)

        save_menu = tk.Menu(menubar, tearoff=0)
        save_menu.add_command(label='png (subplots)', command=lambda:self.save_img('subplots', 'png'))
        save_menu.add_command(label='pdf (subplots)', command=lambda:self.save_img('subplots', 'pdf'))
        save_menu.add_command(label='png (each)', command=lambda:self.save_img('each', 'png'))
        save_menu.add_command(label='pdf (each)', command=lambda:self.save_img('each', 'pdf'))

        path_menu = tk.Menu(menubar, tearoff=0)
        path_menu.add_command(label='path list of plot data', command=self.check_path_list)

        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='Tab', menu=tab_menu)
        menubar.add_cascade(label='Save img', menu=save_menu)
        menubar.add_cascade(label='Path', menu=path_menu)

        self.root.config(menu=menubar)

    def save_img(self, subplots='subplots', ext='png'):
        tab_no = self.notebook.index(self.notebook.select())
        name = self.notebook.tabs()[tab_no]
        tab_widget = self.notebook.nametowidget(name)
        if subplots == 'subplots':
            tab_widget.save_img_subplots(ext)
        elif subplots == 'each':
            tab_widget.save_img_each(ext)

    def read_restart(self):
        self.read_set = {}
        fname = filedialog.askopenfilename(filetypes=[("restart file", "*.qplot")])
        print(f'Read {fname}')
        with open(fname) as f:
            self.read_res_data_dict = json.loads(json.load(f))
        print(f'read {fname} OK')
        pprint.pprint(self.read_res_data_dict)
        self.set_restart()

    def set_restart(self):
        # clear all tabs
        for _ in range(len(self.notebook.tabs())):
            self.notebook.forget(self.notebook.select())
        TabA.tab_index = 0
        TabB.tab_index = 0

        # set_
        for i in range(len(self.read_res_data_dict)-1):
            i = str(i)
            print('set', i, self.notebook.tabs(), self.read_res_data_dict)
            tname = self.read_res_data_dict[i]['tab_name']
            tab = eval(tname)(master=self.root)
            self.notebook.add(tab, text=tab.new_tab_name())
            self.notebook.pack(fill='both', expand=True)
            # print('tabs', i, self.notebook.tabs())
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[int(i)])
            if tname == 'TabA':
                nn = 3
            elif tname == 'TabB':
                nn = 1
                fi = self.read_res_data_dict[i]['filter']
                tab_widget.input_dict['filter'].insert(0, fi)
            for n in range(nn):
                d = self.read_res_data_dict[i]['dirs'][n]
                pqx = self.read_res_data_dict[i]['pq_xcol'][n]
                tab_widget.input_dict['dirs'][n].insert(0, d)
                tab_widget.input_dict['pq_xcol'][n].insert(0, pqx)
            dt = self.read_res_data_dict[i]['data_type']
            tab_widget.data_type.set(dt)

            if [i for i in tab_widget.input_dict['dirs'] if i]: # except for TabA & dirs=null
                tab_widget.search_dirs_and_files()
                for v, d in zip(tab_widget.chkVal, tab_widget.dirs_filtered):
                    # print('checkBox d', d, type(d), self.read_res_data_dict[i]['dirs_checked'])
                    if str(d) in self.read_res_data_dict[i]['dirs_checked']:
                        v.set(True)
                    else:
                        v.set(False)
            # TODO in TabA, checkbox trouble because dirs names is different from restart ones 

            tab_widget.cm_val.set(self.read_res_data_dict[i]['cmap_name'])
            # TODO custom color
            # TODO range
            tab_widget.range_type.set(self.read_res_data_dict[i]['range_type'])
            tab_widget.xylabel_type.set(self.read_res_data_dict[i]['xylabel_type'])
            # TODO data cols

        # tab = eval('TabA')(master=self.root)
        # self.notebook.add(tab, text=tab.new_tab_name())
        # self.notebook.pack(fill='both', expand=True)
        # tab_widget = self.notebook.nametowidget(self.notebook.tabs()[0])
        # tab_widget.input_dict['dirs'][0].insert(0, 'test_path/pq.txt')

    def write_for_restart(self):
        print("write for restart")
        import datetime as dt
        now = dt.datetime.now().strftime('_%Y-%m-%d_%H%M%S')
        fname = './_' + now + '.qplot'
        output_set = self.return_output_set()
        print('output_set', output_set)
        with open(fname, mode='w') as f:
            json.dump(json.dumps(output_set), f, indent=4)
        print(f'write {fname} file OK')

    def return_output_set(self):
        print("return output set")
        output_dict = {
            'tab_number':self.notebook.index('end')
        }
        for i, name in enumerate(self.notebook.tabs()):
            tab_widget = self.notebook.nametowidget(name)
            output_dict[i] = tab_widget.get_restart_data()
        # ****
        # tab_no = self.notebook.index(self.notebook.select())
        # name = self.notebook.tabs()[tab_no]
        # tab_widget = self.notebook.nametowidget(name)
        # if tab_widget.__class__.__name__ == "TabB":
        #     print(tab_widget.checkBox_lst)
        #     print(tab_widget.chkVal)
        # else:
        #     print(tab_widget.__class__.__name__)

        # ****

        return output_dict

    def add_tab(self):
        if TabA.tab_index == 0:
            tab = TabA(master=self.root)
        elif TabB.tab_index == 0:
            tab = TabB(master=self.root)
        else:
            tab_no = self.notebook.index(self.notebook.select())
            name = self.notebook.tabs()[tab_no]
            tab_widget = self.notebook.nametowidget(name)
            tab = tab_widget.__class__(master=self.root)

        self.notebook.add(tab, text=tab.new_tab_name())
        self.notebook.pack(fill='both', expand=True)

    def del_tab(self):
        print("del tab ", self.notebook.select())
        self.notebook.forget(self.notebook.select())

    def check_path_list(self):
        tab_no = self.notebook.index(self.notebook.select())
        name = self.notebook.tabs()[tab_no]
        tab_widget = self.notebook.nametowidget(name)
        p = [t for t in tab_widget.dirs_filtered]
        c = [i.get() for i in tab_widget.chkVal]
        pc = [str(i) + ':' + str(j) + '\n' for i, j in zip(p, c)]
        pc.insert(0, '[Path:Check]')
        pc.insert(0, f'root:{tab_widget.dirs_filtered[0].parent.resolve()}')
        messagebox.showinfo('Check plot data path', '\n'.join(pc))

class Tab(ttk.Frame):

    tab_index = 0

    def __init__(self, master=None, **kw):
        Tab.tab_index += 1
        ttk.Frame.__init__(self, master)  

    # Entry for path, filter
    def set_path_entry_pq_x_col(self, label):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)
        fr.pack_propagate(False)

        lb = ttk.Label(fr, text=label, width=15)
        lb.pack(side=tk.LEFT, padx=10)
        en = ttk.Entry(fr, width=200)
        en.pack(anchor=tk.W, side=tk.LEFT, fill=tk.BOTH)
        en2 = ttk.Entry(fr, width=2)
        en2.pack(anchor=tk.E,fill=tk.BOTH)
        return en, en2

    def set_path_entry(self, label):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)
        fr.pack_propagate(False)

        lb = ttk.Label(fr, text=label, width=15)
        lb.pack(side=tk.LEFT, padx=10)
        en = ttk.Entry(fr)
        en.pack(anchor=tk.W, fill=tk.BOTH)
        return en

    # Button for reading path
    def set_read_path_button_and_data_type_rbutton(self, text_lst=['PQ', 'Span_LE', 'Span_TE', 'bm', 'ccut'], 
                                                        value_lst=['pq', 'span_le', 'span_te', 'bm', 'ccut']):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)

        fr1 = ttk.Frame(fr, width=300)
        fr1.grid(row=0, column=0)
        bt = ttk.Button(fr1, text='Read path', command=self.search_dirs_and_files)
        bt.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        fr2 = ttk.Frame(fr, width=1500)
        fr2.grid(row=0, column=1)
        self.data_type = tk.StringVar()
        self.data_type.set(value_lst[0])
        for i, (t, v) in enumerate(zip(text_lst, value_lst)):
            rb = ttk.Radiobutton(fr2, text=text_lst[i], value=value_lst[i], variable=self.data_type)
            rb.grid(row=0, column=i, sticky=tk.W, padx=10)

    def set_read_path_button_mod(self):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)

        bt = ttk.Button(fr, text='Read path', command=self.search_dirs_and_files)
        bt.grid(row=0, column=0, sticky=tk.W, padx=10)

    def search_dirs_and_files(self):
        print('Read search_dirs_files')
        #### TODO:be able to combine dirs and files
        try:
            # tabA
            if isinstance(self, TabA):
            # if pl.Path(self.input_dict['dirs'][0].get()).is_file():
                dirs = [pl.Path(i.get()) for i in self.input_dict['dirs'] if i.get()]
                dir_filter = ''
            # tabB
            elif isinstance(self, TabB):
            # elif pl.Path(self.input_dict['dirs'][0].get()).is_dir():
                dirs = [f for f in pl.Path(self.input_dict['dirs'][0].get()).iterdir() if f.is_dir()]
                dir_filter = self.input_dict['filter'].get()
        except FileNotFoundError as e:
            print('No Directory. Make sure this path.', e)
        # print('dirs', dirs, dirs[0], str(dirs[0]))
        self.dirs_filtered = [i for i in dirs if i.name.startswith(dir_filter)]
        self.make_chkbox_mod(self.dirs_filtered)
        # self.make_xylabel_rbutton()
        # self.make_data_cols_no_entry()
        self.make_option_button_etc()

    def set_dirs_checkbox(self):
        self.frame_dirs_chkbox = ttk.Frame(self)
        self.frame_dirs_chkbox.pack(anchor=tk.NW)

    def make_chkbox_mod(self, dirs, NUM_PER_ROW=3):
        if 'dirs_checkBox_lst' in dir(self):
            self.dirs_checkBox_lst
            for cbox in self.dirs_checkBox_lst:
                cbox.grid_forget()
        self.dirs_checkBox_lst = []
        self.chkVal = []
        for i, t in enumerate(dirs):
            self.chkVal.append(tk.BooleanVar())
            self.dirs_checkBox_lst.append(tk.StringVar())
            # self.dirs_checkBox_lst[i] = ttk.Checkbutton(self.frame_dirs_chkbox, text=t.name, var=self.chkVal[i])
            self.dirs_checkBox_lst[i] = ttk.Checkbutton(self.frame_dirs_chkbox, text=str(t), var=self.chkVal[i])
            self.dirs_checkBox_lst[i].grid(row=i%(NUM_PER_ROW-1), column=i//(NUM_PER_ROW-1), sticky=tk.W, padx=20)
            self.chkVal[i].set(True) 

    def set_data_type_rbutton(self, text_lst =['PQ', 'Span_LE', 'Span_TE', 'bm', 'ccut'], 
                                    value_lst=['pq', 'span_le', 'span_te', 'bm', 'ccut']):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)

        self.data_type = tk.StringVar()
        self.data_type.set(value_lst[0])
        for i, (t, v) in enumerate(zip(text_lst, value_lst)):
            rb = ttk.Radiobutton(fr, text=text_lst[i], value=value_lst[i], variable=self.data_type)
            rb.grid(row=0, column=i, sticky=tk.W, padx=10)

    def set_plot_button_cmap(self):
        fr = ttk.Frame(self, width=1800, height=25)
        fr.pack(anchor=tk.NW)

        bt = ttk.Button(fr, text='Plot', command=self.plot)
        bt.grid(row=0, column=0, sticky=tk.W, padx=10)

        cm_name_all = pqc.Cmap().read_cm().keys()
        self.cm_val = tk.StringVar()
        self.cm_val.set(next(iter(pqc.Cmap().read_cm())))
        op = tk.OptionMenu(fr, self.cm_val, *cm_name_all, command=self.change_cmap_display)
        op.grid(row=0, column=1, sticky=tk.W, padx=10)
        fr_cm = tk.Frame(fr, width=100, height=30, bg='white')
        fr_cm.grid(row=0, column=2, padx=10)
        fr_cm.grid_propagate(False)
        cm_selected = [i for i in pqc.Cmap().read_cm()[self.cm_val.get()]]
        self.frame_cm_display = []
        for i in range(len(cm_selected)):
            self.frame_cm_display.append(tk.Frame(fr_cm, width=10, height=30, bg=cm_selected[i]['color']))
            self.frame_cm_display[i].grid(row=0, column=i, sticky=tk.W + tk.E + tk.N + tk.S)
        self.bt_dirs_color = []
        self.dirs_color = ['#ffffff']*6
        for i in range(6):
            self.bt_dirs_color.append(tk.Button(fr, text=f'Dir{i+1}', command=self.select_color(i)))
            self.bt_dirs_color[i].grid(row=0, column=3+i)


    def select_color(self, no):
        def x():
            c = colorchooser.askcolor()
            self.bt_dirs_color[no].config(bg=c[1])
            self.dirs_color[no] = c[1]
        return x

    def change_cmap_display(self, event):
        cm_selected = [i for i in pqc.Cmap().read_cm()[self.cm_val.get()]]
        print(f'change cmap:{self.cm_val.get()}')
        for i, fr in enumerate(self.frame_cm_display):
            if i <= len(cm_selected)-1:
                fr.configure(bg=cm_selected[i]['color'])
            else:
                fr.configure(bg='white')

    def plot(self):
        self.set_plot_input_dict()
        pqc.DataPlot(self.plot_input_dict)
        self.tkcanvas.draw()

    def set_plot_input_dict(self):
        if self.dirs_filtered[0].is_file():
            dirs_filtered_add_file = self.dirs_filtered
            pq_xcol = [0 if i.get() == '' else int(i.get())-1 for i in self.input_dict['pq_xcol']]
        elif self.dirs_filtered[0].is_dir():
            dirs_filtered_add_file = self.add_files_to_dirs(self.dirs_filtered, self.data_type.get())
            xc = 0 if self.input_dict['pq_xcol'][0].get() == '' else int(self.input_dict['pq_xcol'][0].get())-1
            pq_xcol = [xc for _ in range(len(dirs_filtered_add_file))]

        # check files exist
        self.dirs_checked = []
        self.pq_xcol_checked = []
        for i in range(len(dirs_filtered_add_file)):
            if self.chkVal[i].get():
                self.dirs_checked.append(dirs_filtered_add_file[i]) 
                self.pq_xcol_checked.append(pq_xcol[i])
        
        # change fig size for data type
        self.fig.clf()
        if self.data_type.get() == 'pq':
            print('figsize change 18, 6')
            self.fig.set_size_inches(18, 12)
            self.fig_max_row = 3
        elif self.data_type.get() == 'span_le':
            print('figsize change 18, 12')
            self.fig.set_size_inches(18, 18)
            self.fig_max_row = 5

        # set range
        if self.range_type.get() == 'auto':
            range_y = None
            range_x = None
        elif self.range_type.get() == 'all':
            # print('range_all_yx', self.entry_range_all_yx[0].get())
            range_y = [i.get() for i in self.entry_range_all_yx[:2]]
            range_x = [i.get() for i in self.entry_range_all_yx[2:]]
            print('range all', range_y, range_x)
        elif self.range_type.get() == 'each':
            range_y = [i[:2] for i in self.range_each_yx_lst]
            range_x = [i[2:] for i in self.range_each_yx_lst]

        # set data column numbers
        #    [[(no1.fig1.x, no1.fig1.y),(no1.fig2.x,.)...], [(no2.fig1.x,.)...],...]
        self.data_cols_no_lst = []
        if self.chkVal_data_cols_no.get() == True:
            for n in range(6):
                # z = [[i, i] for i in range(len())]
                a = self.data_cols_no[n*2].get()
                b = self.data_cols_no[n*2 + 1].get()
                # if a:print(n, a, b, 'true')
                # else:print(n, a, b, 'false')
                self.data_cols_no_lst.append([[i, j] for i, j in zip(a.split(','), b.split(','))])
            print(self.data_cols_no_lst)

        # pack input data
        self.plot_input_dict = {
            'fig':self.fig,
            'fig_max_row':self.fig_max_row,
            'dirs':self.dirs_checked,
            'data_type':self.data_type.get(),
            'cmap_name':self.cm_val.get(),
            'range_type':self.range_type.get(),
            'range_y':range_y,
            'range_x':range_x,
            'range_each_no':self.range_each_no_lst if 'range_each_no_lst' in dir(self) else None,
            'pq_xcol':self.pq_xcol_checked,
            # 'data_cols_no_change':self.chkVal_data_cols_no.get(),
            'data_cols_no_diff':self.data_cols_no_lst,
            'xylabel_type':self.xylabel_type.get(),
            'dirs_color':self.dirs_color,
        }
        print('plot input:', self.plot_input_dict)

    def add_files_to_dirs(self, dirs, data_type):
        dirs_added_files = []
        add_files = {
            'pq':'pq.txt',
            'span_le':'span_phys_le.txt',
            'span_te':'span_phys_te.txt',
            'bm':'bm.txt',
            'ccut':'ccut.txt',
        }
        for i in dirs:
            dirs_added_files.append(i / add_files[data_type])
        for i in dirs_added_files:
            if not i.exists():
                print(f'file is not found:{i}')
        dirs_added_files_exist = [i for i in dirs_added_files if i.exists()]
        return dirs_added_files_exist

    def set_option(self):
        self.frame_option = ttk.Frame(self, width=1800, height=25)
        self.frame_option.pack(anchor=tk.NW)

        self.frame_range = ttk.Frame(self.frame_option)
        self.frame_range.pack(side=tk.LEFT)
        
        self.frame_data_cols_en = ttk.Frame(self.frame_option)
        self.frame_data_cols_en.pack(side=tk.LEFT)
        
        self.frame_xylabel_rb = ttk.Frame(self.frame_option)
        self.frame_xylabel_rb.pack(side=tk.LEFT)

    def make_option_button_etc(self):
        # Range
        lb1 = ttk.Label(self.frame_range, text='  Range ', relief='solid')
        lb1.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.range_type = tk.StringVar()
        self.range_type.set('auto')
        rb1 = ttk.Radiobutton(self.frame_range, text='Auto', value='auto', variable=self.range_type)
        rb2 = ttk.Radiobutton(self.frame_range, text='All', value='all', variable=self.range_type)
        rb3 = ttk.Radiobutton(self.frame_range, text='Each', value='each', variable=self.range_type)
        rb1.grid(row=0, column=1, sticky=tk.W, padx=(20,0))
        rb2.grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        rb3.grid(row=0, column=7, sticky=tk.W, padx=(20,0))
        self.entry_range_all_yx = []
        for i in range(4):
            self.entry_range_all_yx.append(ttk.Entry(self.frame_range, width=6))
            self.entry_range_all_yx[i].grid(row=0, column=i+3, sticky=tk.W)
            self.entry_range_all_yx[i].insert(0, ['ymin', 'ymax', 'xmin', 'xmax'][i])
        ## TODO range each
        self.entry_range_each_yx = []
        self.range_each_no_lst = []
        self.range_each_no = tk.StringVar()

        # data cols
        lb2 = ttk.Label(self.frame_data_cols_en, text='  Data cols No ', relief='solid')
        lb2.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.chkVal_data_cols_no = tk.BooleanVar()
        self.chkVal_data_cols_no.set(False)
        ttk.Checkbutton(self.frame_data_cols_en, text='change', var=self.chkVal_data_cols_no).grid(row=0, column=1, sticky=tk.W, padx=5)

        # xy label
        label_type_lst = ['asis', 'default', 'file']
        text_lst = ['As is', 'Default', 'Read file(qplot_set.txt)']

        lb3 = ttk.Label(self.frame_xylabel_rb, text='  XY Label ', relief='solid')
        lb3.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.xylabel_type = tk.StringVar()
        self.xylabel_type.set(label_type_lst[0])
        for i, (t, v) in enumerate(zip(text_lst, label_type_lst)):
            rb = ttk.Radiobutton(self.frame_xylabel_rb, text=t, value=v, variable=self.xylabel_type)
            rb.grid(row=0, column=i+1, sticky=tk.W, padx=10)
        
        # detail option
        if 'bt_option_detail' in dir(self):
            self.bt_option_detail.forget()
        self.bt_option_detail = ttk.Button(self.frame_option, text='Detail', command=self.set_option_detail)
        self.bt_option_detail.pack(side=tk.LEFT)
    
    def set_option_detail(self):
        self.win = tk.Toplevel()
        self.win.geometry("1000x600")
        ttk.Label(self.win, text='Under constructing').pack()
        # TODO
        pass

    # def set_range_rbuttons(self):
    #     fr = ttk.Frame(self, width=1800, height=25)
    #     fr.pack(anchor=tk.NW)

    #     lb = ttk.Label(fr, text='  Range ')
    #     lb.grid(row=0, column=0, sticky=tk.W, padx=5)
    #     self.range_type = tk.StringVar()
    #     self.range_type.set('auto')
    #     rb1 = ttk.Radiobutton(fr, text='Auto', value='auto', variable=self.range_type)
    #     rb2 = ttk.Radiobutton(fr, text='All', value='all', variable=self.range_type)
    #     rb3 = ttk.Radiobutton(fr, text='Each', value='each', variable=self.range_type)
    #     rb1.grid(row=0, column=1, sticky=tk.W, padx=(20,0))
    #     rb2.grid(row=0, column=2, sticky=tk.W, padx=(20,0))
    #     rb3.grid(row=0, column=7, sticky=tk.W, padx=(20,0))
    #     self.entry_range_all_yx = []
    #     self.entry_range_each_yx = []
    #     for i in range(4):
    #         self.entry_range_all_yx.append(ttk.Entry(fr, width=6))
    #         self.entry_range_all_yx[i].grid(row=0, column=i+3, sticky=tk.W)
    #         self.entry_range_all_yx[i].insert(0, ['ymin', 'ymax', 'xmin', 'xmax'][i])
    #     self.range_each_no_lst = []
    #     self.range_each_no = tk.StringVar()
    #     op = tk.OptionMenu(fr, self.range_each_no, *[i for i in range(22)])
    #     op.grid(row=0, column=8, sticky=tk.W)
    #     for i in range(4):
    #         self.entry_range_each_yx.append(ttk.Entry(fr, width=6))
    #         self.entry_range_each_yx[i].grid(row=0, column=i+9, sticky=tk.W)
    #         self.entry_range_each_yx[i].insert(0, ['ymin', 'ymax', 'xmin', 'xmax'][i])
    #     bt1 = ttk.Button(fr, text='Apply', command=self.range_each_apply)
    #     bt2 = ttk.Button(fr, text='Show list', command=self.range_each_apply_show)
    #     bt1.grid(row=0, column=13, sticky=tk.W)
    #     bt2.grid(row=0, column=14, sticky=tk.W)
 
    def range_each_apply(self):
        if not self.range_each_no_lst:
            self.range_each_yx_lst = []
        l = []
        for i in self.entry_range_each_yx:
            l.append(i.get())
        self.range_each_no_lst.append(self.range_each_no)
        self.range_each_yx_lst.append([l])

    def range_each_apply_show(self):
        try:
            l = '\n'.join([f'no:{i},x:{yx[2:]},y:{yx[:2]}' for i, yx in \
                        zip(self.range_each_no_lst, self.range_each_yx_lst)])
            messagebox.showinfo('Range fix list', l)
        except:
            print('each not apply yet')
        pass

    # def set_xylabel_rbutton(self):
    #     self.frame_xylabel_rb = ttk.Frame(self, width=1800, height=25)
    #     self.frame_xylabel_rb.pack(anchor=tk.NW)

    # def make_xylabel_rbutton(self):
    #     label_type_lst = ['asis', 'default', 'file']
    #     text_lst = ['As is', 'Default', 'Read file(qplot_set.txt)']

    #     lb = ttk.Label(self.frame_xylabel_rb, text='  XY Label ')
    #     lb.grid(row=0, column=0, sticky=tk.W, padx=5)
    #     self.xylabel_type = tk.StringVar()
    #     self.xylabel_type.set(label_type_lst[0])
    #     for i, (t, v) in enumerate(zip(text_lst, label_type_lst)):
    #         rb = ttk.Radiobutton(self.frame_xylabel_rb, text=t, value=v, variable=self.xylabel_type)
    #         rb.grid(row=0, column=i+1, sticky=tk.W, padx=10)
    
    # def set_data_cols_no_entry(self):
    #     self.frame_data_cols_en = ttk.Frame(self, width=1800, height=25)
    #     self.frame_data_cols_en.pack(anchor=tk.NW)
    
    # def make_data_cols_no_entry(self):
    #     print('make data cols No. entry')
    #     lb = ttk.Label(self.frame_data_cols_en, text='  Data cols No ')
    #     lb.grid(row=0, column=0, sticky=tk.W, padx=5)
    #     self.chkVal_data_cols_no = tk.BooleanVar()
    #     self.chkVal_data_cols_no.set(False)
    #     ttk.Checkbutton(self.frame_data_cols_en, var=self.chkVal_data_cols_no).grid(row=0, column=1, sticky=tk.W, padx=5)

    #     NUM = 6
    #     self.data_cols_no = []
    #     for i in range(NUM):
    #         ttk.Label(self.frame_data_cols_en, text=f'Dir{i+1}').grid(row=0, column=i*3+2, sticky=tk.W)
    #         self.data_cols_no.append(ttk.Entry(self.frame_data_cols_en, width=12))
    #         self.data_cols_no[i*2].grid(row=0, column=i*3+3, sticky=tk.W)
    #         self.data_cols_no.append(ttk.Entry(self.frame_data_cols_en, width=12))
    #         self.data_cols_no[i*2+1].grid(row=0, column=i*3+4, sticky=tk.W)
    #     self.data_cols_no[0].insert(0, 'x')
    #     self.data_cols_no[1].insert(0, 'y')        

    def set_plot_canvas(self):
        fr = ttk.Frame(self)
        fr.pack(anchor=tk.NW)
        
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(anchor=tk.NW)

        self.canvas = tk.Canvas(fr, width='1800', height='600', bg='blue')
        self.canvas.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.frame_canvas = tk.Frame(self.canvas)
        self.frame_canvas.pack()
        vsb = tk.Scrollbar(fr, orient=tk.VERTICAL, command=self.canvas.yview)
        hsb = tk.Scrollbar(fr, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='we')

        self.canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        self.canvas.create_window((0,0), anchor=tk.NW, window=self.frame_canvas)
        self.canvas.config(scrollregion=(0,0,1800, 1800))

        self.make_canvas()
        self.tkcanvas.get_tk_widget().bind("<MouseWheel>", self.mouse_y_scroll)

    def make_canvas(self):
        print('make canvas')
        self.fig = plt.figure(figsize=(18,18), tight_layout=True)
        self.tkcanvas = FigureCanvasTkAgg(self.fig, master=self.frame_canvas)
        # self.tkcanvas.draw()
        self.tkcanvas.get_tk_widget().pack()
        self.toolbar = NavigationToolbar2Tk(self.tkcanvas, self.toolbar)
        self.toolbar.update()
        self.tkcanvas._tkcanvas.pack()

    def mouse_y_scroll(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-2, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(2, 'units')

    def save_img_subplots(self, ext='png'):
        dirs_checked_namelist = [i.parent.name for i in self.dirs_checked]
        vs_name = '-'.join(dirs_checked_namelist)
        f = f'qplot_subplots_{self.__class__.__name__}_{self.data_type.get()}_{vs_name}.' + ext
        if pl.Path(f).exists():
            ans = messagebox.askquestion(f'write {ext.upper()} each', f'overwrite OK?\n {f}')
        else:
            ans = 'yes'
        if ans == 'yes':
            if ext == 'png':
                self.fig.savefig(f, dpi=300, transparent=True)
            elif ext == 'pdf':
                with PdfPages(f) as pdf:
                    pdf.savefig()
            messagebox.showinfo(f'write {ext.upper()} subplots', f'Saved {f}')

    def save_img_each(self, ext='png'):
        dirs_checked_namelist = [i.parent.name for i in self.dirs_checked]
        vs_name = '-'.join(dirs_checked_namelist)
        f = f'qplot_each_{self.__class__.__name__}_{self.data_type.get()}_{vs_name}'
        if list(pl.Path().glob(f'{f}*')):
            print(list(pl.Path().glob(f'{f}*.{ext}')))
            ans = messagebox.askquestion(f'write {ext.upper()} each', f'overwrite OK?\n {f}*.{ext}')
        else:
            ans = 'yes'
        if ans == 'yes':
            pqc.SavePlot(self.plot_input_dict)
            # pqc.SavePlot(f, ext, self.dirs_checked_add_file, self.data_type.get(), self.cm_val.get())
        #     if ext == 'png':
        #         # self.fig.savefig(f, dpi=300, transparent=True)
        #         pass
        #     elif ext == 'pdf':
        #         with PdfPages(f) as pdf:
        #             pdf.savefig()
        #     messagebox.showinfo(f'write {ext.upper()} subplots', f'Saved {f}')

    
    # def output_data_set(self):
    #     dirs_filtered_check = {}
    #     for d, c in zip(self.dirs_filtered, self.chkVal):
    #         dirs_filtered_check[d.name] = c.get()
    #     output = {
    #         "tab_class":self.__class__.__name__,
    #         "path_root":self.path_root,
    #         "dir_filter":self.dir_filter,
    #         "dirs_filters":dirs_filtered_check
    #     }
    #     return output
    def get_restart_data(self):
        output_dict = {
            'tab_name':self.__class__.__name__,
            'dirs':[i.get() for i in self.input_dict['dirs']],
            'pq_xcol':[i.get() for i in self.input_dict['pq_xcol']],
            'filter':self.input_dict['filter'].get() if self.input_dict.get('filter') else None,
            'data_type':self.data_type.get(),
            # 'dirs_checked':[str(i) for i in self.dirs_checked] if 'dirs_checked' in dir(self) else None,
            'dirs_checked':[i.parent.name for i in self.dirs_checked] if 'dirs_checked' in dir(self) else None,
            'cmap_name':self.cm_val.get(),
            'cmap_custom_color':self.dirs_color,
            'range_type':self.range_type.get(),
            'xylabel_type':self.xylabel_type.get() if 'xylabel_type' in dir(self) else None,
        }
        return output_dict

class TabA(Tab):

    tab_index = 0

    def __init__(self, master=None, **kw):
        TabA.tab_index += 1
        ttk.Frame.__init__(self, master)    
    
        self.input_dict = {}

        # path & filter Entry
        self.input_dict['dirs'] = []
        self.input_dict['pq_xcol'] = []
        for i in range(3):
            # self.input_dict['dirs'].append(self.set_path_entry('dir:'))
            d, pq = self.set_path_entry_pq_x_col('dir:')
            self.input_dict['dirs'].append(d)
            self.input_dict['pq_xcol'].append(pq)
        
        # read Button
        # self.set_read_path_button_mod()
        self.set_read_path_button_and_data_type_rbutton()

        # plot type RadioButton
        # self.set_data_type_rbutton()

        # plot Button & cmap
        self.set_plot_button_cmap()

        # data Checkbox
        self.set_dirs_checkbox()

        # option
        self.set_option()

        # plot Canvas
        self.set_plot_canvas()

    def new_tab_name(self):
        return "tabA_" + str(TabA.tab_index)

class TabB(Tab):

    tab_index = 0

    def __init__(self, master=None, **kw):
        TabB.tab_index += 1
        ttk.Frame.__init__(self, master)

        self.input_dict = {}

        # path & filter Entry
        d, pq = self.set_path_entry_pq_x_col('Search dir:')
        self.input_dict['dirs'] = [d]
        self.input_dict['pq_xcol'] = [pq]
        # self.input_dict['dirs'] = [self.set_path_entry('Search dir:')]
        self.input_dict['filter'] = self.set_path_entry('Filter:')

        # read Button
        # self.set_read_path_button_mod()
        self.set_read_path_button_and_data_type_rbutton()

        # plot type RadioButton
        # rb_text = ['PQ', 'Span_LE', 'Span_TE', 'bm', 'ccut']
        # rb_value = ['pq', 'span_le', 'span_te', 'bm', 'ccut']
        # self.set_data_type_rbutton()

        # plot Button & cmap
        self.set_plot_button_cmap()

        # data Checkbox
        self.set_dirs_checkbox()

        # option
        self.set_option()

        # plot Canvas
        self.set_plot_canvas()

    def new_tab_name(self):
        return "tabB_" + str(TabB.tab_index)

if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    app = Application()
    app.mainloop()
