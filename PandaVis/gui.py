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
from pandac.PandaModules import TextNode

import PySimpleGUI as sg

class cGUI:
    def __init__(self, defaultWidth, defaultHeight, loader, visApp):
        sg.ChangeLookAndFeel('NeutralBlue')#NeutralBlue

        layout = [ [sg.Button('ONE STEP')],
                   [sg.Button('RUN'), sg.Button('STOP')],
                   [sg.Checkbox('Show proximal synapes',key="proximalSynapses",enable_events=True)],
                   [sg.Checkbox('Show distal synapes',key="distalSynapses",enable_events=True)],
                   [sg.Checkbox('Wireframe mode',key="wireFrame",enable_events=True)],
                   [sg.Submit()] ]

        self.window = sg.Window('Main panel',keep_on_top = True, location=(0, 0)).Layout(layout)

        self.focusedCell = None
        self.focusedPath = None
        self.columnID = 0

        self.showProximalSynapses = True
        self.showDistalSynapses = True

        self.wireframeChanged = False
        self.wireframe = False

        self.visApp = visApp
        self.loader = loader
        self._defaultWidth = defaultWidth
        self._defaultHeight = defaultHeight

        self.ResetCommands()
        self.terminate = False

    def update(self):
        self.window.Read(timeout=10)

        self.window.Element('distalSynapses').Update(self.showDistalSynapses)
        self.window.Element('proximalSynapses').Update(self.showProximalSynapses)

        while not self.terminate:
            event, values = self.window.Read(timeout=10)


            if event is None or event == 'Exit':
                self.terminate = False
                break

            if event != '__TIMEOUT__':

                if event == "ONE STEP":
                    self.cmdStepForward = True
                    print("one step")
                elif event == "RUN":
                    self.cmdRun = True
                elif event == " STOP":
                    self.cmdStop = True

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
