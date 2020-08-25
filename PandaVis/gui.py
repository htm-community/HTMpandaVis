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
from legendWindow import cLegendWindow
from descriptionWindow import cDescriptionWindow
import PySimpleGUI as sg
import json

class cGUI:
    def __init__(self, defaultWidth, defaultHeight, loader, visApp):
        sg.ChangeLookAndFeel('NeutralBlue')#NeutralBlue

        self.focusedCell = None
        self.focusedPath = None
        self.columnID = 0
        self.cellID = 0

        self.visApp = visApp
        self.loader = loader
        self._defaultWidth = defaultWidth
        self._defaultHeight = defaultHeight

        self.ResetCommands()
        self.init = False
        self.terminating = False

        try:
            with open('guiValues.ini', 'r') as file:
                self.defaults = json.loads(file.read())
        except:
            # guiValues doesn't exist, probably is this the first time run
            with open('guiDefaults.ini', 'r') as file:
                self.defaults = json.loads(file.read())


        self.showProximalSynapses = self.getDefault("proximalSynapses")
        self.showOnlyActiveProximalSynapses = self.getDefault("showOnlyProximalSynapses")
        self.showDistalSynapses = self.getDefault("distalSynapses")
        self.showApicalSynapses = self.getDefault("apicalSynapses")
        self.showInputOverlapWithPrevStep = self.getDefault("inputPrevStepOverlap")
        self.showPredictionCorrectness = self.getDefault("predictionCorrectness")
        self.showBursting = self.getDefault("showBursting")

        self.wireframeChanged = True
        self.wireframe = self.getDefault("wireFrame")
        self.transparency = self.getDefault("transparencySlider")
        self.transparencyChanged = True

        self.LODvalue1 = self.getDefault("LODSlider1")
        self.LODvalue2 = self.getDefault("LODSlider2")
        self.LODChanged = True

        self.updateLegend = True
        self.updateDescriptionWindow = True
        self.legend = None
        self.description = None
        self.showLegend = self.getDefault("legend")
        self.showDescription = self.getDefault("desc")

        self.capture = False

        self.iteration = 0
        self.cntIterations = 0

        self.cameraStartLoc = self.getDefault("cameraStartLoc")
        # timer to once upon a time save window position
        # the problem behind this is, that we cant get win pos when user closes the window
        # with cross button, because the event gets called when the window is already destroyed
        self.tmrSaveWinPos = 100
        self.lastWinPos = [0, 0]

        layout = [[sg.Text('Iteration no. 0     ', key = 'iteration')],
                  [sg.Button('STEP -1'), sg.Button('STEP +1')],
                  [sg.Button('RUN'), sg.Button('STOP')],
                  [sg.InputText(self.getDefault("iterationGoto"), key="iterationGoto"), sg.Button('GOTO step')],
                  [sg.Checkbox('Show proximal synapes', key="proximalSynapses", enable_events=True)],
                  [sg.Checkbox('Show only active proximal synapes', key="onlyActiveProximalSynapses", enable_events=True)],
                  [sg.Checkbox('Show distal synapes', key="distalSynapses", enable_events=True)],
                  [sg.Checkbox('Show input overlap with prev.step', key="inputPrevStepOverlap", enable_events=True)],
                  [sg.Checkbox('Show prediction correctness', key="predictionCorrectness", enable_events=True)],
                  [sg.Checkbox('Show bursting', key="showBursting", enable_events=True)],
                  [sg.Checkbox('Wireframe mode', key="wireFrame", enable_events=True)],
                  [sg.Checkbox('Show legend', key="legend", enable_events=True)],
                  [sg.Checkbox('Show description', key="desc", enable_events=True)],
                  [sg.Text('Layer transparency'),
                   sg.Slider(key='transparencySlider', range=(1, 100), orientation='h', size=(10, 10),
                             default_value=100, enable_events=True)],
                  [sg.Frame('Level of detail for columns', [[
                  sg.Slider(key='LODSlider1', range=(1, 1000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True)],
                  [sg.Slider(key='LODSlider2', range=(1, 10000), orientation='h', size=(20, 10),
                            default_value=100, enable_events=True)]])],
                  [sg.Button('capture')],
                  ]

        self.window = sg.Window('Main panel', keep_on_top=True, location=self.getDefault("mainWinPos")).Layout(layout)

    def setIteration(self, iterationNo):
        self.iteration = iterationNo
        self.window["iteration"].update("Iteration no.:"+str(iterationNo))

    def getDefault(self, key):
        try:
            return self.defaults[key]
        except KeyError as e:
            print("Can't load default value:" + str(e))
            return False

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

        self.defaults["mainWinPos"] = self.lastWinPos
        if self.legend is not None:
            self.defaults["legendWinPos"] = self.legend.window.current_location()
        if self.description is not None:
            self.defaults["descWinPos"] = self.description.window.current_location()
        self.defaults["cameraStartLoc"] = self.visApp.env.GetCameraLoc()

    def update(self):

        if not self.init:  # init values at the first run

            self.init = True
            self.window.Read(timeout=10)
            self.updateDefaults()
            return

        if self.updateLegend and self.showLegend:
            self.updateLegend = False
            print("Legend updated")
            if self.legend is not None:
                self.legend.window.close()
            self.legend = cLegendWindow(self.showProximalSynapses, self.showDistalSynapses, self.showInputOverlapWithPrevStep, self.getDefault("legendWinPos"),self.showPredictionCorrectness, self.showBursting)

            self.legend.window.Read(timeout=0)
            self.legend.draw_figure()

        if self.updateDescriptionWindow and self.showDescription:
            self.updateDescriptionWindow = False
            print("Description updated")
            if self.description is not None:
                self.description.window.close()
            self.description = cDescriptionWindow(self.getDefault("descWinPos"))

            self.description.window.Read(timeout=0)

        event, values = self.window.Read(timeout=10)

        if event is None or event == 'Exit':#gui was closed separately by user
            self.Terminate()
            return

        if self.tmrSaveWinPos > 100:
            self.lastWinPos = self.window.current_location()
            self.tmrSaveWinPos = 0
        else:
            self.tmrSaveWinPos += 1

        if event != '__TIMEOUT__':

            if event == "STEP +1":
                print("step +1")
                if(self.iteration + 1 <= self.cntIterations):
                    self.gotoReq = self.iteration + 1
                    self.iteration= self.iteration + 1
            if event == "STEP -1":
                print("step -1")
                if self.iteration > 0:
                    self.gotoReq = self.iteration - 1
                    self.iteration= self.iteration - 1
            elif event == "RUN":
                self.cmdRun = True
            elif event == "STOP":
                self.cmdStop = True
            elif event == "GOTO step":
                try:
                    if (int(values["iterationGoto"]) > self.cntIterations):
                        print("Larger than allowed!")
                    else:
                        self.gotoReq = int(values["iterationGoto"])
                        print("GOTO")
                except:
                    print("It is not a number!")
            elif event == "transparencySlider":
                self.transparency = values["transparencySlider"]
                self.transparencyChanged = True
            elif event == "LODSlider1" or event == "LODSlider2":
                if values["LODSlider2"]>values["LODSlider1"]:
                    self.LODvalue1 = values["LODSlider1"]
                    self.LODvalue2 = values["LODSlider2"]

                    self.LODChanged = True
            elif event in ["proximalSynapses", "distalSynapses", "inputPrevStepOverlap", "predictionCorrectness","showBursting"]:
                self.updateLegend = True

            elif event == "legend":
                if values["legend"]:
                    self.updateLegend = True
                else:
                    self.legend.window.close()
                    self.legend = None
            elif event == "desc":
                if values["desc"]:
                    self.updateDescriptionWindow = True
                else:
                    self.description.window.close()
                    self.description = None
            elif event == 'capture':
                self.capture = True


            self.wireframe = values["wireFrame"]
            self.wireframeChanged = event == "wireFrame"

            self.showProximalSynapses = values["proximalSynapses"]
            self.showOnlyActiveProximalSynapses = values["onlyActiveProximalSynapses"]
            self.showDistalSynapses = values["distalSynapses"]
            self.showInputOverlapWithPrevStep = values["inputPrevStepOverlap"]
            self.showPredictionCorrectness = values["predictionCorrectness"]
            self.showBursting = values["showBursting"]

            self.showLegend = values["legend"]
            self.showDescription = values["desc"]

            print("event "+str(event))
            print("values "+str(values))

    def UpdateDescription(self, txt):
        if self.description is not None:
            self.description.updateText(txt)

    def UpdateCellDescription(self):

        if self.focusedCell is None:
            return
        desc = "path:\n"
        desc += str(self.focusedPath) + "\n"
        desc += "\n---CELL:\n"
        desc += self.focusedCell.getDescription()
        if self.focusedCell.column is not None:
            desc += "\n---COLUMN:\n"
            desc += self.focusedCell.column.getDescription()

        self.UpdateDescription(desc)

    def ResetCommands(self):
        self.cmdRun = False
        self.cmdStop = False
        self.cmdStepForward = False
        self.gotoReq = -1


    def Terminate(self): #  event when app exit
        self.retrieveDefaults()
        try:
            with open('guiValues.ini', 'w') as file:
                file.write(json.dumps(self.defaults))
        except:
            self.defaults = {}
            print("Wasn't able to save defaults into file guiValues.ini !!")
        self.terminating = True # this will terminate main app
