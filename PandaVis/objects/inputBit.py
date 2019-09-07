#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 11:37:36 2019

@author: zz
"""

from panda3d.core import LColor, CollisionNode, CollisionBox

# import random


class cInputBit:
    def __init__(self):
        self.state = False  # False if random.randint(0,1)==0 else True
        self.__node = None
        self.__highlight = False

    def CreateGfx(self, loader, idx):

        self.__node = loader.loadModel("models/cube")
        self.__node.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(0.5, 0.5, 0.5)

        self.__node.setTag("clickable", str(idx))  # to be able to click on it
        self.__node.setName("inputBit")

        # COLLISION
        collBox = CollisionBox(self.__node.getPos(), 1.0, 1.0, 1.0)
        cnodePath = self.__node.attachNewNode(CollisionNode("cnode"))
        cnodePath.node().addSolid(collBox)

        self.UpdateState()

    def UpdateState(self):
        if self.state:
            self.__node.setColor(0.0, 1.0, 0.0, 1.0)  # green
        else:
            self.__node.setColor(1.0, 1.0, 1.0, 1.0)  # white

        if self.__highlight:
            col = self.__node.getColor()
            col[1] *= 0.6
            col[2] *= 0.6
            self.__node.setColor(col)

        # self.__node.setRenderModeThickness(5)
        self.__node.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))

    def getNode(self):
        return self.__node

    def setHighlight(self):
        self.__highlight = True
        self.UpdateState()

    def resetHighLight(self):
        self.__highlight = False
        self.UpdateState()
