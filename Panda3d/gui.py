#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

#from direct.gui.DirectGui import *
#from direct.gui.DirectGuiGlobals import RAISED
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectCheckButton

class cGUI:
    
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
    
  def setWireframe(self,status):
    print(status)
    
  def __init__(self,width,height):
      
    FRAME_WIDTH = 200
    FRAME_HEIGHT = 600
   
    self.myFrame = DirectFrame(frameColor = (0,0,0,0.4),frameSize=(0, FRAME_WIDTH, -FRAME_HEIGHT, 0),#pos=(1, -1, -1),
                                parent=pixel2d,pos=(10,0,-10))#pos=(x,-,-y) origin is center,scale(x,-,y))
    #,scale=(FRAME_WIDTH,1,FRAME_HEIGHT)
    
      
    self.btnFwd = DirectButton(text = ("Step forward"), scale=15,parent=self.myFrame, command=self.btnEv_forward,
                               pos=(50,0,-30))
    
    
    self.btnRunStop = DirectButton(text = ("Run"), scale=15,parent=self.myFrame, command=self.btnEv_StartStop,
                                pos=(50,0,-80))
    
    self.cBox = DirectCheckButton(text = "wireframe",scale=16,parent=self.myFrame,command=self.setWireframe,
                                pos=(60,0,-200))
    
    self.ResetCommands()
    
    
  def ResetCommands(self):
    self.cmdRun=False
    self.cmdStop=False
    self.cmdStepForward=False
    
    
  def onWindowEvent(self,window): # to keep the same size of frame even after resizing
   
    width = window.getProperties().getXSize()
    height = window.getProperties().getYSize()
   
    scaleX = 1000 / width
    scaleY = 1000 / height
    
    self.myFrame.setScale(scaleX,1.0,scaleY)
     
    
  
  
       