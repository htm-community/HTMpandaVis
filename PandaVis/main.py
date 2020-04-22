# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from pandaComm.client import SocketClient
import math

import time
from objects.htmObject import cHTM
from gui import cGUI # Graphical user interface
from environment import cEnvironment # handles everything about the environment
from interaction import cInteraction # handles keys, user interaction etc..
from direct.stdpy import threading

import faulthandler; faulthandler.enable()


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

        self.client = SocketClient()
        self.client.setGui(self.gui)
        
        self.interaction = cInteraction(self)
        
        self.interaction.SetupKeys()
        self.interaction.SetupOnClick()
        
        self.taskMgr.add(self.update, "main loop")
        self.accept(self.win.getWindowEvent(), self.interaction.onWindowEvent)
       
        self.HTMObjects = {}
        self.allHTMobjectsCreated = False
        self.oneOfObjectsCreationFinished = False

        self.gfxCreationThread= threading.Thread(target=self.gfxCreationWorker, args=())


    def updateHTMstate(self):
        if self.client.stateDataArrived or self.oneOfObjectsCreationFinished:
            self.client.stateDataArrived = False
            self.oneOfObjectsCreationFinished = False
            printLog("Data change! Updating HTM state", verbosityMedium)

            self.gui.setIteration(self.client.serverData.iterationNo)
            serverObjs = self.client.serverData.HTMObjects

            # if we get HTM data objects, iterate over received data
            for obj in serverObjs:

                if not obj in self.HTMObjects:  # its new HTM object
                    printLog("New HTM object arrived! Name:" + str(obj))
                    # create HTM object
                    newObj = cHTM(self, self.loader, obj)
                    newObj.getNode().reparentTo(self.render)

                    # create inputs
                    for inp in serverObjs[obj].inputs:
                        printLog("Creating input: " + str(inp), verbosityHigh)
                        newObj.CreateInput(
                            name=inp,
                            count=serverObjs[obj].inputs[inp].count,
                            rows=int(math.sqrt(serverObjs[obj].inputs[inp].count)),
                        )
                    # create layers
                    for lay in serverObjs[obj].layers:
                        printLog("Creating layer: " + str(lay), verbosityHigh)
                        newObj.CreateLayer(
                            name=lay,
                            nOfColumnsPerLayer=serverObjs[obj].layers[lay].columnCount,
                            nOfCellsPerColumn=serverObjs[obj]
                            .layers[lay]
                            .cellsPerColumn,
                        )

                    self.HTMObjects[obj] = newObj

                    self.gfxCreationThread.start()
                # update HTM object

                # go through all incoming inputs
                for i in serverObjs[obj].inputs:  # dict
                    printLog("Updating state of input: " + str(i), verbosityHigh)
                    # find matching input in local structure

                    self.HTMObjects[obj].inputs[i].UpdateState(
                        serverObjs[obj].inputs[i].bits,
                        serverObjs[obj].inputs[i].stringValue,
                    )

                # go through all incoming layers
                for l in serverObjs[obj].layers:  # dict
                    if self.HTMObjects[obj].layers[l].gfxCreationFinished:
                        printLog("Updating state of layer: " + str(l), verbosityHigh)
                        # find matching layer in local structure
                        self.HTMObjects[obj].layers[l].UpdateState(
                            serverObjs[obj].layers[l].activeColumns,
                            serverObjs[obj].layers[l].activeCells,
                            serverObjs[obj].layers[l].winnerCells,
                            serverObjs[obj].layers[l].predictiveCells,
                            newStep = True,
                            showPredictionCorrectness=self.gui.showPredictionCorrectness
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
                        self.HTMObjects[obj].layers[l].minicolumns[
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
                        self.HTMObjects[obj].layers[l].minicolumns[
                            columnID
                        ].cells[cellID].CreateDistalSynapses(
                            self.HTMObjects[obj],
                            self.HTMObjects[obj].layers[l],
                            distalSynapses,
                            serverObjs[obj].layers[l].distalInputs
                        )


    def update(self, task):

        self.gui.update()
        self.interaction.Update()
        self.updateHTMstate()

        return task.cont

    def gfxCreationWorker(self):

        time.sleep(5) # need to delay this, there was SIGSEG faults, probably during creation of objects thread collision happens
        printLog("Starting GFX worker thread")
        while(True):
            # finishing HTM objects creation on the run
            if not self.allHTMobjectsCreated:
                allFinished = True
                for obj in self.HTMObjects:
                    if not self.HTMObjects[obj].gfxCreationFinished:
                        allFinished = False
                        self.HTMObjects[obj].CreateGfxProgressively()

                        if self.HTMObjects[obj].gfxCreationFinished:  # it just finished GFX creation
                            self.oneOfObjectsCreationFinished = True
                if allFinished:
                    self.allHTMobjectsCreated = True
                    printLog("GFX worker: all objects finished")
                    break
            if self.gui.terminating:
                break
        printLog("GFX worker: quit")

if __name__ == "__main__":
    app = cApp()
    app.run()
