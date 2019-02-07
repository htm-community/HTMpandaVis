#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:45:18 2019

@author: osboxes
"""

from layer import cLayer
from panda3d.core import NodePath,PandaNode

class cHTM():
 
    def __init__(self):
        nOfLayers=3
        nOfColumnsPerLayer=20
        nOfNeuronsPerColumn=3
        
        self.layers = []
        for i in range(nOfLayers):
            l = cLayer('',nOfColumnsPerLayer,nOfNeuronsPerColumn)
            self.layers.append(l)
    
        self.__gfx=None
        self.__node=None
    
    def CreateGfx(self,loader):
        
        self.__node = NodePath(PandaNode('HTM1'))#TextNode('layerText')#loader.loadModel("models/teapot")
        #self.__node.setPos(0, 0, 20)
        
        
        x=0
        for l in self.layers:
            l.CreateGfx(loader)
            l.getNode().setPos(x, 0, 0)
            x+=40
            l.getNode().reparentTo(self.__node)
        
        #self.__node = NodePath()
        
        
    def getNode(self):
        return self.__node
        