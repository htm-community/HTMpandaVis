#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from pandaComm.client import SocketClient
import math


from objects.htmObject import cHTM
from gui import cGUI # Graphical user interface
from environment import cEnvironment # handles everything about the environment
from interaction import cInteraction # handles keys, user interaction etc..
import threading

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityHigh
)  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


class cApp(ShowBase):
        
    def __init__(self):
        ShowBase.__init__(self)
        self.speed = 40

        # Mouse and camera movement init
        self.mouseX_last = 0
        self.mouseY_last = 0
        self.rotateCamera = False
        self.move_z = 50

        self.env = cEnvironment(self)
        
        self.env.CreateBasement()  # to not be lost if there is nothing around
        self.env.SetupLights()
        self.env.SetupCamera()
        
        width = self.win.getProperties().getXSize()
        height = self.win.getProperties().getYSize()

        self.gui = cGUI(
            width,
            height,
            self.loader,
            visApp = self
        )

        self.guiThread = threading.Thread(target = self.gui.update)
        self.guiThread.start()

        self.client = SocketClient()
        self.client.setGui(self.gui)
        
        self.interaction = cInteraction(self)
        
        self.interaction.SetupKeys()
        self.interaction.SetupOnClick()
        
        self.taskMgr.add(self.update, "main loop")
        self.accept(self.win.getWindowEvent(), self.interaction.onWindowEvent)
       
        self.HTMObjects = {}

    def updateHTMstate(self):
        if self.client.stateDataArrived:
            self.client.stateDataArrived = False
            printLog("Data change! Updating HTM state", verbosityMedium)

            serverObjs = self.client.serverData.HTMObjects

            # if we get HTM data objects, iterate over received data
            for obj in serverObjs:

                if not obj in self.HTMObjects:  # its new HTM object
                    printLog("New HTM object arrived! Name:" + str(obj))
                    # create HTM object
                    newObj = cHTM(self.loader, obj)
                    newObj.getNode().reparentTo(self.render)

                    # create inputs
                    for inp in serverObjs[obj].inputs:
                        newObj.CreateInput(
                            name=inp,
                            count=serverObjs[obj].inputs[inp].count,
                            rows=int(math.sqrt(serverObjs[obj].inputs[inp].count)),
                        )
                    # create layers
                    for lay in serverObjs[obj].layers:
                        newObj.CreateLayer(
                            name=lay,
                            nOfColumnsPerLayer=serverObjs[obj].layers[lay].columnCount,
                            nOfCellsPerColumn=serverObjs[obj]
                            .layers[lay]
                            .cellsPerColumn,
                        )

                    self.HTMObjects[obj] = newObj
                # update HTM object

                # go through all incoming inputs
                for i in serverObjs[obj].inputs:  # dict
                    # find matching input in local structure

                    self.HTMObjects[obj].inputs[i].UpdateState(
                        serverObjs[obj].inputs[i].bits,
                        serverObjs[obj].inputs[i].stringValue,
                    )

                # go through all incoming layers
                for l in serverObjs[obj].layers:  # dict
                    # find matching layer in local structure
                    self.HTMObjects[obj].layers[l].UpdateState(
                        serverObjs[obj].layers[l].activeColumns,
                        serverObjs[obj].layers[l].winnerCells,
                        serverObjs[obj].layers[l].predictiveCells
                    )

        if self.client.proximalDataArrived:
            printLog("Proximal data arrived, updating synapses!", verbosityMedium)
            self.client.proximalDataArrived = False
            serverObjs = self.client.serverData.HTMObjects

            for obj in serverObjs:

                self.HTMObjects[obj].DestroyProximalSynapses()

                for l in serverObjs[obj].layers:  # dict
                    printLog(serverObjs[obj].layers[l].proximalSynapses, verbosityHigh)
                    for syn in serverObjs[obj].layers[l].proximalSynapses:  # array

                        printLog("Layer:" + str(l), verbosityMedium)
                        printLog("proximalSynapses:" + str(syn), verbosityHigh)

                        columnID = syn[0]
                        proximalSynapses = syn[1]

                        # update columns with proximal Synapses
                        self.HTMObjects[obj].layers[l].corticalColumns[
                            columnID
                        ].CreateProximalSynapses(
                            serverObjs[obj].layers[l].proximalInputs,
                            self.HTMObjects[obj].inputs,
                            proximalSynapses,
                        )
        if self.client.distalDataArrived:
            printLog("Distal data arrived, updating synapses!", verbosityMedium)
            self.client.distalDataArrived = False
            serverObjs = self.client.serverData.HTMObjects

            for obj in serverObjs:

                self.HTMObjects[obj].DestroyDistalSynapses()

                for l in serverObjs[obj].layers:  # dict
                    printLog(serverObjs[obj].layers[l].distalSynapses, verbosityHigh)
                    for syn in serverObjs[obj].layers[l].distalSynapses:  # array

                        printLog("Layer:" + str(l), verbosityMedium)
                        printLog("distalSynapses:" + str(syn), verbosityHigh)

                        columnID = syn[0]
                        cellID = syn[1]
                        distalSynapses = syn[2]

                        # update columns with proximal Synapses
                        self.HTMObjects[obj].layers[l].corticalColumns[
                            columnID
                        ].cells[cellID].CreateDistalSynapses(
                            self.HTMObjects[obj].layers[l],
                            distalSynapses
                        )

    def update(self, task):

        self.interaction.Update()
        self.updateHTMstate()
        # update environment - e.g. controlling drawing style in runtime

        return task.cont



if __name__ == "__main__":
    app = cApp()
    app.run()
