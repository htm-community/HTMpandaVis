#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from objects.cell import cCell
from panda3d.core import NodePath, PandaNode, LODNode, LColor
from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Geom,
    GeomLines,
    GeomNode,
)
from Colors import *

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityHigh  # change this to change printing verbosity of this file

CELL_OFFSET = 0.3

def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


class cMinicolumn:
    def __init__(self, nameOfLayer, nOfCellsPerColumn):
        self.cells = []
        for i in range(nOfCellsPerColumn):
            n = cCell(self)
            self.cells.append(n)

        self.idx = -1
        self.parentLayer = nameOfLayer
        self.transparency = 1.0
        self.gfxCreated = False
        self.LodDistance1Stored = 100.0
        self.LodDistance2Stored = 5000.0

        self.bursting = False
        self.active = False
        self.oneOfCellPredictive = False
        self.oneOfCellCorrectlyPredicted = False
        self.oneOfCellFalselyPredicted = False

    def CreateGfx(self, loader, idx):
        #                __node
        #                /   \
        #  cellsNodePath   columnBox

        self.lod = LODNode("columnLOD")  # Level of detail node for Column
        self.__node = NodePath(
            self.lod
        )  # NodePath(PandaNode('column'))# loader.loadModel("models/box")
        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)

        self.idx = idx

        # self.__node.setTag('clickable',str(idx))#to be able to click on it

        self.__columnBox = loader.loadModel("PandaVis/models/cube")
        self.__columnBox.setPos(
            0, 0, -0.5 + (0 if len(self.cells) == 0 else len(self.cells)*(1+CELL_OFFSET) / 2)
        )
        self.__columnBox.setScale(
            0.5, 0.5, 0.5 * (1 if len(self.cells) == 0 else len(self.cells)*(1+CELL_OFFSET))
        )
        self.__columnBox.setName("columnBox")

        self.__cellsNodePath = NodePath(
            PandaNode("cellsNode")
        )  # to pack all cells into one node path
        self.__cellsNodePath.setName("column")
        self.__cellsNodePath.setTag(
            "id", str(idx)
        )  # to be able to retrieve index of column for mouse click

        self.lod.addSwitch(100.0, 0.0)
        self.lod.addSwitch(5000.0, 100.0)

        self.__cellsNodePath.reparentTo(self.__node)
        self.__columnBox.reparentTo(self.__node)

        z = 0
        idx = 0
        for n in self.cells:
            n.CreateGfx(loader, idx)
            idx += 1
            n.getNode().setPos(0, 0, z)
            z += 1+CELL_OFFSET
            n.getNode().reparentTo(self.__cellsNodePath)

        self.gfxCreated = True

    def LODUpdateSwitch(self, lodDistance, lodDistance2):
        self.lodDistance1Stored = lodDistance
        self.lodDistance2Stored = lodDistance2

        self.lod.clearSwitches()
        self.lod.addSwitch(lodDistance, 0.0)
        self.lod.addSwitch(lodDistance2, lodDistance)

    def LODUpdateSwitch_long(self):
        self.lod.clearSwitches()
        self.lod.addSwitch(self.lodDistance2Stored, 0.0)
        self.lod.addSwitch(self.lodDistance2Stored, self.lodDistance2Stored)

    def LODUpdateSwitch_normal(self):
        self.LODUpdateSwitch(self.lodDistance1Stored, self.lodDistance2Stored)

    def UpdateState(self, bursting, activeColumn, oneOfCellPredictive, oneOfCellCorrectlyPredicted, oneOfCellFalselyPredicted):

        self.bursting = bursting
        self.active = activeColumn
        self.oneOfCellPredictive = oneOfCellPredictive
        self.oneOfCellCorrectlyPredicted = oneOfCellCorrectlyPredicted
        self.oneOfCellFalselyPredicted = oneOfCellFalselyPredicted

        # update column box color (for LOD in distance look)
        if self.oneOfCellCorrectlyPredicted:
            COL_COLUMN_ONEOFCELLCORRECTLY_PREDICTED.setW(self.transparency)
            col = COL_COLUMN_ONEOFCELLCORRECTLY_PREDICTED
            self.__columnBox.setColor(col)
        elif self.oneOfCellFalselyPredicted:
            COL_COLUMN_ONEOFCELLFALSELY_PREDICTED.setW(self.transparency)
            col = COL_COLUMN_ONEOFCELLFALSELY_PREDICTED
            self.__columnBox.setColor(col)
        elif self.bursting:
            COL_COLUMN_BURSTING.setW(self.transparency)
            col = COL_COLUMN_BURSTING
            self.__columnBox.setColor(col)
        elif self.active and self.oneOfCellPredictive:
            COL_COLUMN_ACTIVE_AND_ONEOFCELLPREDICTIVE.setW(self.transparency)
            col = COL_COLUMN_ACTIVE_AND_ONEOFCELLPREDICTIVE
            self.__columnBox.setColor(col)
        elif self.oneOfCellPredictive:
            COL_COLUMN_ONEOFCELLPREDICTIVE.setW(self.transparency)
            col = COL_COLUMN_ONEOFCELLPREDICTIVE
            self.__columnBox.setColor(col)
        elif self.active:
            COL_COLUMN_ACTIVE.setW(self.transparency)
            col = COL_COLUMN_ACTIVE
            self.__columnBox.setColor(col)

        else:
            COL_COLUMN_INACTIVE.setW(self.transparency)
            col = COL_COLUMN_INACTIVE
            self.__columnBox.setColor(col)

