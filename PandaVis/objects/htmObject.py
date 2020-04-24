#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
)  # adds parent directory to path

from objects.layer import cLayer
from objects.input import cInput
from panda3d.core import NodePath, PandaNode


class cHTM:

    layerOffset = 0
    inputOffset = 0

    def __init__(self, baseApp, loader, name):

        self.__base = baseApp
        self.__loader = loader
        self.layers = {}
        self.inputs = {}

        self.__gfx = None
        self.__node = None
        self.name = name
        self.gfxCreationFinished = False
        self.__node = NodePath(PandaNode(name))

    def CreateLayer(self, name, nOfColumnsPerLayer, nOfCellsPerColumn):

        l = cLayer(name, nOfColumnsPerLayer, nOfCellsPerColumn)
        self.layers[name] = l

        l.CreateGfx(self.__loader)
        l.getNode().setPos(0, 0 , cHTM.layerOffset)

        l.getNode().reparentTo(self.__node)
        # self.__node = NodePath()

        cHTM.layerOffset += nOfCellsPerColumn + 40

    def CreateInput(self, name, count, rows):

        i = cInput(self.__base, name, count, rows)
        self.inputs[name] = i

        i.CreateGfx(self.__loader)
        i.getNode().setPos(-40, cHTM.inputOffset, 0)

        i.getNode().reparentTo(self.__node)

        cHTM.inputOffset += 5 + rows * 3

    def getNode(self):
        return self.__node

    def DestroyProximalSynapses(self):
        for ly in self.layers.values():
            ly.DestroyProximalSynapses()

        for inp in self.inputs.values():
                inp.resetProximalFocus()
            
    def DestroyDistalSynapses(self):
        for ly in self.layers.values():
            ly.DestroyDistalSynapses()

        for inp in self.inputs.values():
            inp.resetPresynapticFocus()
        
    def updateWireframe(self, value):
        for ly in self.layers.values():
            ly.updateWireframe(value)
        for i in self.inputs.values():
            i.updateWireframe(value)

    def CreateGfxProgressively(self):
        allFinished = True
        for ly in self.layers:
            if not self.layers[ly].gfxCreationFinished:
                self.layers[ly].CreateGfxProgressively()
                allFinished = False

        if allFinished:
            self.gfxCreationFinished = True

