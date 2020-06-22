# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from bakeReader.bakeReader import BakeReader
import math
import os
import time

from objects.htmObject import cHTM
from gui import cGUI # Graphical user interface
from environment import cEnvironment # handles everything about the environment
from interaction import cInteraction # handles keys, user interaction etc..
from direct.stdpy import threading
from panda3d.core import loadPrcFileData, GraphicsWindow

loadPrcFileData('', 'win-size 1600 900')

#import faulthandler; faulthandler.enable()

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityHigh
)  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


class cExplorer3D(ShowBase):
        
    def __init__(self, databaseFilePath):
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

        self.databaseFilePath = databaseFilePath

        self.bakeReader = BakeReader(self.databaseFilePath)
        
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
        self.iterationDataUpdate = False

        self.BuildStructure()

        # hand over this value to the gui to be able to validate user inputs
        # -1 because predictive cells are + 1
        self.gui.cntIterations = self.bakeReader.cntIterations-1

        self.iteration = 0
        self.initIterationLoaded = False

        self.autoRunIteration = 0

    def BuildStructure(self):

        self.bakeReader.OpenDatabase()
        self.bakeReader.BuildStructure()

        obj = "HTM1"
        if obj not in self.HTMObjects:

            printLog("HTM object creation! Name:" + str(obj))
            # create HTM object
            newObj = cHTM(self, self.loader, obj)
            newObj.getNode().reparentTo(self.render)

            # create inputs
            for inp in self.bakeReader.inputs:
                printLog("Creating input: " + str(inp), verbosityHigh)

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
                    nOfColumnsPerLayer=int(self.bakeReader.layers[lay].params['sp_columnCount']),
                    nOfCellsPerColumn=int(self.bakeReader.layers[lay].params['tm_cellsPerColumn']),
                )

            self.HTMObjects[obj] = newObj

            self.gfxCreationThread.start()


    def LoadIteration(self, iteration):
        self.iteration = iteration

        for obj in self.HTMObjects:
            for inp in self.HTMObjects[obj].inputs:
                self.bakeReader.LoadInput(inp, iteration)

            for ly in self.HTMObjects[obj].layers:
                self.bakeReader.LoadActiveColumns(ly, iteration)
                self.bakeReader.LoadWinnerCells(ly, iteration)
                self.bakeReader.LoadPredictiveCells(ly, iteration+1)#take predictions for t+1
                if self.gui.showPredictionCorrectness:
                    self.bakeReader.LoadPredictiveCells(ly, iteration, loadPrevious=True)#take also predictions for t to be able to calculate correctness
                self.bakeReader.LoadActiveCells(ly, iteration)

                self.bakeReader.LoadProximalSynapses(ly,[self.gui.columnID,], iteration)
                #can't load distal synapses here, because they are a big size
                # loading just for one cell per - user click


        self.updateHTMstate() # update state of the HTM objects and connections


    def updateHTMstate(self):
        printLog("Data change! Updating HTM state", verbosityMedium)

        self.gui.setIteration(self.iteration)
        obj = "HTM1"
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
                    self.bakeReader.layers[l].prev_predictiveCells,
                    showPredictionCorrectness=self.gui.showPredictionCorrectness,
                    showBursting = self.gui.showBursting
                )

        self.oneOfObjectsCreationFinished = False

        self.UpdateProximalAndDistalData()
        self.gui.UpdateCellDescription()

    def UpdateProximalAndDistalData(self):
        if self.gui.focusedCell is None:
            return
        # -------- proximal and distal synapses -----------------------
        if self.gui.showProximalSynapses:
            self.ShowProximalSynapses(self.gui.focusedPath[0],self.gui.focusedPath[1],self.gui.columnID, self.gui.showOnlyActiveProximalSynapses)

        if self.gui.showDistalSynapses:
            self.ShowDistalSynapses(self.gui.focusedPath[0], self.gui.focusedPath[1], self.gui.columnID, self.gui.cellID)

        # if self.gui.showProximalSynapses and self.gui.focusedCell is not None:
        #     self.client.reqProximalData()
        # else:
        #     for obj in self.base.HTMObjects.values():
        #         obj.DestroyProximalSynapses()
        #
        # #do not request distal data if we don't want to show them or if this layer doesn't have TM
        # if self.gui.showDistalSynapses and self.gui.focusedCell is not None:
        #     self.client.reqDistalData()
        # else:
        #     for obj in self.base.HTMObjects.values():  # destroy synapses if they not to be shown
        #         obj.DestroyDistalSynapses()
        # -----------------------------------------------------------

    def ShowProximalSynapses(self, obj, layerName, column, showOnlyActive):# reads the synapses from the database and show them

        layer = self.bakeReader.layers[layerName]
        self.bakeReader.LoadProximalSynapses(layerName, [column], self.iteration) # load it

        if column not in layer.proximalSynapses:
            printLog("Don't have proximal data for requested column:"+str(column) + " of layer:"+str(layerName))
            self.HTMObjects[obj].layers[layerName].DestroyProximalSynapses()
            return
        self.HTMObjects[obj].layers[layerName].ShowProximalSynapses(column, layer.proximalSynapses[column],
                                                                       layer.proximalInputs,#names of inputs
                                                                        self.HTMObjects[obj].inputs,
                                                                        layer.params['sp_synPermConnected'],
                                                                        showOnlyActive)
    def ShowDistalSynapses(self, obj, layerName, column, cell):

        layer = self.bakeReader.layers[layerName]

        gotSomeData = self.bakeReader.LoadDistalSynapses(layerName, column, cell, self.iteration)  # load it

        if not gotSomeData:
            printLog("Don't have any distal synapses to show for this cell.")
            self.HTMObjects[obj].layers[layerName].minicolumns[
                column
            ].cells[cell].DestroyDistalSynapses()
            return

        self.HTMObjects[obj].layers[layerName].minicolumns[
            column
        ].cells[cell].CreateDistalSynapses(
            self.HTMObjects[obj],
            self.HTMObjects[obj].layers[layerName],
            layer.distalSynapses[cell],
            layer.distalInputs
        )


    def update(self, task):

        self.gui.update()
        self.interaction.Update()

        if self.allHTMobjectsCreated and not self.initIterationLoaded:  # wait till the objects are created, then load iteration 0
            self.LoadIteration(0)
            self.initIterationLoaded = True

        if self.gui.gotoReq >= 0:
            self.LoadIteration(self.gui.gotoReq)
            self.gui.gotoReq = -1


        if self.gui.capture:
            self.LoadIteration(self.autoRunIteration)
            self.autoRunIteration += 1
            if self.autoRunIteration > 997:
                self.gui.capture =False
                os.system("ffmpeg -y -framerate 10 -i screenshots/%01d.jpg -codec copy screenshots/recording.mkv")
            self.win.saveScreenshot('screenshots/'+str(self.autoRunIteration)+'.jpg')


        return task.cont

    def gfxCreationWorker(self):

        time.sleep(5) # need to delay this, there was SIGSEG faults, probably during creation of objects thread collision happens
        printLog("Starting GFX worker thread")
        while True:
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

