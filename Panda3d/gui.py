#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

from direct.gui.DirectGui import DirectFrame,DirectButton

class cGUI:
  PANEL_WIDTH_PX = 100 # width in pixels
  
  def btnEvent(self):
    print("EVENT")
    
  def __init__(self,width,height):
      
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 600
   
    self.myFrame = DirectFrame(frameColor = (0,0,0,0.3),frameSize=(0, FRAME_WIDTH, -FRAME_HEIGHT, 0),#pos=(1, -1, -1),
                                parent=pixel2d,pos=(10,0,-10))#pos=(x,-,-y) origin is center,scale(x,-,y))
    #,scale=(FRAME_WIDTH,1,FRAME_HEIGHT)
      
    self.button = DirectButton(text = ("OK", "click!", "rolling over", "disabled"), scale=0.1,parent=self.myFrame, command=self.btnEvent)
    self.button.setPos(40,0,-50)
    
  
  def onWindowEvent(self,window):
   
    width = window.getProperties().getXSize()
    height = window.getProperties().getYSize()
   
    scaleX = cGUI.PANEL_WIDTH_PX / width
    ratio = width/height
     
    
  
  
       