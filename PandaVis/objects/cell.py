#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 05:46:38 2019

@author: osboxes
"""
from panda3d.core import LColor, CollisionBox, CollisionNode


class cCell:
    def __init__(self, column):
        self.active = False
        self.predictive = False
        
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
            self.__node.setColor(0.2, 0.5, 1.0, 1.0)  # light blue
        elif self.predictive and self.active:
            self.__node.setColor(0.0, 1.0, 0.0, 1.0)  # green
        elif self.predictive:
            self.__node.setColor(1.0, 0.0, 0.0, 1.0)  # red
        elif self.active:
            self.__node.setColor(1.0, 0.8, 0.8, 1.0)  # pink
        else:
            self.__node.setColor(1.0, 1.0, 1.0, 1.0)  # white

    def setFocus(self):
        self.UpdateState(self.active,self.predictive,True)# no change except focus

    def resetFocus(self):
        self.UpdateState(self.active,self.predictive,False)# no change except focus
        
    def updateWireframe(self,value):
        if value:
            self.__node.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        else:
            self.__node.setRenderModeFilled()
            
    def getNode(self):
        return self.__node
    
     # -- Create distal synapses
    # inputObjects - list of names of inputs(areas)
    # inputs - panda vis input object
    # synapses - list of the second points of synapses (first point is this cortical column)
    # NOTE: synapses are now DENSE
    def CreateDistalSynapses(self, inputObjects, inputs, synapses):

        for child in self.__cellsNodePath.getChildren():
            if child.getName() == "myLine":
                child.removeNode()

        printLog("Creating synapses", verbosityMedium)
        #printLog("To inputs called:" + str(inputObjects), verbosityMedium)
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

    def DestroyDistalSynapses(self):
        for syn in self.__cellsNodePath.findAllMatches("synapse"):
            syn.removeNode()
