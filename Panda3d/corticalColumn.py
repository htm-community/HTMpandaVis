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
          
        self.state = False
            
    def CreateGfx(self,loader,idx):
        
        self.__node = NodePath(PandaNode('column'))# loader.loadModel("models/box")
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)
        
        self.__node.setTag('clickable',str(idx))#to be able to click on it
        
        z=0
        idx=0
        for n in self.neurons:
            n.CreateGfx(loader,idx)
            idx+=1
            n.getNode().setPos(0,0,z)
            z+=1
            n.getNode().reparentTo(self.__node)
        
        return
      
    def UpdateState(self,state):
      
      self.state = state
      
      for n in self.neurons:
        n.state = state
        n.UpdateState()

    def getNode(self):
        return self.__node