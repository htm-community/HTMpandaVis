#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from objects.minicolumn import cMinicolumn
from objects.gridCellModule import cGridCellModule
from panda3d.core import NodePath, PandaNode, TextNode
import math
from panda3d.core import LColor
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
        textNodePath.setColor(LColor(0.0, 0.0, 0.0, 1.0)) # black

        textNodePath.setPos(0, -5, 0)

        self._node.setPos(0, 0, 0)
        self._node.setScale(1, 1, 1)

        self.loader = loader

        if self.SUBOBJ_PER_ROW == 0:
            self.SUBOBJ_PER_ROW = int(math.sqrt(len(self.subObjects)))

        print("GFX created for "+self.name)


    @abstractmethod
    def getBoundingBoxSize(self): # return [horizontal, vertical]
        pass

    def setPosition(self, pos):
        if self.getNode() is not None: # check if region has physical objects
            self.getNode().setPos(pos[0], 0, pos[1])

    # creating gfx per chunks, to avoid lagging
    def CreateGfxProgressively(self, regions):
        createdObjs = 0
        currentlyCreatedObjs = 0
        allFinished = True


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
                if self.text is not None:
                    self.text.setText(self.name)

                    if self.type in ['TMRegion', 'py.ApicalTMPairRegion'] and self.unifiedWithSPRegion:
                        self.text.setText(self.name + ' + ' + self.unifiedSPRegion)

        else:
            if self.text is not None:
                self.text.setText(self.name + "(creating:" + str(int(100 * createdObjs / len(self.subObjects))) + " %)")

    @abstractmethod
    def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
        pass

    def updateWireframe(self, value):
        for obj in self.subObjects:
            obj.updateWireframe(value)
            
    def getNode(self):
        return self._node

    # this method shows requested synapse type on the specific column/cell of this region
    def ShowSynapses(self, regionObjects, bakeReader, synapsesType, column, cell, onlyActive):


        if synapsesType in ['proximal','distal'] : # SPRegion, TMRegion
            inputName = 'bottomUpIn'
        elif synapsesType == 'basal': # ApicalTMRegion
            inputName = 'basalInput'
        elif synapsesType == 'apical': # ApicalTMRegion
            inputName = 'apicalInput'
        else:
            raise NotImplemented("Synapses type:"+str(synapsesType)+' not implemented!')

        #TMRegion takes distal input from his own
        if synapsesType == 'distal' and self.type == 'TMRegion':
            self.minicolumns[column].cells[cell]\
                .CreateSynapses(regionObjects, bakeReader.regions[self.name].cellConnections[synapsesType], synapsesType,
                            [self.name], onlyActive)

        elif synapsesType == "proximal": # we are on minicolumns
            if hasattr(self, 'unifiedWithSPRegion') and self.unifiedWithSPRegion:
                regName = self.unifiedSPRegion
            else:
                regName = self.name

            self.minicolumns[
                column
            ].CreateSynapses(regionObjects, bakeReader.regions[regName].columnConnections[synapsesType], synapsesType, self.FindSourceRegionsOfInput(bakeReader, regName, inputName), onlyActive)

        else: # other than proximal
            if hasattr(self, "minicolumns"):
                cellObj = self.minicolumns[column].cells[cell]
            elif hasattr(self, "cells"):
                cellObj = self.cells[cell]
            elif hasattr(self, "gridCellModules"):
                cellObj = self.gridCellModules.cells[cell]
            else:
                raise NotImplemented()

            cellObj.CreateSynapses(regionObjects, bakeReader.regions[self.name].cellConnections[synapsesType], synapsesType,
                               self.FindSourceRegionsOfInput(bakeReader, self.name, inputName))

    # finds all source regions that matches this region's input
    @classmethod
    def FindSourceRegionsOfInput(cls, bakeReader, regionName, regionInput):
        result = []

        for idx, link in bakeReader.links.items():
            if link.destinationRegion == regionName and link.destinationInput == regionInput:
                result += [link.sourceRegion]

        return result


    def DestroySynapses(self, synapseType):
        for obj in self.subObjects:
            obj.DestroySynapses(synapseType)

            
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
