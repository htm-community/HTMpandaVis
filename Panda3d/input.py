#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 11:32:40 2019

@author: zz
"""
from panda3d.core import NodePath,PandaNode,TextNode
from inputBit import cInputBit

class cInput():
  
  def __init__(self,name,count,rows):
    
    self.name = name
    self.count = count
    self.rows = rows
        
    self.inputBits = []
    for i in range(count):
        c = cInputBit()
        self.inputBits.append(c)
      
    
  def CreateGfx(self,loader):
      
      self.__node = NodePath(PandaNode('Input'))#TextNode('layerText')#loader.loadModel("models/teapot")
      
      text = TextNode('name text')
      text.setText(self.name)
      
      textNodePath = self.__node.attachNewNode(text)
      textNodePath.setScale(2)
      textNodePath.setPos(0,-5,0)
      
      # value string that represents what is encoded into SDR
      textVal = TextNode('value text')
      textVal.setText("no value")
      
      textValNodePath = self.__node.attachNewNode(textVal)
      textValNodePath.setScale(2)
      textValNodePath.setPos(0,-5+(self.rows*3)/2,3*self.count/self.rows)
      textValNodePath.setHpr(90,0,0)
      
          
      self.__node.setPos(0, 0, 0)
      self.__node.setScale(1, 1, 1)
      
      
      y=0
      z=0
      cursor=0
      idx=0
      for c in self.inputBits:
          c.CreateGfx(loader,idx)
          c.getNode().setPos(0,y,z)
          y+=3
          
          idx+=1
          cursor+=1
          if cursor>= self.rows:
            cursor=0
            z+=3
            y=0

          c.getNode().reparentTo(self.__node)
      
      return
    
  def UpdateState(self,data,text):
    
    if len(data)!=self.count:
      print("Given data for input does not match number of bits in input!")
      print("A:"+str(self.count)+" B:"+str(len(data)))
      return
    
    for i in range(len(data)):
      self.inputBits[i].state = False if data[i]==0 else True
      
      self.inputBits[i].UpdateState()
      

  def getNode(self):
      return self.__node