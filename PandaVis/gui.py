#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectCheckButton,
    DirectLabel,
    DirectEntry,
    OnscreenText,
)
from GUILegend import GUILegend
import PySimpleGUI as sg

class cGUI:
    def __init__(self, defaultWidth, defaultHeight, loader, visApp):
        sg.ChangeLookAndFeel('NeutralBlue')#NeutralBlue




        self.focusedCell = None
        self.focusedPath = None
        self.columnID = 0

        self.showProximalSynapses = True
        self.showDistalSynapses = True

        self.wireframeChanged = False
        self.wireframe = False
        self.transparency = 100
        self.transparencyChanged = False

        self.LODvalue1 = 100
        self.LODvalue2 = 5000
        self.LODChanged = True

        self.visApp = visApp
        self.loader = loader
        self._defaultWidth = defaultWidth
        self._defaultHeight = defaultHeight

        self.ResetCommands()
        self.terminate = False
        self.init = False

        self.legend = GUILegend()
        layout = [[sg.Button('ONE STEP')],
                  [sg.Button('RUN'), sg.Button('STOP')],
                  [sg.Checkbox('Show proximal synapes', key="proximalSynapses", enable_events=True)],
                  [sg.Checkbox('Show distal synapes', key="distalSynapses", enable_events=True)],
                  [sg.Checkbox('Wireframe mode', key="wireFrame", enable_events=True)],
                  [sg.Text('Layer transparency'),
                   sg.Slider(key='transparencySlider', range=(1, 100), orientation='h', size=(20, 10),
                             default_value=100, enable_events=True)],
                  [sg.Text('LOD columns'),
                  sg.Slider(key='LODSlider1', range=(1, 1000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True),
                  sg.Slider(key='LODSlider2', range=(1, 10000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True)],
                  [sg.Canvas(background_color='#92aa9d', size=(self.legend.figure_w, self.legend.figure_h), key='canvas')]
                  ]

        self.window = sg.Window('Main panel', keep_on_top=True, location=(0, 0)).Layout(layout)


    def update(self):

        if not self.init: # init values at the first run
            self.init = True
            self.window.Read(timeout=10)

            self.window.Element('distalSynapses').Update(self.showDistalSynapses)
            self.window.Element('proximalSynapses').Update(self.showProximalSynapses)

            fig_canvas_agg = self.legend.draw_figure(self.window['canvas'].TKCanvas, self.legend.figlegend)
            return

        event, values = self.window.Read(timeout=10)


        if event is None or event == 'Exit':
            self.terminate = True
            return

        if event != '__TIMEOUT__':

            if event == "ONE STEP":
                self.cmdStepForward = True
                print("one step")
            elif event == "RUN":
                self.cmdRun = True
            elif event == "STOP":
                self.cmdStop = True
            elif event == "transparencySlider":
                self.transparency = values["transparencySlider"]
                self.transparencyChanged = True
            elif event == "LODSlider1" or event == "LODSlider2":
                if values["LODSlider2"]>values["LODSlider1"]:
                    self.LODvalue1 = values["LODSlider1"]
                    self.LODvalue2 = values["LODSlider2"]

                    self.LODChanged = True

            self.wireframe = values["wireFrame"]
            self.wireframeChanged = event == "wireFrame"

            self.showProximalSynapses = values["proximalSynapses"]
            self.showDistalSynapses = values["distalSynapses"]

            print("event "+str(event))
            print("values "+str(values))


    def ResetCommands(self):
        self.cmdRun = False
        self.cmdStop = False
        self.cmdStepForward = False
