#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 11:37:36 2019

@author: zz
"""
import os
from panda3d.core import LColor, CollisionNode, CollisionBox
from Colors import *
# import random


class cInputBit:
    def __init__(self, parentObj):
        self.__parentObj = parentObj
        self.active = False  # False if random.randint(0,1)==0 else True
        self.focused = False
        self.__node = None
        self.__proximalFocus = False
        self.__distalFocus = False
        self.__prevActive = False

    def CreateGfx(self, loader, idx):

        self.__node = loader.loadModel(os.path.join(os.getcwd(),"models/cube"))
        #self.__node.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(0.5, 0.5, 0.5)

        self.__node.setTag("clickable", str(idx))  # to be able to click on it
        self.__node.setName("inputBit")

        # COLLISION
        collBox = CollisionBox(self.__node.getPos(), 1.0, 1.0, 1.0)
        cnodePath = self.__node.attachNewNode(CollisionNode("cnode"))
        cnodePath.node().addSolid(collBox)

        self.UpdateState()


    def UpdateState(self, focused=False , proximalFocus=False, distalFocus=False):
        self.focused = focused
        self.__proximalFocus = proximalFocus
        self.__distalFocus = distalFocus

        if self.__parentObj.base.gui.showInputOverlapWithPrevStep:# special overlap colors
            if self.__prevActive and self.active:
                self.__node.setColor(IN_BIT_OVERLAPPING)
            elif self.active:
                self.__node.setColor(IN_BIT_ACTIVE)
            else:
                self.__node.setColor(IN_BIT_INACTIVE)
        else:
            if self.focused:
                self.__node.setColor(IN_BIT_FOCUSED)
            elif self.active:
                self.__node.setColor(IN_BIT_ACTIVE)
            elif self.__distalFocus:
                self.__node.setColor(IN_BIT_DISTAL_FOCUS)
            elif self.__proximalFocus:
                self.__node.setColor(IN_BIT_PROXIMAL_FOCUS)
            else:
                self.__node.setColor(IN_BIT_INACTIVE)

        self.__prevActive = self.active
        # self.__node.setRenderModeThickness(5)
        #self.__node.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))

    def getNode(self):
        return self.__node

    def setProximalFocus(self):
        self.UpdateState(self.focused, True, self.__distalFocus)  # no change except proximal focus

    def resetProximalFocus(self):
        self.UpdateState(self.focused, False, self.__distalFocus)  # reset proximal focus

    def setPresynapticFocus(self):#needs to have same name as for cells for polymorphysm
        self.UpdateState(self.focused,  self.__proximalFocus, True)  # no change except distal focus

    def resetPresynapticFocus(self):#needs to have same name as for cells for polymorphysm
        self.UpdateState(self.focused,  self.__proximalFocus, False)  # reset distal focus

    def updateWireframe(self, value):
        if value:
            self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        else:
            self.__node.setRenderModeFilled()
            
    def getDescription(self):
        txt = ""
        txt += "Active:" + str(self.active)+"\n"

        return txt
