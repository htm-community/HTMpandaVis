#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import warnings

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
)  # adds parent directory to path

from objects.region import cRegion
from panda3d.core import NodePath, PandaNode
from objects.ColumnPoolerRegion import cColumnPoolerRegion
from objects.ApicalTMPairRegion import cApicalTMPairRegion
from objects.RawSensorRegion import cRawSensorRegion
from objects.RawValuesRegion import cRawValuesRegion
from objects.GridCellLocationRegion import cGridCellLocationRegion

class cHTM:

    layerOffset = 0
    inputOffset = 0

    def __init__(self, baseApp, loader, name, gui):

        self.__base = baseApp
        self.__loader = loader
        self.regions = {}
        self.gui = gui

        self.__gfx = None
        self.__node = None
        self.name = name
        self.gfxCreationFinished = False
        self.__node = NodePath(PandaNode(name))

    @classmethod
    def getClassByType(cls, type):
        if type == 'py.ColumnPoolerRegion':
            return cColumnPoolerRegion
        elif type == 'py.ApicalTMPairRegion':
            return cApicalTMPairRegion
        elif type == 'py.GridCellLocationRegion':
            return cGridCellLocationRegion
        elif type == 'py.RawValues':
            return cRawValuesRegion
        elif type == 'py.RawSensor':
            return cRawSensorRegion

        else:
            warnings.warn(type + ' region is not implemented!', UserWarning)
            return None

    def CreateRegion(self, name, regionData):

        regionClass = cHTM.getClassByType(regionData.type)
        if regionClass is None:
            return  # not implemented
        self.regions[name] = regionClass(name, regionData, self.gui)
        region = self.regions[name]

        region.CreateGfx(self.__loader)
        region.getNode().setPos(0, 0, cHTM.layerOffset)

        region.getNode().reparentTo(self.__node)
        # self.__node = NodePath()

        cHTM.layerOffset += region.getVerticalSize() + 40


    def getNode(self):
        return self.__node

    def DestroyProximalSynapses(self):
        for ly in self.regions.values():
            ly.DestroyProximalSynapses()

    def DestroyDistalSynapses(self):
        for ly in self.regions.values():
            ly.DestroyDistalSynapses()

    def updateWireframe(self, value):
        for reg in self.regions.values():
            reg.updateWireframe(value)

    def CreateGfxProgressively(self):
        allFinished = True
        for reg in self.regions:
            if not self.regions[reg].gfxCreationFinished:
                self.regions[reg].CreateGfxProgressively()
                allFinished = False

        if allFinished:
            self.gfxCreationFinished = True

