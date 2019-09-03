#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

from direct.gui.DirectGuiGlobals import RAISED,SUNKEN,GROOVE,RIDGE
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
    
  def __init__(self,defaultWidth,defaultHeight,loader,fWireframe):
    
    #self.setWireframe = None
    
    self.loader = loader
    FRAME_WIDTH = 200
    FRAME_HEIGHT = 600
    self._defaultWidth = defaultWidth
    self._defaultHeight = defaultHeight
    
    self.myFrame = DirectFrame(frameColor = Color(73,73,73,215),frameSize=(0, FRAME_WIDTH, -FRAME_HEIGHT, 0),#pos=(1, -1, -1),
                                parent=pixel2d,pos=(10,0,-10))#pos=(x,-,-y) origin is center,scale(x,-,y))
        
    
    self.btnFwd = DirectButton(text = ("Step forward"), scale=14,parent=self.myFrame, command=self.btnEv_forward,
                               pos=(100,0,-60))
    
    
    
    
    self.btnRunStop = DirectButton(text = ("Run"), scale=14,parent=self.myFrame, command=self.btnEv_StartStop,
                                   pos=(100,0,-120))
    
    self.ButtonStyle1(self.btnFwd)
    self.ButtonStyle1(self.btnRunStop)
    
    self.cBox = DirectCheckButton(text = "wireframe",scale=14,parent=self.myFrame,command=fWireframe,
                                pos=(100,0,-200))
    
    self.cBox2 = DirectCheckButton(text = "some option",scale=14,parent=self.myFrame,
                                pos=(100,0,-220))
    
    self.CheckBoxStyle1(self.cBox)
    self.CheckBoxStyle1(self.cBox2)
    
    self.ResetCommands()
    
    self.focusCursor = None
    

    
  def ResetCommands(self):
    self.cmdRun=False
    self.cmdStop=False
    self.cmdStepForward=False
    self.cmdGetColumnData=False

    
  def onWindowEvent(self,window): # to keep the same size of frame even after resizing
    #return
    width = window.getProperties().getXSize()
    height = window.getProperties().getYSize()
    
    #pixel2d is constructed with default resolution, so we need to calculate scaling with it
    scaleX = self._defaultWidth / width          
    scaleY = self._defaultHeight / height
    
    self.myFrame.setScale(scaleX,1.0,scaleY)
    
  def ButtonStyle1(self,btn):
    btn['frameColor']=Color(62,135,34,255)
    btn['text_fg']=(255,255,255,255)
    btn['frameSize']=(-5,5,-1.5,2)#left,right,bottom,top
    btn['text_font']= self.loader.loadFont('Ubuntu-B.ttf')
  
  def CheckBoxStyle1(self,box):
    box['frameColor']=Color(0,0,0,0)
    box['text_fg']=(255,255,255,255)
    box['frameSize']=(-5,5,-0.5,1)#left,right,bottom,top
    box['text_font']= self.loader.loadFont('Ubuntu-B.ttf')
    
  
def Color(r,g,b,a):#converts color from fromat 255,255,255 to panda format 1.0,1.0,1.0
  return (r/255.0,g/255.0,b/255.0,a/255.0)


    
  
  
       