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


verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityHigh  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


class cCorticalColumn:
    def __init__(self, nameOfLayer, nOfCellsPerColumn):
        self.cells = []
        for i in range(nOfCellsPerColumn):
            n = cCell(self)
            self.cells.append(n)

        self.state = False
        self.parentLayer = nameOfLayer

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

        # self.__node.setTag('clickable',str(idx))#to be able to click on it

        self.__columnBox = loader.loadModel("models/cube")
        self.__columnBox.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
        self.__columnBox.setPos(
            0, 0, -0.5 + (0 if len(self.cells) == 0 else len(self.cells) / 2)
        )
        self.__columnBox.setScale(
            0.5, 0.5, 0.5 * (1 if len(self.cells) == 0 else len(self.cells))
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
            z += 1
            n.getNode().reparentTo(self.__cellsNodePath)

    def UpdateState(self, state):

        self.state = state

        # update column box color (for LOD in distance look)
        if self.state:
            self.__columnBox.setColor(1.0, 0.0, 0.0, 1.0)  # red
        else:
            self.__columnBox.setColor(1.0, 1.0, 1.0, 1.0)  # white

        for n in self.cells:
            n.state = state
            n.UpdateState()

    def getNode(self):
        return self.__node

    # -- Create proximal synapses
    # inputObjects - list of names of inputs(areas)
    # inputs - panda vis input object
    # synapses - list of the second points of synapses (first point is this cortical column)
    # NOTE: synapses are now DENSE
    def CreateProximalSynapses(self, inputObjects, inputs, synapses):

        for child in self.__cellsNodePath.getChildren():
            if child.getName() == "myLine":
                child.removeNode()

        printLog("Creating synapses", verbosityMedium)
        printLog("To inputs called:" + str(inputObjects), verbosityMedium)
        printLog("Synapses count:" + str(len(synapses)), verbosityMedium)
        printLog("active:" + str(sum([i for i in synapses])), verbosityHigh)

        # inputs are divided into separate items in list - [input1,input2,input3]
        # synapses are one united array [1,0,0,1,0,1,0...]
        # length is the same

        # synapses can be connected to one input or to several inputs
        # if to more than one - split synapses array
        if len(inputObjects) > 1:
            synapsesDiv = []
            offset = 0
            for inputObj in inputObjects:
                synapsesDiv.append(synapses[offset : offset + inputs[inputObj].count])
                offset += inputs[inputObj].count

        for i in range(len(synapsesDiv)):  # for each input object

            inputs[inputObjects[i]].resetHighlight()  # clear color highlight

            for y in range(
                len(synapsesDiv[i])
            ):  # go through every synapse and check activity
                if synapsesDiv[i][y] == 1:

                    form = GeomVertexFormat.getV3()
                    vdata = GeomVertexData("myLine", form, Geom.UHStatic)
                    vdata.setNumRows(1)
                    vertex = GeomVertexWriter(vdata, "vertex")

                    vertex.addData3f(
                        inputs[inputObjects[i]]
                        .inputBits[y]
                        .getNode()
                        .getPos(self.__node)
                    )
                    vertex.addData3f(0, 0, 0)
                    # vertex.addData3f(self.__node.getPos())
                    # printLog("Inputs:"+str(i)+"bits:"+str(y))
                    # printLog(inputs[i].inputBits[y].getNode().getPos(self.__node))

                    # highlight
                    inputs[inputObjects[i]].inputBits[
                        y
                    ].setHighlight()  # highlight connected bits

                    prim = GeomLines(Geom.UHStatic)
                    prim.addVertices(0, 1)

                    geom = Geom(vdata)
                    geom.addPrimitive(prim)

                    node = GeomNode("synapse")
                    node.addGeom(geom)

                    self.__cellsNodePath.attachNewNode(node)

    def DestroySynapses(self):
        for syn in self.__cellsNodePath.findAllMatches("synapse"):
            syn.removeNode()