#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('__file__'))))#adds parent directory to path

from objects.layer import cLayer
from objects.input import cInput
from panda3d.core import NodePath,PandaNode

class cHTM():
 
  layerOffset=0
  inputOffset=0
  
  
  def __init__(self,loader,name):
      
    self.__loader = loader
    self.layers = []
    self.inputs = []

    self.__gfx=None
    self.__node=None
    self.name = name
    
    self.__node = NodePath(PandaNode(name))
  
  
  def CreateLayer(self,name,nOfColumnsPerLayer,nOfCellsPerColumn):
    
    l = cLayer(name,nOfColumnsPerLayer,nOfCellsPerColumn)
    self.layers.append(l)
    
    l.CreateGfx(self.__loader)
    l.getNode().setPos(cHTM.layerOffset, 0, 0)
    
    l.getNode().reparentTo(self.__node)
    #self.__node = NodePath()
    
    cHTM.layerOffset+=40
    
  def CreateInput(self,name,count,rows):
    
    l = cInput(name,count,rows)
    self.inputs.append(l)
    
    l.CreateGfx(self.__loader)
    l.getNode().setPos(-40, cHTM.inputOffset, 0)
    
    l.getNode().reparentTo(self.__node)
    
    cHTM.inputOffset+=5+rows*3
      
      
  def getNode(self):
      return self.__node
  
  def DestroySynapses(self):
      for ly in self.layers:
          ly.DestroySynapses()

  @staticmethod
  def getObjByName(arr,name):
      for i in arr:
          if i.name == name:
              return i