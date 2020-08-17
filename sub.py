import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pathlib as pl
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import messagebox
from cycler import cycler

class DataPlot():
    def __init__(self, input_dict):
        print('DataPlot')
        # input, init
        self.input_dict = input_dict
        self.init_val()

        # check path & read data
        self.del_no_files()

        # set plot style, range
        self.set_plot_option()

        # plot
        # self.plot()
        self.plot_mod()

    def init_val(self):
        self.fig = self.input_dict['fig']
        self.max_row = self.input_dict['fig_max_row']
        self.data_type = self.input_dict['data_type']
        self.range_type = self.input_dict['range_type']
        self.pq_xcol = self.input_dict['pq_xcol']
        self.xylabel_type = self.input_dict['xylabel_type']
        self.data_cols_no_diff = self.input_dict['data_cols_no_diff']
        self.dirs_color = self.input_dict['dirs_color']

    def del_no_files(self):
        # self.files = self.add_files_to_dirs(self.input_dict['dirs'])
        self.files = self.input_dict['dirs']
        print('---files exist check---')
        self.files_checked = []
        for i in self.files:
            if i.is_file():
                self.files_checked.append(i)
                print(f'{i} is found')
            else:
                print(f'{i} is NOT found')

        self.d_lst = [self.read_data(i) for i in self.files_checked]
        print('----------------------')

    def read_data(self, fname):
        with open(fname, mode='r') as f:
            ff = f.readlines()
            d = [l.split() for l in ff if l.split()]
            # print('d=', d)
            for _ in range(len(d[1])-len(d[0])):
                d[0].append('unknown')
            d = [list(x) for x in zip(*d)]
            # print('d=', d)
            # for i_ff, ln in enumerate(ff):
            #     ln = ln.split()
            #     if i_ff == 0:d = [0]*len(ln)
            #     for i_ln, ln_i in enumerate(ln):
            #         if i_ff == 0:d[i_ln] = [ln_i]
            #         else:
            #             d[i_ln].append(ln_i)
        print(f'file:{fname}, data size:{len(d)}x{len(d[0])}')
        # for i in d:
        #     print(f'   {i[:3]} ...')
        print('   ', ' '.join([i[0] for i in d]))
        print('   ', ' '.join([i[1] for i in d]))
        print('   ', ' '.join([i[2] for i in d]))
        print('----------------------')
        return d

    def plot_mod(self):
        print(f'Plot:{self.data_type}')

        # col of plot
        # col = [i for i in range(len(self.d_lst[0]))] # TODO
        col = [i for i in range(max([len(i) for i in self.d_lst]))]
        # col = self.select_col() # don't make yet
        print('plot col:', col, self.max_row)

        # fig arange
        ax = [0]*len(col)
        if len(col) <= self.max_row:
            row_n = len(col)
        else:
            row_n = self.max_row
        if len(col) % self.max_row == 0:
            col_n = len(col) // self.max_row
        else:
            col_n = len(col) // self.max_row + 1
        print(f'plot layout:{row_n}x{col_n}')
        for i, c in enumerate(col):
            ax[i] = self.fig.add_subplot(col_n, row_n, i+1)
   
        # plot
        for i, a in enumerate(ax):
            # a.legend()
            a.grid(True)
            a.set_title(self.title[self.data_type])
            if self.range_type == 'all':
                try:
                    a.set_xlim(*list(map(float, self.range_x)))
                except:
                    pass
                try:
                    a.set_ylim(*list(map(float, self.range_y)))
                except:
                    pass
            elif self.range_type == 'each':
                try:
                    a.set_xlim(*list(map(float, self.range_x[i])))
                except:
                    pass
                try:
                    a.set_ylim(*list(map(float, self.range_y[i])))
                except:
                    pass
            for i_d, (d, fname) in enumerate(zip(self.d_lst, self.files_checked)):
                try:
                    # x = list(map(float, d[self.pq_xcol[i_d]][1:]))
                    # y = list(map(float, d[i][1:]))
                    x = list(map(float, d[self.data_cols_no[i_d][i][0]][1:]))
                    y = list(map(float, d[self.data_cols_no[i_d][i][1]][1:]))
                    if self.data_type == 'pq':
                        a.plot(x, y, label=fname.parents[0].name)
                    else:
                        a.plot(y, x, label=fname.parents[0].name)
                    lbx = ','.join(set([k[0] for k in self.xylabel_dict['xlabel']]))
                    lby = ','.join(set([k[i] for k in self.xylabel_dict['ylabel'] if k[i:]]))
                    a.set_xlabel(lbx)
                    a.set_ylabel(lby)
                except:
                    pass
            a.legend()
    
    def set_plot_option(self):
        # set style
        plt.style.use('ggplot')
        self.change_plot_style()

        # set range
        self.set_range()
        self.set_title()
        self.set_xylabel()
        self.set_cols_no()

    def change_plot_style(self):
        kw = {
        # "font.family":'serif',
        # "font.serif":"Times New Roman",
        'axes.titlesize':10,
        'axes.prop_cycle':Cmap().read_cm()[self.input_dict['cmap_name']] if self.input_dict['cmap_name'] != 'custom' else cycler(color=self.dirs_color),
        'lines.linewidth':1,
        'lines.linestyle':'--',
        'lines.marker':'o',
        'lines.markersize':3,
        'legend.frameon':False,
        'legend.framealpha':0.8,
        # legend outside -> https://symfoware.blog.fc2.com/blog-entry-1418.html
        # 'axes.labelcolor':'black', # default:#555555
        # 'xtick.color':'black', # default:#555555
        # 'ytick.color':'black', # default:#555555
        'figure.dpi':300, # default 100 or 72
        }
        for k, v in kw.items():
            plt.rcParams[k] = v

    def set_range(self):
        if self.range_type == 'each':
            self.range_each_no_lst = self.input_dict['range_each_no']
        self.range_y = self.input_dict['range_y']
        self.range_x = self.input_dict['range_x']
        # if self.range_type != 'auto':
        #     print('pq range', self.range_y, self.range_x)
        #     self.range_y = [float(i) for i in self.range_y]
        #     self.range_x = [float(i) for i in self.range_x]
            # self.range_y = [list(map(float, i)) for i in self.range_y]
            # self.range_x = [list(map(float, i)) for i in self.range_x]
        print('Range ', self.range_type, self.range_x, self.range_y)
        
    def set_title(self):
        self.title = {
            'pq':'PQ plot',
            'span_le':'Span LE plot',
            'span_te':'Span TE plot',
            'bm':'Blade Mach Number plot',
            'cccc':'Cccc plot',
        }
    
    def set_xylabel(self):
        # self.xylabel_dict = label[self.data_type][self.xylabel_type]
        self.xylabel_dict = self.get_xylabel(self.data_type, self.xylabel_type)
        print('xylabel', self.xylabel_dict)

    def get_xylabel(self, data_type, label_type):
        if label_type == 'asis':
            lb = {
                'pq':{
                    'xlabel':[[b[0] for j, b in enumerate(a) if j == self.pq_xcol[i]] for i, a in enumerate(self.d_lst)],
                    # 'ylabel':[[*i] for i in zip(*self.d_lst) for j in i],
                    'ylabel':[[j[0] for j in i] for i in self.d_lst],
                },
                'span_le':{
                    'xlabel':[[b[0] for j, b in enumerate(a) if j == self.pq_xcol[i]] for i, a in enumerate(self.d_lst)],
                    'ylabel':[[j[0] for j in i] for i in self.d_lst],
                },
            }
        elif label_type == 'default':
            lb = {
                'pq':{
                    'xlabel':[['Corrected mass flow[kg/s]']]*len(self.d_lst),
                    'ylabel':[['Corrected mass flow[kg/s]', 'Pressure ratio[-]', 'Adiabatic efficienty[%]', 'Corrected mass flow[lb/s]']]*len(self.d_lst),
                },
                'span_le':{
                    'xlabel':[['Span[%]']]*len(self.d_lst),
                    'ylabel':[[f'phys{i}' for i in range(23)]]*len(self.d_lst), # TODO
                },
            }
        elif label_type == 'file':
            lb = {
                'pq':{
                    'xlabel':[self.xylabel_read_file()[0]]*len(self.d_lst),
                    'ylabel':[self.xylabel_read_file()[1]]*len(self.d_lst),
                },
                'span_le':{
                    'xlabel':[self.xylabel_read_file()[0]]*len(self.d_lst),
                    'ylabel':[self.xylabel_read_file()[1]]*len(self.d_lst),
                }
            }
        return lb[data_type]
    
    def xylabel_read_file(self):
        lst = []
        with open('qplot_set.txt') as f:
            for i in f.readlines():
                lst.append(list(map(str.strip, i.split(sep=','))))
        for i in range(len(self.d_lst[0])-len(lst[1])):
            lst[1].append(lst[1][-1])
        return lst

    def set_cols_no(self):
        print('set cols no')
        self.data_cols_no = []

        # default
        for i_d, d in enumerate(self.d_lst):
            cols = [[self.pq_xcol[i_d], i] for i in range(len(d))]
            self.data_cols_no.append(cols)
        print('data_cols_no before', self.data_cols_no)

        # change
        if self.data_cols_no_diff:
            for i_d, d in enumerate(self.data_cols_no):
                for i_col, _ in enumerate(d):
                    for i_xy in range(2): # x, y
                        if self.data_cols_no_diff[i_d][i_col:]:
                            if self.data_cols_no_diff[i_d][i_col][i_xy]:
                                d[i_col][i_xy] = int(self.data_cols_no_diff[i_d][i_col][i_xy])
        
        print('data_cols_no changed', self.data_cols_no)

