# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from bakeReader.bakeReader import BakeReader
import math
import os
import time
import sys
import json

from objects.htmObject import cHTM
from gui import cGUI # Graphical user interface
from environment import cEnvironment # handles everything about the environment
from interaction import cInteraction # handles keys, user interaction etc..
from direct.stdpy import threading
from panda3d.core import loadPrcFileData, GraphicsWindow

loadPrcFileData('', 'win-size 1600 900')


import faulthandler; faulthandler.enable() # detailed debug for SIGFAULTS for example

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
        self.move_z = 0

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
        self.env.SetCameraLoc(self.gui.cameraStartLoc)

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

        self.taskMgr.add(self.gfxCreationWorker, "gfxCreation")
        #self.gfxCreationThread = threading.Thread(target=self.gfxCreationWorker, args=())

        #----
        self.iterationDataUpdate = False

        self.BuildStructure()

        # hand over this value to the gui to be able to validate user inputs
        # -1 because predictive cells are + 1
        self.gui.cntIterations = self.bakeReader.cntIterations-1

        self.iteration = 0
        self.initIterationLoaded = False
        self.tmrRun = 0
        self.autoRunIteration = 0

    def BuildStructure(self):

        self.bakeReader.OpenDatabase()
        self.bakeReader.BuildStructure()

        obj = "HTM1"
        if obj not in self.HTMObjects:

            printLog("HTM object creation! Name:" + str(obj))
            # create HTM object
            newObj = cHTM(self, self.loader, obj, self.gui)
            newObj.getNode().reparentTo(self.render)

            # create regions
            for reg in self.bakeReader.regions:

                if self.CheckForUnification(reg) is not None: # check if there is region for unification
                    printLog("Creating unificated region: " + str(reg), verbosityHigh)
                    newObj.CreateUnificatedRegion(
                        name=reg,
                        regionData=self.bakeReader.regions[reg]
                    )
                else:
                    printLog("Creating region: " + str(reg), verbosityHigh)
                    newObj.CreateRegion(
                        name=reg,
                        regionData = self.bakeReader.regions[reg]
                    )

            self.HTMObjects[obj] = newObj

            # need to do it here due to unknown order creation
            for reg in self.HTMObjects[obj].regions:
                uniReg = self.CheckForUnification(reg)
                if uniReg is not None:
                    self.HTMObjects[obj].regions[reg].SetUnifiedTMRegion(uniReg) # link SP->TM
                    self.HTMObjects[obj].regions[uniReg].SetUnifiedSPRegion(reg) # link TM -> SP

            # assign position of regions in 3D space

            # load positionOverride
            override = None
            try:
                with open('regionPositionOverride.ini', 'r') as file:
                    override = json.loads(file.read())
            except:
                print("Error while loading position override file!")

            xShift = 0
            yShift = 0
            layerHeight = 0
            if override is not None:
                for layer in override:
                    for reg in override[layer]:
                        if reg in self.HTMObjects[obj].regions.keys():
                            region = self.HTMObjects[obj].regions[reg]
                            region.setPosition([xShift, yShift])
                            x, y = region.getBoundingBoxSize()
                            xShift += x
                            layerHeight = max(layerHeight, y)
                    yShift += layerHeight + 20 # layer completed
                    layerHeight = 0
                    xShift = 0



            #self.gfxCreationThread.start()


    # checks if the "reg" SPregion is unified with TMregion, returning name of TMRegion
    def CheckForUnification(self, reg):
        if self.bakeReader.regions[reg].type in ['SPRegion']:# applies only for SPRegion now
            # check if SP is connected to TM or TM like region, with minicolumns

            for link in self.bakeReader.links.values():# SP region is source and his out is bottomUpOut
                if link.sourceRegion == reg and link.sourceOutput == 'bottomUpOut' and\
                    self.bakeReader.regions[link.destinationRegion].type in ['TMRegion', 'ApicalTMPairRegion']:
                    return link.destinationRegion

        return None


    def LoadIteration(self, iteration):
        self.iteration = iteration

        for obj in self.HTMObjects:

            for reg in self.HTMObjects[obj].regions:
                self.bakeReader.LoadAllRegionData(reg, iteration)

                # we need to store also predictive cells for t+1
                self.bakeReader.LoadRegionData(reg, iteration+1, "predictedCells", "next_predictedCells")

                #self.bakeReader.LoadProximalSynapses(reg,[self.gui.columnID,], iteration)
                # can't load distal synapses here, because they are a big size
                # loading just for one cell per - user click


        self.updateHTMstate() # update state of the HTM objects and connections


    def updateHTMstate(self):
        printLog("Data change! Updating HTM state", verbosityMedium)

        self.gui.setIteration(self.iteration)
        obj = "HTM1"  # hardcoded for now

        # go through all regions
        for reg in self.bakeReader.regions:  # dict
            if reg in self.HTMObjects[obj].regions and self.HTMObjects[obj].regions[reg].gfxCreationFinished:
                printLog("Updating state of region: " + str(reg), verbosityHigh)

                self.HTMObjects[obj].regions[reg].UpdateState(self.bakeReader.regions[reg])

        self.oneOfObjectsCreationFinished = False

        self.UpdateConnections()
        self.gui.UpdateCellDescription()

    # this updates focused cell / column connections
    def UpdateConnections(self):
        if self.gui.focusedCell is None:
            return

        obj = self.gui.focusedPath[0]
        regionName = self.gui.focusedPath[1]
        column = self.gui.columnID
        cell = self.gui.cellID

        region = self.HTMObjects[obj].regions[regionName]
        regionData = self.bakeReader.regions[regionName]

        # cleans all data, do not call if you want to stack data for more cells/columns for example
        self.bakeReader.CleanCellConnections(regionName)
        self.bakeReader.CleanColumnConnections(regionName)



        # ---------------------------- Column connections SYNAPSES ---------------------------------------------------------------
        for connType, typeFiles in region.connections.items(): # iterate over conn types
            for typeFile in typeFiles: # iterate over connection file types (can be multiple per connectionType)
                self.UpdateColumnConnections(regionName, region, column, obj, connectionType=connType, connectionTypeFile=typeFile)


        # ---------------------------- Cell connections SYNAPSES -----------------------------------------------------------

        for connType, typeFiles in region.connections.items(): # iterate over conn types
            for typeFile in typeFiles: # iterate over connection file types (can be multiple per connectionType)
                self.UpdateCellConnections(obj=obj, connectionType=connType, connectionTypeFile=typeFile, regionName=regionName, column=column, cell=cell)


    def UpdateColumnConnections(self, regionName, region, column, obj, connectionType, connectionTypeFile):

        createConn = False
        destroyConn = False

        if connectionType == 'proximal':
            if self.gui.showProximalSynapses:
                createConn = True
            else:
                destroyConn = True

        if createConn:

            # determine region to get data from
            if hasattr(region, 'unifiedSPRegion'): # if it has unified SP region
                data_regionName = region.unifiedSPRegion
            else:
                data_regionName = regionName
            # load the data
            self.bakeReader.LoadColumnConnections(connectionType=connectionType, connectionTypeFile=connectionTypeFile,
                                                  regionName=data_regionName, iteration=self.iteration,
                                                  colID=column,
                                                  connectedOnly=self.gui.showOnlyConnectedSynapses)  # proximal, but without prefix, because they are the only one

            if connectionType not in self.bakeReader.regions[data_regionName].columnConnections or \
                    column not in [x[0] for x in
                                   self.bakeReader.regions[data_regionName].columnConnections[connectionType]]:
                printLog("Don't have column data for requested column:" + str(column) + " of region:" + str(regionName))
                # self.HTMObjects[obj].regions[regionName].DestroyProximalSynapses()
                return
            self.HTMObjects[obj].regions[regionName].DestroySynapses(synapseType=connectionType)
            self.HTMObjects[obj].regions[regionName].ShowSynapses(self.HTMObjects["HTM1"].regions, self.bakeReader,
                                                                  synapsesType=connectionType, column=column, cell=-1,
                                                                  onlyActive=self.gui.showOnlyActiveSynapses)
        if destroyConn:
            self.HTMObjects[obj].regions[regionName].DestroySynapses(synapseType=connectionType)

    # loads data, destroys previous synapses, creates new ones
    def UpdateCellConnections(self, obj, connectionType, connectionTypeFile, regionName, column, cell):

        createConn = False
        destroyConn = False

        if connectionType == 'distal':
            if self.gui.showDistalSynapses :
                createConn = True
            else:
                destroyConn = True

        if connectionType == 'apical':
            if self.gui.showDistalSynapses :
                createConn = True
            else:
                destroyConn = True

        if connectionType == 'proximal' and self.HTMObjects[obj].regions[regionName].type == 'py.ColumnPoolerRegion': # special case
            if self.gui.showProximalSynapses :
                createConn = True
            else:
                destroyConn = True

        if createConn:

            if hasattr(self.HTMObjects[obj].regions[regionName], 'nOfCellsPerColumn'):
                cellID = column * self.HTMObjects[obj].regions[
                    regionName].nOfCellsPerColumn + cell
            else:
                cellID = cell
            # load it
            self.bakeReader.LoadCellConnections(connectionType=connectionType, connectionTypeFile=connectionTypeFile, regionName=regionName,
                                                iteration=self.iteration,
                                                cellID=cellID,
                                                connectedOnly=self.gui.showOnlyConnectedSynapses)

            self.HTMObjects[obj].regions[regionName].DestroySynapses(synapseType=connectionType)
            self.HTMObjects[obj].regions[regionName].ShowSynapses(self.HTMObjects["HTM1"].regions, self.bakeReader,
                                                                  synapsesType=connectionType, column=column, cell=cell,
                                                                  onlyActive=self.gui.showOnlyActiveSynapses)
        if destroyConn:
            self.HTMObjects[obj].regions[regionName].DestroySynapses(synapseType=connectionType)


    def update(self, task):

        self.gui.update()
        self.interaction.Update()

        if self.allHTMobjectsCreated and not self.initIterationLoaded:  # wait till the objects are created, then load iteration 0
            self.LoadIteration(0)
            self.initIterationLoaded = True

        # --------------------------- GUI COMMANDS ---------------------------------------------------------------------
        if self.gui.gotoReq >= 0:
            self.LoadIteration(self.gui.gotoReq)
            self.gui.gotoReq = -1

        if self.gui.cmdRun and (self.tmrRun - time.time())>1: # each second perform step +1
            self.LoadIteration(self.iteration+1)
            self.tmrRun = time.time()

        if self.gui.cmdStop:
            self.gui.cmdRun = False
            self.gui.cmdStop = False

        if self.gui.capture:
            path = os.path.join(os.path.dirname(self.databaseFilePath),"capture")
            if not os.path.exists(path):
                os.makedirs(path)

            self.LoadIteration(self.autoRunIteration)
            self.autoRunIteration += 1
            if self.autoRunIteration > self.gui.cntIterations:
                self.gui.capture =False
                os.system("ffmpeg -y -framerate 10 -i "+path+"/%01d.jpg -codec copy "+path+"/recording.mkv")
            self.win.saveScreenshot(path+'/'+str(self.autoRunIteration)+'.jpg')

        # --------------------------------------------------------------------------------------------------------------

        if self.gui.updateConnections:
            print("Updating connections due to change in GUI settings")
            self.UpdateConnections()
            self.gui.updateConnections = False


        if self.gui.terminating:
            sys.exit()

        return task.cont

    def gfxCreationWorker(self, task):
        #time.sleep(20) # need to delay this, there was SIGSEG faults, probably during creation of objects thread collision happens
        #printLog("Starting GFX worker thread")
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

        if self.allHTMobjectsCreated or self.gui.terminating:
            return 0 # this return causes not to call this method anymore
        else:
            return task.cont

    # def FindReferences(self):
    #     for obj in self.HTMObjects:
    #         for regName in self.HTMObjects[obj].regions:
    #             self.HTMObjects[obj].regions[regName].
    #             self.bakeReader.LoadCellConnections(connectionType=connectionType,
    #                                                 connectionTypeFile=connectionTypeFile, regionName=regionName,
    #                                                 iteration=self.iteration,  # basal = distal
    #                                                 cellID=cellID,
    #                                                 connectedOnly=self.gui.showOnlyConnectedSynapses)  # load it

if __name__ == "__main__":
    import sys
    app = cExplorer3D(sys.argv[1])  # first argument is database path
    app.run()


