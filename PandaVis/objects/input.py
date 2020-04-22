#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from panda3d.core import NodePath, PandaNode, TextNode
from objects.inputBit import cInputBit

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityHigh
)  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


class cInput:
    def __init__(self, baseApp, name, count, rows):

        self.base = baseApp
        self.name = name
        self.count = count
        self.rows = rows

        self.inputBits = []
        for i in range(count):
            c = cInputBit(self)
            self.inputBits.append(c)

    def CreateGfx(self, loader):

        self.__node = NodePath(
            PandaNode("Input")
        )  # TextNode('layerText')#loader.loadModel("models/teapot")

        text = TextNode("name text")
        text.setText(self.name)

        textNodePath = self.__node.attachNewNode(text)
        textNodePath.setScale(2)
        textNodePath.setPos(0, -5, 0)

        # value string that represents what is encoded into SDR
        textVal = TextNode("value text")
        textVal.setText("no value")

        self.__textValNodePath = self.__node.attachNewNode(textVal)
        self.__textValNodePath.setScale(2)
        self.__textValNodePath.setPos(
            0, -5 + (self.rows * 3) / 2, 3 * self.count / self.rows
        )
        self.__textValNodePath.setHpr(90, 0, 0)

        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)

        y = 0
        z = 0
        cursor = 0
        idx = 0
        for c in self.inputBits:
            c.CreateGfx(loader, idx)
            c.getNode().setPos(0, y, z)
            y += 3

            idx += 1
            cursor += 1
            if cursor >= self.rows:
                cursor = 0
                z += 3
                y = 0

            c.getNode().reparentTo(self.__node)

        return

    def UpdateState(self, data, text):

        #    if len(data)!=self.count:
        #      print("Given data for input does not match number of bits in input!")
        #      print("A:"+str(self.count)+" B:"+str(len(data)))
        #      return
        printLog("In UpdateState(): " + str(self.name), verbosityHigh)

        self.__textValNodePath.getNode(0).setText(text)

        for i in range(len(self.inputBits)):
            self.inputBits[i].active = False

        for i in data:  # data contains indicies of what bits are "ON"
            self.inputBits[i].active = True

        for i in range(len(self.inputBits)):  # update all states
            self.inputBits[i].UpdateState()

        printLog("Leaving UpdateState()")

    def getNode(self):
        return self.__node

    def resetProximalFocus(self):
        for i in self.inputBits:
            i.resetProximalFocus()
    
    def updateWireframe(self, value):
        
        for i in self.inputBits:
            i.updateWireframe(value)

    def setPresynapticFocus(self):
        #TODO
        return

    def resetPresynapticFocus(self):
        #TODO
        return