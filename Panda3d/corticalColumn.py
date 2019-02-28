#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:27 2019

@author: osboxes
"""

from neuron import cNeuron
from panda3d.core import NodePath,PandaNode,LODNode,LColor


class cCorticalColumn():
    
    def __init__(self,nOfNeuronsPerColumn):
      self.neurons = []
      for i in range(nOfNeuronsPerColumn):
          n = cNeuron()
          self.neurons.append(n)
        
      self.state = False
            
    def CreateGfx(self,loader,idx):
      #                __node 
      #                /   \
      #  neuronsNodePath   columnBox
        
      self.lod = LODNode('columnLOD')#Level of detail node for Column
      self.__node = NodePath(self.lod)# NodePath(PandaNode('column'))# loader.loadModel("models/box")
      self.__node.setPos(0, 0, 0)
      self.__node.setScale(1, 1, 1)
      
      #self.__node.setTag('clickable',str(idx))#to be able to click on it
           
      
      self.__columnBox = loader.loadModel("cube")      
      self.__columnBox.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
      self.__columnBox.setPos(0, 0, -0.5+ (0 if len(self.neurons)==0 else len(self.neurons)/2))
      self.__columnBox.setScale(0.5, 0.5, 0.5*(1 if len(self.neurons)==0 else len(self.neurons)))
      self.__columnBox.setName('columnBox')
      
      
      self.__neuronsNodePath = NodePath(PandaNode('neuronsNode'))#to pack all neurons into one node path
      self.__neuronsNodePath.setName("column")
      self.__neuronsNodePath.setTag('id',str(idx))#to be able to retrieve index of column for mouse click
      
      
      self.lod.addSwitch(100.0,0.0)
      self.lod.addSwitch(5000.0,100.0)
      
      self.__neuronsNodePath.reparentTo(self.__node)
      self.__columnBox.reparentTo(self.__node)
      
      
      
      z=0
      idx=0
      for n in self.neurons:
          n.CreateGfx(loader,idx)
          idx+=1
          n.getNode().setPos(0,0,z)
          z+=1
          n.getNode().reparentTo(self.__neuronsNodePath)
      
      return
      
    def UpdateState(self,state):
      
      self.state = state
      
      #update column box color (for LOD in distance look)
      if self.state:
        self.__columnBox.setColor(1.0,0.0,0.0,1.0)#red
      else:
        self.__columnBox.setColor(1.0,1.0,1.0,1.0)#white
      
      for n in self.neurons:
        n.state = state
        n.UpdateState()

    def getNode(self):
        return self.__node