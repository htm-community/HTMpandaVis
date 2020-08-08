#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from objects.minicolumn import cMinicolumn
from objects.gridCellModule import cGridCellModule
from panda3d.core import NodePath, PandaNode, TextNode
import math
import warnings


class cRegion(ABC):

    MAX_CREATED_OBJ_PER_CYCLE = 50

    def __init__(self, name, cellData, gui):

        self.name = name
        self.type = cellData.type
        self.parameters = cellData.parameters
        self.gui = gui  # to be able for regions to determine what we want to visualize


        # for creation of GFX
        self.loader = None
        self.gfxCreationFinished = False
        self._node = None
        self.text = None

        # can be overidden by derived classes
        self.SUBOBJ_DISTANCE_X = 2
        self.SUBOBJ_DISTANCE_Y = 2

        self.subObjects = []  # subObjects can be now minicolumn or cells

        # determine how many object must be in one row to achieve square like placement
        self.offset_idx = 0
        self.offset_x = 0
        self.offset_y = 0
        self.SUBOBJ_PER_ROW = 0


    def CreateGfx(self, loader):

        self._node = NodePath(
            PandaNode(self.name)
        )  # TextNode('layerText')#loader.loadModel("models/teapot")

        self.text = TextNode("Layer text node")
        self.text.setText(self.name)

        textNodePath = self._node.attachNewNode(self.text)
        textNodePath.setScale(5)

        textNodePath.setPos(0, -5, 0)

        self._node.setPos(0, 0, 0)
        self._node.setScale(1, 1, 1)

        self.loader = loader

        print("GFX created for "+self.name)


    @abstractmethod
    def getVerticalSize(self):
        pass

    # creating gfx per chunks, to avoid lagging
    def CreateGfxProgressively(self):
        createdObjs = 0
        currentlyCreatedObjs = 0
        allFinished = True

        if self.SUBOBJ_PER_ROW == 0:
            self.SUBOBJ_PER_ROW = int(math.sqrt(len(self.subObjects)))


        for o in self.subObjects:
            if not o.gfxCreated:
                o.CreateGfx(self.loader, self.offset_idx)
                self.offset_idx += 1
                o.getNode().setPos(self.offset_x * self.SUBOBJ_DISTANCE_X, self.offset_y * self.SUBOBJ_DISTANCE_Y, 0)
                self.offset_y += 1

                if self.offset_idx % self.SUBOBJ_PER_ROW == 0:
                    self.offset_y = 0
                    self.offset_x += 1
                o.getNode().reparentTo(self._node)
                o.gfxCreated = True
                currentlyCreatedObjs += 1

                if currentlyCreatedObjs >= cRegion.MAX_CREATED_OBJ_PER_CYCLE:
                    allFinished = False
                    break
            else:
                createdObjs += 1

        if allFinished:
            if not self.gfxCreationFinished:
                self.gfxCreationFinished = True
                self.text.setText(self.name)
        else:
            self.text.setText(self.name + "(creating:" + str(int(100 * createdObjs / len(self.subObjects))) + " %)")

    @abstractmethod
    def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
        pass

    def updateWireframe(self, value):
        for obj in self.subObjects:
            obj.updateWireframe(value)
            
    def getNode(self):
        return self._node

    def ShowProximalSynapses(self, column, permanences, inputNames, inputObj, thresholdConnected, showOnlyActive):
        # update columns with proximal Synapses
        self.minicolumns[
            column
        ].CreateProximalSynapses(
            inputNames,
            inputObj,
            permanences,
            thresholdConnected,
            createOnlyActive=showOnlyActive
        )

    def DestroyProximalSynapses(self):
        for obj in self.subObjects:
            obj.DestroyProximalSynapses()
    
    def DestroyDistalSynapses(self):
        for obj in self.subObjects:
            obj.DestroyDistalSynapses()
            
    def setTransparency(self,transparency):
        self.transparency = transparency
        for obj in self.subObjects:
            obj.setTransparency(transparency)

    def LODUpdateSwitch(self, lodDistance, lodDistance2):
        for obj in self.subObjects:
            if isinstance(obj, cMinicolumn) or isinstance(obj, cGridCellModule):
                obj.LODUpdateSwitch(lodDistance, lodDistance2)

    def resetPresynapticFocus(self):
        for obj in self.subObjects:
            obj.resetPresynapticFocus()
