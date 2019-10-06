#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
from panda3d.core import LColor, CollisionBox, CollisionNode
from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Geom,
    GeomLines,
    GeomNode,
)
import random
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
        self.active = False
        self.predictive = False
        self.transparency = 1.0
        self.column = column  # to be able to track column that this cell belongs to

    def CreateGfx(
        self, loader, idx
    ):  # idx is neccesary to be able to track it down for mouse picking

        self.__node = loader.loadModel("models/cube")
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
            self.__node.setColor(COL_CELL_FOCUSED)
        elif self.predictive and self.active:
            COL_CELL_CORRECTLY_PREDICTED.setW(self.transparency)
            col = COL_CELL_CORRECTLY_PREDICTED
            self.__node.setColor(col)
        elif self.predictive:
            COL_CELL_PREDICTIVE.setW(self.transparency)
            col = COL_CELL_PREDICTIVE
            self.__node.setColor(col)
        elif self.active:
            COL_CELL_ACTIVE.setW(self.transparency)
            col = COL_CELL_ACTIVE
            self.__node.setColor(col)
        else:
            COL_CELL_DEFAULT.setW(self.transparency)
            col = COL_CELL_DEFAULT
            self.__node.setColor(col)

    def setFocus(self):
        self.UpdateState(self.active,self.predictive,True)# no change except focus

    def resetFocus(self):
        self.UpdateState(self.active,self.predictive,False)# no change except focus
    
    def setTransparency(self,transparency):
        self.transparency = transparency
        
    def updateWireframe(self,value):
        if value:
            self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        else:
            self.__node.setRenderModeFilled()
            
    def getNode(self):
        return self.__node
    
    def CreateDistalSynapses(self, layer, data):

        for child in self.__node.getChildren():
            if child.getName() == "DistalSynapseLine":
                child.removeNode()

        printLog("Creating distal synapses", verbosityMedium)
       
        
        for segment in data:
            
            lineColor = LColor(random.random(),random.random(),random.random(),1.0)
            
            for presynCellID in segment:
                
                cellID = presynCellID % layer.nOfCellsPerColumn
                colID = (int)(presynCellID / layer.nOfCellsPerColumn)
                
                
                presynCell = layer.corticalColumns[colID].cells[cellID]
        
        
                form = GeomVertexFormat.getV3()
                vdata = GeomVertexData("DistalSynapseLine", form, Geom.UHStatic)
                vdata.setNumRows(1)
                vertex = GeomVertexWriter(vdata, "vertex")

                vertex.addData3f(
                    presynCell
                    .getNode()
                    .getPos(self.__node)
                )
                vertex.addData3f(0, 0, 0)
               

                prim = GeomLines(Geom.UHStatic)
                prim.addVertices(0, 1)

                geom = Geom(vdata)
                geom.addPrimitive(prim)

                node = GeomNode("DistalSynapse")
                node.addGeom(geom)
                
                nodePath = self.__node.attachNewNode(node)
                
                nodePath.setRenderModeThickness(2)
                nodePath.setColor(lineColor)# color of the line
                

    def DestroyDistalSynapses(self):
        for syn in self.__node.findAllMatches("DistalSynapse"):
            syn.removeNode()