class Cmap():
    def read_cm(self):
        paired_hex = [mpl.colors.rgb2hex(plt.cm.Paired(i)) for i in range(len(plt.cm.Paired.colors))]
        tab10_hex = [mpl.colors.rgb2hex(plt.cm.tab10(i)) for i in range(len(plt.cm.tab10.colors))]
        tab20_hex = [mpl.colors.rgb2hex(plt.cm.tab20(i)) for i in range(len(plt.cm.tab20.colors))]
        tab20c_hex = [mpl.colors.rgb2hex(plt.cm.tab20c(i)) for i in range(len(plt.cm.tab20c.colors))]
        cm_dict = {
            'cm_pq' : cycler(color=['#d62728', '#1f77b4', '#2ca02c', '#9467bd', '#17becf', '#bcbd22', '#e377c2', '#8c564b', '#7f7f7f']),
            # 'cm_blue_cycle5' : cycler(color=['#011f4b','#03396c','#005b96','#6497b1','#b3cde0']),
            'cm_blue_cycle4_tab20c' : cycler(color=tab20c_hex[:4]),
            'cm_orange_cycle4_tab20c' : cycler(color=tab20c_hex[4:8]),
            'cm_brown_cycle5' : cycler(color=['#8d5524','#c68642','#e0ac69','#f1c27d','#ffdbac']),
            'cm_paired' : cycler(color=paired_hex),
            'cm_tab10' : cycler(color=tab10_hex),
            'cm_tab20' : cycler(color=tab20_hex),
            'custom': cycler(color=['white']),
         }
        return cm_dict

