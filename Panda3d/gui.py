#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

#from direct.gui.DirectGui import *
#from direct.gui.DirectGuiGlobals import RAISED
from direct.gui.DirectGui import DirectFrame,DirectButton

class cGUI:
  PANEL_WIDTH_PX = 100 # width in pixels
  
    
  def btnEv_forward(self):
    print("Forward")
    self.cmdStepForward=True
  def btnEv_StartStop(self):
    print("StartStop")
    if self.btnRunStop['text']=='Run':
        self.btnRunStop.setText("Stop")
        self.cmdRun=True
    else:
        self.btnRunStop.setText("Run")
        self.cmdStop=True
    
  def __init__(self,width,height):
      
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 600
   
    self.myFrame = DirectFrame(frameColor = (0,0,0,0.3),frameSize=(0, FRAME_WIDTH, -FRAME_HEIGHT, 0),#pos=(1, -1, -1),
                                parent=pixel2d,pos=(10,0,-10))#pos=(x,-,-y) origin is center,scale(x,-,y))
    #,scale=(FRAME_WIDTH,1,FRAME_HEIGHT)
    
      
    self.btnFwd = DirectButton(text = ("Step forward"), scale=15,parent=self.myFrame, command=self.btnEv_forward,
                               pos=(50,0,-30))
    
    
    self.btnRunStop = DirectButton(text = ("Run"), scale=15,parent=self.myFrame, command=self.btnEv_StartStop,
                                pos=(50,0,-80))
    
    self.ResetCommands()
    
    
  def ResetCommands(self):
    self.cmdRun=False
    self.cmdStop=False
    self.cmdStepForward=False
    
    
  def onWindowEvent(self,window):
   
    width = window.getProperties().getXSize()
    height = window.getProperties().getYSize()
   
    scaleX = cGUI.PANEL_WIDTH_PX / width
    ratio = width/height
     
    
  
  
       