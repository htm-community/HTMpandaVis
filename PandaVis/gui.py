#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

from direct.gui.DirectGuiGlobals import RAISED, SUNKEN, GROOVE, RIDGE
from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectCheckButton,
    DirectLabel,
    DirectEntry,
    OnscreenText,
)
from pandac.PandaModules import TextNode


class cGUI:
    def btnEv_forward(self):
        print("Forward")
        self.cmdStepForward = True

    def btnEv_StartStop(self):
        print("StartStop")
        if self.btnRunStop["text"] == "Run":
            self.btnRunStop.setText("Stop")
            self.cmdRun = True
        else:
            self.btnRunStop.setText("Run")
            self.cmdStop = True

    def __init__(self, defaultWidth, defaultHeight, loader, visApp):

        self.focusedCell = None
        self.focusedPath = None
        self.columnID = 0
        
        self.showProximalSynapses=True
        self.showDistalSynapses=True
        self.wireframeChanged = False
        self.wireframe = False
        
        
        # self.setWireframe = None
        self.visApp = visApp
        self.loader = loader
        FRAME_WIDTH = 200
        FRAME_HEIGHT = 600
        self._defaultWidth = defaultWidth
        self._defaultHeight = defaultHeight

        self.myFrame = DirectFrame(
            frameColor=Color(73, 73, 73, 215),
            frameSize=(0, FRAME_WIDTH, -FRAME_HEIGHT, 0),  # pos=(1, -1, -1),
            parent=pixel2d,
            pos=(10, 0, -10),
        )  # pos=(x,-,-y) origin is center,scale(x,-,y))

        self.btnFwd = DirectButton(
            text=("Step forward"),
            scale=14,
            parent=self.myFrame,
            command=self.btnEv_forward,
            pos=(100, 0, -60),
        )

        self.btnRunStop = DirectButton(
            text=("Run"),
            scale=14,
            parent=self.myFrame,
            command=self.btnEv_StartStop,
            pos=(100, 0, -120),
        )

        self.ButtonStyle1(self.btnFwd)
        self.ButtonStyle1(self.btnRunStop)

        self.cBoxProxSyn = DirectCheckButton(text = "Show proximal syn.",scale=12,parent=self.myFrame,command=self.onShowProxSynapses,
        pos=(100,0,-160))
        self.cBoxProxSyn["indicatorValue"] = self.showProximalSynapses
        self.cBoxProxSyn.setIndicatorValue()

        self.cBoxDistSyn = DirectCheckButton(text = "Show distal syn.",scale=12,parent=self.myFrame,command=self.onShowDistSynapses,
        pos=(100,0,-180))
        self.cBoxDistSyn["indicatorValue"] = self.showDistalSynapses
        self.cBoxDistSyn.setIndicatorValue()

        self.cBoxWireframe = DirectCheckButton(text = "Wireframe",scale=12,parent=self.myFrame,command=self.onChangeWireframe,
        pos=(100,0,-200))
        
        self.speedText = OnscreenText(
            text="Speed",
            scale=14,
            parent=self.myFrame,
            pos=(20, -220, 0),
            fg=(1, 1.0, 1.0, 1),
            align=TextNode.ALeft,
            mayChange=1,
        )

        self.speedEntry = DirectEntry(
            text="",
            scale=14,
            parent=self.myFrame,
            command=self.onSpeedChange,
            pos=(40, 0, -240),
            initialText=str(visApp.speed),
            numLines=1,
            focus=0,
        )
        
        self.hints = OnscreenText(
            text="hints:\nPress spacebar for boost",
            scale=14,
            parent=self.myFrame,
            pos=(20, -280, 0),
            fg=(1, 1.0, 1.0, 1),
            align=TextNode.ALeft,
            mayChange=1,
        )

        self.CheckBoxStyle1(self.cBoxProxSyn)
        self.CheckBoxStyle1(self.cBoxDistSyn)

        self.ResetCommands()

 

    def ResetCommands(self):
        self.cmdRun = False
        self.cmdStop = False
        self.cmdStepForward = False

    def onSpeedBoostChanged(self, value):
        if not value:
            self.speedText.text = "Speed"
            self.speedText.fg = (1, 1.0, 1.0, 1)
        else:
            self.speedText.text = "Speed [BOOST]"
            self.speedText.fg = (1, 0.5, 0.5, 1)

    def onShowProxSynapses(self,value):
        self.showProximalSynapses=value
        #showProximalSynapses
    def onShowDistSynapses(self,value):
        self.showDistalSynapses=value
        
    def onChangeWireframe(self, value):
        self.wireframe = value
        self.wireframeChanged = True
        
    def onSpeedChange(self, value):
        try:
            self.speed = int(value)
        except:
            return
        
    def onWindowEvent(
        self, window
    ):  # to keep the same size of frame even after resizing
        # return
        width = window.getProperties().getXSize()
        height = window.getProperties().getYSize()

        # pixel2d is constructed with default resolution, so we need to calculate scaling with it
        scaleX = self._defaultWidth / width
        scaleY = self._defaultHeight / height

        self.myFrame.setScale(scaleX, 1.0, scaleY)

    def ButtonStyle1(self, btn):
        btn["frameColor"] = Color(62, 135, 34, 255)
        btn["text_fg"] = (255, 255, 255, 255)
        btn["frameSize"] = (-5, 5, -1.5, 2)  # left,right,bottom,top
        btn["text_font"] = self.loader.loadFont("Ubuntu-B.ttf")

    def CheckBoxStyle1(self, box):
        box["frameColor"] = Color(0, 0, 0, 0)
        box["text_fg"] = (255, 255, 255, 255)
        box["text_pos"]=(2,0)
        box["frameSize"] = (-5, 5, -0.5, 1)  # left,right,bottom,top
        box["text_font"] = self.loader.loadFont("Ubuntu-B.ttf")


def Color(
    r, g, b, a
):  # converts color from fromat 255,255,255 to panda format 1.0,1.0,1.0
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)
