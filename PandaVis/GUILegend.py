#!/usr/bin/env python
import PySimpleGUI as sg
import matplotlib
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import pylab
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Colors import *

data = {'active cell': ['patch', COL_CELL_ACTIVE],
        'predictive cell': ['patch', COL_CELL_PREDICTIVE],
        'focused cell': ['patch', COL_CELL_FOCUSED],
        'inactive cell': ['patch', COL_CELL_INACTIVE],
        'correctly predicted cell': ['patch', COL_CELL_CORRECTLY_PREDICTED],
        'false predicted cell': ['patch', COL_CELL_FALSE_PREDICTED],
        'column with one of cells active': ['patch', COL_COLUMN_ONEOFCELLACTIVE],
        'column with one of cells correctly predicted': ['patch', COL_COLUMN_ONEOFCELLCORRECTLY_PREDICTED],
        'column with one of cells predictive': ['patch', COL_COLUMN_ONEOFCELLPREDICTIVE],
        'inactive column': ['patch', COL_COLUMN_INACTIVE],
        'proximal synapses': ['line', COL_PROXIMAL_SYNAPSES],
        'distal synapses': ['line', COL_DISTAL_SYNAPSES],

        }


class GUILegend:
    def __init__(self,showProximalSynapses, showDistalSynapses):
        # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE -----------------------------
        self.figure_canvas_agg = None

        self.figlegend = pylab.figure(figsize=(4, 3))

        self.Update(showProximalSynapses, showDistalSynapses)


        self.legend.get_frame().set_facecolor('#92aa9d')  # fill color in frame
        self.legend.get_frame().set_edgecolor('black')  # frame color
        self.figlegend.set_facecolor('#92aa9d')  # surrounding background color

        self.figure_x, self.figure_y, self.figure_w, self.figure_h = self.figlegend.bbox.bounds

        layout = [[sg.Canvas(background_color='#92aa9d', size=(self.figure_w, self.figure_h), key='canvas')]]

        self.window = sg.Window('a panel', keep_on_top=True, location=(0, 0)).Layout(layout)




    def Update(self,showProximalSynapses, showDistalSynapses):

        print(showProximalSynapses)
        print(showDistalSynapses)
        objs = []
        descriptions = []
        for i in data.keys():

            # don't show colors that can't be shown by settings
            if (not showProximalSynapses and data[i][1] == COL_PROXIMAL_SYNAPSES) or \
                    (not showDistalSynapses and data[i][1] == COL_DISTAL_SYNAPSES):
                print("deleted:"+str(i)+":"+str(data[i][1]))
                continue

            if data[i][0] == 'line':
                objs += [GUILegend.line([data[i][1][0], data[i][1][1], data[i][1][2], data[i][1][3]])]
                descriptions += [i]
            elif data[i][0] == 'patch':
                objs += [GUILegend.patch([data[i][1][0], data[i][1][1], data[i][1][2], data[i][1][3]])]
                descriptions += [i]
        self.legend = self.figlegend.legend(objs, descriptions, 'center')

    @staticmethod
    def line(color):
        return mlines.Line2D([], [], color=color,
                      markersize=15, label="")

    @staticmethod
    def patch(color):
        return mpatches.Patch(color=color, label="")

# ------------------------------- END OF YOUR MATPLOTLIB CODE -------------------------------

# ------------------------------- Beginning of Matplotlib helper code -----------------------

    def draw_figure(self, loc=(0, 0)):
        self.figure_canvas_agg = FigureCanvasTkAgg(self.figlegend, self.window['canvas'].TKCanvas)
        self.figure_canvas_agg.draw()
        self.figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)



# ------------------------------- Beginning of GUI CODE -------------------------------

# # define the window layout
# layout = [[sg.Text('Plot test', font='Any 18')],
#           [sg.Canvas(size=(figure_w, figure_h), key='canvas')],
#           [sg.OK(pad=((figure_w / 2, 0), 3), size=(4, 2))]]
#
# # create the form and show it without the plot
# window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True)
#
# # add the plot to the window
# fig_canvas_agg = draw_figure(window['canvas'].TKCanvas, figlegend)
#
# event, values = window.read()