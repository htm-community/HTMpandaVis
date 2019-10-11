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
import json

class cGUI:
    def __init__(self, defaultWidth, defaultHeight, loader, visApp):
        sg.ChangeLookAndFeel('NeutralBlue')#NeutralBlue

        self.focusedCell = None
        self.focusedPath = None
        self.columnID = 0

        self.visApp = visApp
        self.loader = loader
        self._defaultWidth = defaultWidth
        self._defaultHeight = defaultHeight

        self.ResetCommands()
        self.init = False

        try:
            with open('guiDefaults.ini', 'r') as file:
                self.defaults = json.loads(file.read())
        except:
            self.defaults = {}

        self.showProximalSynapses = self.defaults["proximalSynapses"]
        self.showDistalSynapses = self.defaults["distalSynapses"]

        self.wireframeChanged = True
        self.wireframe = self.defaults["wireFrame"]
        self.transparency = self.defaults["transparencySlider"]
        self.transparencyChanged = True

        self.LODvalue1 = self.defaults["LODSlider1"]
        self.LODvalue2 = self.defaults["LODSlider2"]
        self.LODChanged = True

        self.updateLegend = True
        self.legend = None

        layout = [[sg.Button('ONE STEP')],
                  [sg.Button('RUN'), sg.Button('STOP')],
                  [sg.Checkbox('Show proximal synapes', key="proximalSynapses", enable_events=True)],
                  [sg.Checkbox('Show distal synapes', key="distalSynapses", enable_events=True)],
                  [sg.Checkbox('Wireframe mode', key="wireFrame", enable_events=True)],
                  [sg.Text('Layer transparency'),
                   sg.Slider(key='transparencySlider', range=(1, 100), orientation='h', size=(20, 10),
                             default_value=100, enable_events=True)],
                  [sg.Frame('Level of detail for columns', [[
                  sg.Slider(key='LODSlider1', range=(1, 1000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True)],
                  [sg.Slider(key='LODSlider2', range=(1, 10000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True)]])]
                  ]

        self.window = sg.Window('Main panel', keep_on_top=True, location=(0, 0)).Layout(layout)

    def updateDefaults(self):
        for o in self.window.AllKeysDict:
            try:
                self.window[o].Update(self.defaults[o])
            except:
                continue
                #print("Default not for:"+str(o))

    def retrieveDefaults(self):

        event, values = self.window.Read(timeout=10)

        if values is not None:
            for o in values:
                try:
                    self.defaults[o] = values[o]
                except Exception as e:
                    print(e)
                    print("Default not for:"+str(o))

    def update(self):

        if not self.init:  # init values at the first run

            self.init = True
            self.window.Read(timeout=10)
            self.updateDefaults()
            return

        if self.updateLegend:
            self.updateLegend = False
            print("Legend updated")
            if self.legend is not None:
                self.legend.window.close()
            self.legend = GUILegend(self.showProximalSynapses, self.showDistalSynapses)

            self.legend.window.Read(timeout=0)
            #self.legend = GUILegend(self.showProximalSynapses, self.showDistalSynapses)
            #self.legend.Update(self.showProximalSynapses, self.showDistalSynapses)
            self.legend.draw_figure()
            #self.window['canvas'].TKCanvas.delete(self.legend.figure_canvas_agg)

            #self.legend.figure_canvas_agg.delete("all")
            #self.legend.Update(False, False)
            #self.legend.figure_canvas_agg.draw()



        event, values = self.window.Read(timeout=10)

        if event is None or event == 'Exit':#gui was closed separately by user
            self.Terminate()
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
            elif event == "proximalSynapses" or event == "distalSynapses":
                #self.legend.Update(values["proximalSynapses"], values["distalSynapses"])# update legend
                self.updateLegend = True

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

    def Terminate(self): #  event when app exit
        self.retrieveDefaults()
        try:
            with open('guiDefaults.ini', 'w') as file:
                file.write(json.dumps(self.defaults))
        except:
            self.defaults = {}