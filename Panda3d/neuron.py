#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
import random
from panda3d.core import LColor

class cNeuron():
    
    def __init__(self):
        self.state = False if random.randint(0,1)==0 else True
        
        
    def createGfx(self,loader):
        
        self.__node = loader.loadModel("cube")
        self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)

    def getNode(self):
        return self.__node