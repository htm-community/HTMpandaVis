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
        
    scaleX = cGUI.PANEL_WIDTH_PX / width
   
    ratio = width/height
   
    self.myFrame = DirectFrame(frameColor = (0,0,0,0.3),frameSize=(-1, 1, -1, 1),pos=(1, -1, -1))#left,right,bottom,top #x,y,z
    
    self.myFrame.reparentTo(pixel2d)
    self.myFrame.setPos(0, 0, 0)
    self.myFrame.setScale(364, 1, 50)
        
    #self.myFrame.setPos(100,0,-100)
    #self.myFrame = DirectFrame(frameColor = (0,0,0,0.3),frameSize=(0,scaleX*ratio*2,-1,1),#left,right,bottom,top
                             #pos=(-ratio,0,0))#x,y,z
 
  
    #self.button = DirectButton(text = ("OK", "click!", "rolling over", "disabled"), scale=.05, command=self.btnEvent)
    
    #self.button.reparentTo(self.myFrame)
  
  def onWindowEvent(self,window):
   
    width = window.getProperties().getXSize()
    height = window.getProperties().getYSize()
   
    scaleX = cGUI.PANEL_WIDTH_PX / width
    ratio = width/height
     
    
  
  
       