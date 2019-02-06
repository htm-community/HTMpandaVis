#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:01 2019

@author: osboxes
"""

from corticalColumn import cCorticalColumn

class cLayer():
        
    def __init__(self,nOfColumns,nOfNeuronsPerColumn):
        self.corticalColumns = []
        for i in range(nOfColumns):
            c = cCorticalColumn(nOfNeuronsPerColumn)
            self.corticalColumns.append(c)
    def createGfx(self,loader):
        
        self.__node = loader.loadModel("models/panda")
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)
        
        y=0
        for c in self.corticalColumns:
            c.createGfx(loader)
            c.getNode().setPos(0,y,0)
            y+=3
            c.getNode().reparentTo(self.__node)
        
        return

    def getNode(self):
        return self.__node