#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
import os
from panda3d.core import LColor, CollisionBox, CollisionNode
from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Geom,
    GeomLines,
    GeomNode,
)
import objects.ConnectionFactory as ConnectionFactory
from Colors import *

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityHigh  # change this to change printing verbosity of this file

def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)
        
class cCell:
    def __init__(self, column):

        self.gfxCreated = False
        self.active = False
        self.predictive = False
        self.winner = False
        self.presynapticFocus = False
        self.focused = False
        self.correctlyPredicted = False
        self.falselyPredicted = False
        self.transparency = 1.0
        self.column = column  # to be able to track column that this cell belongs to
        self.idx = -1
        self.showPredictionCorrectness = False


    def CreateGfx(
        self, loader, idx
    ):  # idx is neccesary to be able to track it down for mouse picking

        self.idx = idx
        self._node = loader.loadModel(os.path.join(os.getcwd(),"models/cube"))
        self._node.setPos(0, 0, 0)
        self._node.setScale(0.5, 0.5, 0.5)
        self._node.setTag("clickable", str(idx))  # to be able to click on it
        self._node.setName("cell")

        # COLLISION
        collBox = CollisionBox(self._node.getPos(), 1.0, 1.0, 1.0)
        cnodePath = self._node.attachNewNode(CollisionNode("cnode"))
        cnodePath.node().addSolid(collBox)

        self.UpdateState(False, False, False)

    def UpdateState(self, active, predictive, winner, focused=False, presynapticFocus=False, showPredictionCorrectness = False, prev_predictive = False):

        # determine if previous prediction was correct or not

        if showPredictionCorrectness:#was predicted last step
            if prev_predictive and active:#was predictive and now is active
                self.correctlyPredicted = True
                self.falselyPredicted = False
            elif prev_predictive and not active:
                self.correctlyPredicted = False
                self.falselyPredicted = True
            else:#wasn't predictive previous step, so can't be correct or false
                self.correctlyPredicted = False
                self.falselyPredicted = False
        else: # we don't want to see correctness
            self.correctlyPredicted = False
            self.falselyPredicted = False
            self.showPredictionCorrectness = showPredictionCorrectness # store it for purposes of description

        self.active = active
        self.predictive = predictive
        self.winner = winner
        self.focused = focused

        if self.focused and self.column is not None:# if we have this cell focused, modify LOD to long distance
            self.column.LODUpdateSwitch_long()

        self.presynapticFocus = presynapticFocus
        
        if self.focused:
            self._node.setColor(COL_CELL_FOCUSED)
        elif self.correctlyPredicted:
            col = COL_CELL_CORRECTLY_PREDICTED
            self._node.setColor(col)
        elif self.falselyPredicted:
            col = COL_CELL_FALSELY_PREDICTED
            self._node.setColor(col)
        elif self.winner:
            col = COL_CELL_WINNER
            self._node.setColor(col)
        elif self.predictive and self.active:
            col = COL_CELL_ACTIVE_AND_PREDICTIVE
            self._node.setColor(col)
        elif self.predictive:
            col = COL_CELL_PREDICTIVE
            self._node.setColor(col)
        elif self.active:
            col = COL_CELL_ACTIVE
            self._node.setColor(col)
        elif self.presynapticFocus:
            col = COL_CELL_PRESYNAPTIC_FOCUS
            self._node.setColor(col)
        else:
            COL_CELL_INACTIVE.setW(self.transparency)
            col = COL_CELL_INACTIVE
            self._node.setColor(col)

    def setFocus(self):
        self.UpdateState(self.active, self.predictive, self.winner, True)  #no change except focus

    def resetFocus(self):
        self.UpdateState(self.active, self.predictive, self.winner, False)  #reset focus
        if self.column is not None:
            self.column.LODUpdateSwitch_normal()

    def setPresynapticFocus(self):
        self.UpdateState(self.active, self.predictive, self.winner, self.focused, True)  # no change except presynaptic focus

    def resetPresynapticFocus(self):
        self.UpdateState(self.active, self.predictive, self.winner, self.focused, False)  # reset presynaptic focus

    def setTransparency(self, transparency):
        self.transparency = transparency

        self.UpdateState(self.active, self.predictive, self.winner, self.focused, self.presynapticFocus)
        
    def updateWireframe(self, value):
        if value:
            self._node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        else:
            self._node.setRenderModeFilled()
            
    def getNode(self):
        return self._node

    def CreateSynapses(self, regionObjects, cellConnections, sourceRegion):
        printLog("Creating synapses", verbosityMedium)

        if self.column is not None:
            myID = self.column.idx * self.column.nOfCellsPerColumn + self.idx
        else:
            myID = self.idx

        ConnectionFactory.CreateSynapses(callbackCreateSynapse=self._CreateOneSynapse, regionObjects=regionObjects,
                                         cellConnections=cellConnections, sourceRegion = sourceRegion, idx = myID )

    # creates synapse, that will go from presynCell to this cell
    # presynCell - cell object
    def _CreateOneSynapse(self, presynCell):

        presynCell.setPresynapticFocus()  # highlight presynaptic cells

        form = GeomVertexFormat.getV3()
        vdata = GeomVertexData("SynapseLine", form, Geom.UHStatic)
        vdata.setNumRows(1)
        vertex = GeomVertexWriter(vdata, "vertex")

        vertex.addData3f(
            presynCell
                .getNode()
                .getPos(self._node)
        )
        vertex.addData3f(0, 0, 0)

        prim = GeomLines(Geom.UHStatic)
        prim.addVertices(0, 1)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode("Synapse")
        node.addGeom(geom)

        nodePath = self._node.attachNewNode(node)

        nodePath.setRenderModeThickness(2)

        # color of the line
        if presynCell.active:
            nodePath.setColor(COL_DISTAL_SYNAPSES_ACTIVE)
        else:
            nodePath.setColor(COL_DISTAL_SYNAPSES_INACTIVE)


    def getDescription(self):
        txt = ""
        if self.column is not None:# for regions with columns
            txt += "ID:" + str(self.idx) + "  ABS ID:"+ str(len(self.column.cells)*self.column.idx + self.idx) +"\n"
        else:
            txt += "ID:" + str(self.idx) + "\n"
        txt += "Active:" + str(self.active)+"\n"
        txt += "Winner:" + str(self.winner) + "\n"
        txt += "Predictive:" + str(self.predictive)+"\n"
        txt += "Correctly predicted:" + ('N/A' if not self.showPredictionCorrectness else str(self.correctlyPredicted))+"\n"
        txt += "Falsely predicted:" + ('N/A' if not self.showPredictionCorrectness else str(self.falselyPredicted))+"\n"

        return txt

    def DestroySynapses(self):
        for syn in self._node.findAllMatches("Synapse"):
            syn.removeNode()
