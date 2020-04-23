#!/usr/bin/env python
import PySimpleGUI as sg
import matplotlib
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import pylab
import math
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Colors import *

data = {'----- CELLS -----': ['patch', COL_SEPARATOR],
        'active cell': ['patch', COL_CELL_ACTIVE],
        'winner cell': ['patch', COL_CELL_WINNER],
        'predictive cell': ['patch', COL_CELL_PREDICTIVE],
        'active&predictive cell': ['patch', COL_CELL_ACTIVE_AND_PREDICTIVE],
        'focused cell': ['patch', COL_CELL_FOCUSED],
        'inactive cell': ['patch', COL_CELL_INACTIVE],
        'correctly predicted cell': ['patch', COL_CELL_CORRECTLY_PREDICTED],
        'falsely predicted cell': ['patch', COL_CELL_FALSELY_PREDICTED],
        '---- COLUMNS ----': ['patch', COL_SEPARATOR],
        'active column': ['patch', COL_COLUMN_ACTIVE],
        'bursting column': ['patch', COL_COLUMN_BURSTING],
        'column with one of cells correctly predicted': ['patch', COL_COLUMN_ONEOFCELLCORRECTLY_PREDICTED],
        'column with one of cells falsely predicted': ['patch', COL_COLUMN_ONEOFCELLFALSELY_PREDICTED],
        'column with one of cells predictive': ['patch', COL_COLUMN_ONEOFCELLPREDICTIVE],
        'active column & with one of cells predictive': ['patch', COL_COLUMN_ACTIVE_AND_ONEOFCELLPREDICTIVE],
        'inactive column': ['patch', COL_COLUMN_INACTIVE],
        '----- INPUTS -----': ['patch', COL_SEPARATOR],
        'overlapping input bit': ['patch', IN_BIT_OVERLAPPING],
        '---- SYNAPSES ----': ['patch', COL_SEPARATOR],
        'inactive proximal synapses': ['line', COL_PROXIMAL_SYNAPSES_INACTIVE],
        'active proximal synapses': ['line', COL_PROXIMAL_SYNAPSES_ACTIVE],
        'inactive distal synapses': ['line', COL_DISTAL_SYNAPSES_INACTIVE],
        'active distal synapses': ['line', COL_DISTAL_SYNAPSES_ACTIVE],
        }


class cLegendWindow:
    def __init__(self,showProximalSynapses, showDistalSynapses, showInputOverlapWithPrevStep, winPos, showPredictionCorrectness, showBursting):
        # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE -----------------------------
        self.figure_canvas_agg = None

        objs = []
        descriptions = []
        itemCnt = 0
        for i in data.keys():

            # don't show colors that can't be shown by settings
            if (not showProximalSynapses and (i in ['inactive proximal synapses','active proximal synapses']) or \
                not showDistalSynapses and (i in ['inactive distal synapses','active distal synapses']) or \
                not showInputOverlapWithPrevStep and i == 'overlapping input bit') or \
                not showPredictionCorrectness and (i in ['correctly predicted cell','falsely predicted cell','column with one of cells correctly predicted', 'column with one of cells falsely predicted']) or \
                not showBursting and (i in ['bursting column']):
                #print("deleted:" + str(i) + ":" + str(data[i][1]))
                continue

            if data[i][0] == 'line':
                objs += [cLegendWindow.line([data[i][1][0], data[i][1][1], data[i][1][2], data[i][1][3]])]
                descriptions += [i]
            elif data[i][0] == 'patch':
                objs += [cLegendWindow.patch([data[i][1][0], data[i][1][1], data[i][1][2], data[i][1][3]])]
                descriptions += [i]

            itemCnt += 1

        self.figlegend = pylab.figure(figsize=(4, itemCnt/22.0*5))  #size according to item count

        self.legend = self.figlegend.legend(objs, descriptions, 'center')

        self.legend.get_frame().set_facecolor('#92aa9d')  # fill color in frame
        self.legend.get_frame().set_edgecolor('black')  # frame color
        self.figlegend.set_facecolor('#92aa9d')  # surrounding background color

        self.figure_x, self.figure_y, self.figure_w, self.figure_h = self.figlegend.bbox.bounds

        layout = [[sg.Canvas(background_color='#92aa9d', size=(self.figure_w, self.figure_h), key='canvas')],
                  [sg.Text('WSAD, Shift, Ctrl to move around')],
                  [sg.Text('SPACEBAR toggle for boost speed')],
                  [sg.Text('ESC to cancel focus')]]

        self.window = sg.Window('Legend', keep_on_top=True, location=winPos).Layout(layout)


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