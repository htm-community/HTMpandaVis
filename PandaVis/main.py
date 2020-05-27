# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from bakeReader.bakeReader import BakeReader
import math

import time
from objects.htmObject import cHTM
from gui import cGUI # Graphical user interface
from environment import cEnvironment # handles everything about the environment
from interaction import cInteraction # handles keys, user interaction etc..
from direct.stdpy import threading
from panda3d.core import loadPrcFileData

loadPrcFileData('', 'win-size 1600 900')

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

        self.bakeReader = BakeReader('/home/zz/Desktop/test1.db')
        self.bakeReader.setGui(self.gui)
        
        self.interaction = cInteraction(self)
        
        self.interaction.SetupKeys()
        self.interaction.SetupOnClick()
        
        self.taskMgr.add(self.update, "main loop")
        self.accept(self.win.getWindowEvent(), self.interaction.onWindowEvent)
       
        self.HTMObjects = {}
        self.allHTMobjectsCreated = False
        self.oneOfObjectsCreationFinished = False

        self.gfxCreationThread= threading.Thread(target=self.gfxCreationWorker, args=())

        #----
        self.firstTime = True
        self.dataChange = False
        self.iteration = 100

    def updateHTMstate(self):

        if self.firstTime:
            self.bakeReader.OpenDatabase()
            self.bakeReader.BuildStructure()

            self.bakeReader.LoadActiveColumns('SensoryLayer', self.iteration)
            self.bakeReader.LoadWinnerCells('SensoryLayer', self.iteration)
            self.bakeReader.LoadPredictiveCells('SensoryLayer', self.iteration)
            self.bakeReader.LoadActiveCells('SensoryLayer', self.iteration)

            self.firstTime = False
            self.dataChange = True
            return

        cellDataWasUpdated = False

        if self.dataChange or self.oneOfObjectsCreationFinished:

            printLog("Data change! Updating HTM state", verbosityMedium)

            self.gui.setIteration(self.iteration)

            obj = "HTM1"
            if obj not in self.HTMObjects:

                printLog("New HTM object arrived! Name:" + str(obj))
                # create HTM object
                newObj = cHTM(self, self.loader, obj)
                newObj.getNode().reparentTo(self.render)

                # create inputs
                for inp in self.bakeReader.inputs:
                    printLog("Creating input: " + str(inp), verbosityHigh)
                    print(self.bakeReader.inputs[inp])
                    newObj.CreateInput(
                        name=inp,
                        count=self.bakeReader.inputs[inp].size,
                        rows=int(math.sqrt(self.bakeReader.inputs[inp].size)),
                    )
                # create layers
                for lay in self.bakeReader.layers:
                    printLog("Creating layer: " + str(lay), verbosityHigh)
                    newObj.CreateLayer(
                        name=lay,
                        nOfColumnsPerLayer=int(self.bakeReader.layers[lay].spParams['sp_columnDimensions_x']),
                        nOfCellsPerColumn=1,
                    )

                self.HTMObjects[obj] = newObj

                self.gfxCreationThread.start()
                # update HTM object

            # go through all incoming inputs
            for i in self.bakeReader.inputs:  # dict
                printLog("Updating state of input: " + str(i), verbosityHigh)
                # find matching input in local structure

                self.HTMObjects[obj].inputs[i].UpdateState(
                    self.bakeReader.inputs[i].bits,
                    self.bakeReader.inputs[i].stringValue,
                )

            # go through all incoming layers
            for l in self.bakeReader.layers:  # dict
                if self.HTMObjects[obj].layers[l].gfxCreationFinished:
                    printLog("Updating state of layer: " + str(l), verbosityHigh)
                    # find matching layer in local structure
                    self.HTMObjects[obj].layers[l].UpdateState(
                        self.bakeReader.layers[l].activeColumns,
                        self.bakeReader.layers[l].activeCells,
                        self.bakeReader.layers[l].winnerCells,
                        self.bakeReader.layers[l].predictiveCells,
                        newStep = True,
                        showPredictionCorrectness=self.gui.showPredictionCorrectness,
                        showBursting = self.gui.showBursting
                    )

            self.oneOfObjectsCreationFinished = False
            cellDataWasUpdated = True

        # if self.client.proximalDataArrived:
        #     printLog("Proximal data arrived, updating synapses!", verbosityMedium)
        #
        #     serverObjs = self.client.serverData.HTMObjects
        #
        #     for obj in serverObjs:
        #
        #         self.HTMObjects[obj].DestroyProximalSynapses()
        #
        #         for l in serverObjs[obj].layers:  # dict
        #             printLog("data len:"+str(len(serverObjs[obj].layers[l].proximalSynapses)), verbosityHigh)
        #             for syn in serverObjs[obj].layers[l].proximalSynapses:  # array
        #
        #                 printLog("Layer:" + str(l), verbosityMedium)
        #                 printLog("proximalSynapses len:" + str(len(syn)), verbosityHigh)
        #
        #                 columnID = syn[0]
        #                 proximalSynapses = syn[1]
        #
        #                 # update columns with proximal Synapses
        #                 self.HTMObjects[obj].layers[l].minicolumns[
        #                     columnID
        #                 ].CreateProximalSynapses(
        #                     serverObjs[obj].layers[l].proximalInputs,
        #                     self.HTMObjects[obj].inputs,
        #                     proximalSynapses,
        #                 )
        #     self.client.proximalDataArrived = False
        #
        # if self.client.distalDataArrived:
        #     printLog("Distal data arrived, updating synapses!", verbosityMedium)
        #     serverObjs = self.client.serverData.HTMObjects
        #
        #     for obj in serverObjs:
        #
        #         self.HTMObjects[obj].DestroyDistalSynapses()
        #
        #         for l in serverObjs[obj].layers:  # dict
        #             printLog("len:"+str(len(serverObjs[obj].layers[l].distalSynapses)), verbosityHigh)
        #             for syn in serverObjs[obj].layers[l].distalSynapses:  # array
        #
        #                 printLog("Layer:" + str(l), verbosityMedium)
        #                 printLog("distalSynapses len:" + str(len(syn)), verbosityHigh)
        #
        #                 columnID = syn[0]
        #                 cellID = syn[1]
        #                 distalSynapses = syn[2]
        #
        #                 # update columns with distal Synapses
        #                 self.HTMObjects[obj].layers[l].minicolumns[
        #                     columnID
        #                 ].cells[cellID].CreateDistalSynapses(
        #                     self.HTMObjects[obj],
        #                     self.HTMObjects[obj].layers[l],
        #                     distalSynapses,
        #                     serverObjs[obj].layers[l].distalInputs
        #                 )
        #
        #     self.client.distalDataArrived = False

        if cellDataWasUpdated:
            self.interaction.UpdateProximalAndDistalData()
            self.gui.UpdateCellDescription()


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
