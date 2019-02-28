#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
import random
from panda3d.core import LColor,CollisionBox,CollisionNode

class cNeuron():
    
    def __init__(self):
      self.state = False if random.randint(0,1)==0 else True
        
        
    def CreateGfx(self,loader,idx):#idx is neccesary to be able to track it down for mouse picking
        
      self.__node = loader.loadModel("cube")
      self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
      self.__node.setPos(0, 0, 0)
      self.__node.setScale(0.5, 0.5, 0.5)
      self.__node.setTag('clickable',str(idx))#to be able to click on it
      self.__node.setName('neuron')
      
      
      #COLLISION
      collBox = CollisionBox(self.__node.getPos(),1.0,1.0,1.0)
      cnodePath = self.__node.attachNewNode(CollisionNode('cnode'))
      cnodePath.node().addSolid(collBox)
      
      
      
      
      self.UpdateState()

    def UpdateState(self):
      if self.state:
        self.__node.setColor(1.0,0.0,0.0,1.0)#red
      else:
        self.__node.setColor(1.0,1.0,1.0,1.0)#white
          
      #self.__node.setRenderModeThickness(5)
      self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        
    def setFocus(self):
      self.__node.setColor(1.0,1.0,0.0,1.0)#yellow
      
    def resetFocus(self):
      self.UpdateState()
      
    def getNode(self):
      return self.__node