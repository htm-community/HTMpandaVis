#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from objects.corticalColumn import cCorticalColumn
from panda3d.core import NodePath,PandaNode,TextNode

class cLayer():
        
    def __init__(self,name,nOfColumns,nOfCellsPerColumn):
        
        self.name=name
        
        self.corticalColumns = []
        for i in range(nOfColumns):
            c = cCorticalColumn(nOfCellsPerColumn)
            self.corticalColumns.append(c)
            
    def CreateGfx(self,loader):
        
        self.__node = NodePath(PandaNode('Layer_'+self.name))#TextNode('layerText')#loader.loadModel("models/teapot")
        
        text = TextNode('Layer text node')
        text.setText(self.name)
        
        textNodePath = self.__node.attachNewNode(text)
        textNodePath.setScale(2)
        
        textNodePath.setPos(0,-5,0)
            
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)
        
        y = 0
        idx = 0
        row = 0
        for c in self.corticalColumns:
            c.CreateGfx(loader,idx)
            idx+=1
            c.getNode().setPos(row*10,y,0)
            y+=3
            
            if y>150:
                y=0
                row+=1
            c.getNode().reparentTo(self.__node)
        
        return
    
    def UpdateState(self,activeColumns,activeCells):
    
      #print("COLUMNS SIZE:"+str(len(self.corticalColumns)))
      
      for col in self.corticalColumns:
        col.UpdateState(False)
      
      for i in activeColumns:
        #print("COLUMNS SIZE:"+str(len(self.corticalColumns)))
        #print(i)
        self.corticalColumns[i].UpdateState(True)
      

    def getNode(self):
        return self.__node
    
    def DestroySynapses(self):
        for col in self.corticalColumns:
            col.DestroySynapses()