#        for n in self.cells:
#            n.active = active
#            n.UpdateState()

    def getNode(self):
        return self.__node

    def updateWireframe(self, value):
        for cell in self.cells:
            cell.updateWireframe(value)
        if value:
            self.__columnBox.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
        else:
            self.__columnBox.setRenderModeFilled()
            
    # -- Create proximal synapses
    # inputNames - list of names of inputs(areas)
    # inputObj - panda vis input object
    # permanences - list of the second points of synapses (first point is this minicolumn)
    # NOTE: synapses are now DENSE

    def CreateProximalSynapses(self, inputNames, inputObj, permanences, thresholdConnected):

        self.DestroyProximalSynapses()

        printLog("Creating proximal permanences", verbosityMedium)
        printLog("To inputObj called:" + str(inputNames), verbosityMedium)
        printLog("permanences count:" + str(len(permanences)), verbosityMedium)
        printLog("active:" + str(sum([i for i in permanences])), verbosityHigh)

        # inputObj are divided into separate items in list - [input1,input2,input3]
        # permanences are one united array [1,0,0,1,0,1,0...]
        # length is the same

        # synapses can be connected to one input or to several inputObj
        # if to more than one - split synapses array
        synapsesDiv = []
        offset = 0
        for inputName in inputNames:
            synapsesDiv.append(permanences[offset : offset + inputObj[inputName].count])
            offset += inputObj[inputName].count

        for i in range(len(synapsesDiv)):  # for each input object

            inputObj[inputNames[i]].resetProximalFocus()  # clear color highlight

            for y in range(
                len(synapsesDiv[i])
            ):  # go through every synapse and check if its connected (we are comparing permanences)
                if synapsesDiv[i][y] >= thresholdConnected:

                    form = GeomVertexFormat.getV3()
                    vdata = GeomVertexData("ProximalSynapseLine", form, Geom.UHStatic)
                    vdata.setNumRows(1)
                    vertex = GeomVertexWriter(vdata, "vertex")

                    vertex.addData3f(
                        inputObj[inputNames[i]]
                        .inputBits[y]
                        .getNode()
                        .getPos(self.__node)
                    )
                    vertex.addData3f(0, 0, 0)
                    # vertex.addData3f(self.__node.getPos())
                    # printLog("inputObj:"+str(i)+"bits:"+str(y))
                    # printLog(inputObj[i].inputBits[y].getNode().getPos(self.__node))

                    # highlight
                    inputObj[inputNames[i]].inputBits[
                        y
                    ].setProximalFocus()  # highlight connected bits

                    prim = GeomLines(Geom.UHStatic)
                    prim.addVertices(0, 1)
                    

                    geom = Geom(vdata)
                    geom.addPrimitive(prim)

                    node = GeomNode("ProximalSynapse")
                    node.addGeom(geom)
                                       

                    nodePath = self.__cellsNodePath.attachNewNode(node)
                    
                    nodePath.setRenderModeThickness(2)
                    # color of the line
                    if inputObj[inputNames[i]].inputBits[y].active:
                        nodePath.setColor(COL_PROXIMAL_SYNAPSES_ACTIVE)
                    else:
                        nodePath.setColor(COL_PROXIMAL_SYNAPSES_INACTIVE)

    def setTransparency(self, transparency):
        self.transparency = transparency
        for cell in self.cells:
            cell.setTransparency(transparency)

        self.UpdateState(self.bursting, self.active, self.oneOfCellPredictive, self.oneOfCellCorrectlyPredicted, self.oneOfCellFalselyPredicted)

    def DestroyProximalSynapses(self):
        if not self.gfxCreated:
            return
        for syn in self.__cellsNodePath.findAllMatches("ProximalSynapse"):
            syn.removeNode()
    
    def DestroyDistalSynapses(self):
        if not self.gfxCreated:
            return
        for cell in self.cells:
            cell.DestroyDistalSynapses()

        self.resetPresynapticFocus()

    def resetPresynapticFocus(self):
        if not self.gfxCreated:
            return
        for cell in self.cells:
            cell.resetPresynapticFocus()  # also reset distal focus

    def getDescription(self):
        txt = ""
        txt += "ID:" + str(self.idx) + "\n"
        txt += "Active:" + str(self.active)+"\n"
        txt += "One of cell is predictive:" + str(self.oneOfCellPredictive) + "\n"
        txt += "One of cell correctly predicted:" + str(self.oneOfCellCorrectlyPredicted) + "\n"
        txt += "One of cell false predicted:" + str(self.oneOfCellFalselyPredicted) + "\n"
        return txt
