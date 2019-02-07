#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:27 2019

@author: osboxes
"""

from neuron import cNeuron
from panda3d.core import NodePath,PandaNode


class cCorticalColumn():
    
    def __init__(self,nOfNeuronsPerColumn):
        self.neurons = []
        for i in range(nOfNeuronsPerColumn):
            n = cNeuron()
            self.neurons.append(n)
            
    def CreateGfx(self,loader):
        
        self.__node = NodePath(PandaNode('column'))# loader.loadModel("models/box")
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)
        
        z=0
        for n in self.neurons:
            n.CreateGfx(loader)
            n.getNode().setPos(0,0,z)
            z+=1
            n.getNode().reparentTo(self.__node)
        
        return

    def getNode(self):
        return self.__node