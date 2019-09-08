#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
from panda3d.core import LColor, CollisionBox, CollisionNode


class cCell:
    def __init__(self, column):
        self.active = False
        self.predictive = False
        
        self.column = column  # to be able to track column that this cell belongs to

    def CreateGfx(
        self, loader, idx
    ):  # idx is neccesary to be able to track it down for mouse picking

        self.__node = loader.loadModel("models/cube")
        # self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(0.5, 0.5, 0.5)
        self.__node.setTag("clickable", str(idx))  # to be able to click on it
        self.__node.setName("cell")

        # COLLISION
        collBox = CollisionBox(self.__node.getPos(), 1.0, 1.0, 1.0)
        cnodePath = self.__node.attachNewNode(CollisionNode("cnode"))
        cnodePath.node().addSolid(collBox)

        self.UpdateState(False, False)

    def UpdateState(self, active, predictive, focused=False):
        
        self.active = active
        self.predictive = predictive
        self.focused = focused
        
        if self.focused:
            self.__node.setColor(1.0, 1.0, 0.0, 1.0)  # yellow
        elif self.predictive:
            self.__node.setColor(0.0, 0.0, 1.0, 1.0)  # blue
        elif self.active:
            self.__node.setColor(1.0, 0.0, 0.0, 1.0)  # red
        else:
            self.__node.setColor(1.0, 1.0, 1.0, 1.0)  # white


        # self.__node.setRenderModeThickness(5)
        self.__node.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))

    def setFocus(self):
        self.UpdateState(self.active,self.predictive,True)# no change except focus

    def resetFocus(self):
        self.UpdateState(self.active,self.predictive,False)# no change except focus
        

    def getNode(self):
        return self.__node
