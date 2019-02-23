#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 11:37:36 2019

@author: zz
"""

from panda3d.core import LColor
#import random

class cInputBit():
    
    def __init__(self):
        self.state = False#False if random.randint(0,1)==0 else True
        
        
    def CreateGfx(self,loader):
        
        self.__node = loader.loadModel("cube")
        self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(0.5, 0.5, 0.5)
        
        self.UpdateState()

    def UpdateState(self):
        if self.state:
            self.__node.setColor(0.0,1.0,0.0,1.0)#green
        else:
            self.__node.setColor(1.0,1.0,1.0,1.0)#white
            
        #self.__node.setRenderModeThickness(5)
        self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        
    def getNode(self):
        return self.__node