class SavePlot(DataPlot):
    def __init__(self, input_dict):
        print('SavePlot')
        # input, init
        self.input_dict = input_dict
        self.init_val()

        # check path & read data
        self.del_no_files()

        # set plot style, range
        self.set_plot_option()

        # plot
        # self.plot_mod()

        # save img        
        self.save_img_each()

    # def init_val(self):
    #     self.max_row = 5
    #     self.fig = self.input_dict['fig']
    #     self.data_type = self.input_dict['data_type']
    #     self.range_type = self.input_dict['range_type']
    #     self.pq_xcol = self.input_dict['pq_xcol']

    def save_img_each(self):
        print('save_img_each in pqc')
        if self.data_type == 'pq':
            ax_n = 3
            col_num = [0, 1, 2]

            figs = []
            axes = []
            for i in range(ax_n):
                figs.append(plt.figure(figsize=(6, 6), tight_layout=True))
                axes.append(figs[i].add_subplot(111))
            
            # TODO:DataPlotと共通化して作る（おそらく、画面配置のみの違い）

            for d, fname in zip(self.d_lst, self.path_lst_checked):
                x = list(map(float, d[0][1:]))
                for i, a in zip(col_num, axes):    
                    y = list(map(float, d[i][1:]))
                    a.plot(x, y, label=fname.parents[0].name)
                    a.set_xlabel(d[0][0])
                    a.set_ylabel(d[i][0])
                    a.legend()
                    a.grid(True)
                    a.set_title('PQ plot')

        if self.ext == 'png':
            for i in range(len(figs)):
                figs[i].savefig(f'{self.fname}_{i}.png', dpi=300, transparent=True)
            messagebox.showinfo(f'write {self.ext.upper()} each', f'Saved {self.fname}_(0~{i}).png')
        elif self.ext == 'pdf':
            with PdfPages(f'{self.fname}.pdf') as pdf:
                for f in figs:
                    pdf.savefig(f)
            messagebox.showinfo(f'write {self.ext.upper()} each', f'Saved {self.fname}.pdf')
        
if __name__ == '__main__':
    pass
