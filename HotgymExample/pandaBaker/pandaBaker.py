# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database
from pandaBaker.dataStructs import cLayer,cInput
import numpy as np
import os
import time

class PandaBaker(object):
    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath
        self.db = None

        self.layers = {}  # can contain cLayer instances
        self.inputs = {}  # can contain cInput instances

        #flags what to bake
        self.bakeProximalSynapses = False
        self.bakeDistalSynapses = False


    def PrepareDatabase(self):
        #create database file, delete if exists
        if os.path.exists(self.databaseFilePath):
            Log("database file "+self.databaseFilePath+" exists, deleting...")
            os.remove(self.databaseFilePath)
        else:
            Log("Creating new database file:"+self.databaseFilePath)

        self.db = Database(self.databaseFilePath)  # connect to the database


        # STATIC tables creation -----------------------------------------------------------------------------
        self.db.CreateTable('connections', "input TEXT, layer TEXT, type TEXT")


        self.db.CreateTable('par_inputs','name TEXT, size INTEGER')
        for inp in self.inputs:
            self.db.Insert('par_inputs', [inp, str(self.inputs[inp].size)])


        for ly in self.layers:
            tableName = 'par_layers_'+ly
            self.db.CreateTable(tableName, "name TEXT, value REAL")
            self.db.InsertParameters(tableName, self.layers[ly].params)
            #create table for defining to what inputs these layers are connected
            for pi in self.layers[ly].proximalInputs:
                self.db.Insert("connections", [pi, ly, 'proximal'])
            for pi in self.layers[ly].distalInputs:
                self.db.Insert("connections", [pi, ly, 'distal'])

        # DYNAMIC tables creation -----------------------------------------------------------------------------

        for inp in self.inputs:
            self.db.CreateTable('inputs_'+inp, "iteration INTEGER, value TEXT, data SDR")
        for ly in self.layers:
            self.db.CreateTable('layer_activeColumns_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_predictiveCells_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_winnerCells_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_activeCells_'+ly, "iteration INTEGER, data SDR")

        self.db.conn.commit()

    def CommitBatch(self):# writes to the file, do it reasonably, it takes time
        self.db.conn.commit()

    def StoreIteration(self, iteration):
        # store input states
        for inp in self.inputs:
            self.db.InsertDataArray2('inputs_'+inp, iteration, self.inputs[inp].stringValue, self.inputs[inp].bits)
        #layer states
        for ly in self.layers:
            self.db.InsertDataArray('layer_activeColumns_' + ly,
                                iteration, self.layers[ly].activeColumns)
            self.db.InsertDataArray('layer_predictiveCells_' + ly,
                                iteration, self.layers[ly].predictiveCells)
            self.db.InsertDataArray('layer_winnerCells_' + ly,
                                iteration, self.layers[ly].winnerCells)
            self.db.InsertDataArray('layer_activeCells_' + ly,
                                iteration, self.layers[ly].activeCells)

            layer = self.layers[ly]
            sp = layer.sp
            if sp is not None and self.bakeProximalSynapses:

                if layer.spParams['sp_columnDimensions_y']==0:
                    columnCount = layer.spParams['sp_columnDimensions_x']
                else:
                    #two dimensional SP
                    columnCount = layer.spParams['sp_columnDimensions_x']*layer.spParams['sp_columnDimensions_y']

                layer.proximalSynapses = [] # erase
                for col in range(columnCount):
                    #proximal synapses
                    synapses = np.zeros(
                        sp.getNumInputs(), dtype=np.float32
                    )
                    sp.getPermanence(col, synapses,
                                     0.0)#get all permanences

                    layer.proximalSynapses.append(synapses)

            tm = layer.tm
            #if tm is not None and self.bakeDistalSynapses:

                # cellsPerColumn = self.serverData.HTMObjects[HTMObjectName].layers[layerName].cellsPerColumn
                # reqCellID = requestedColumn * cellsPerColumn + requestedCell
                #
                # printLog("Requested cell ID:" + str(reqCellID), verbosityMedium)
                #
                # if not layerName in self.temporalMemories[HTMObjectName]:
                #     printLog("This layer doesn't have TM, can't request distal connections.. skipping")
                #     continue
                # tm = self.temporalMemories[HTMObjectName][layerName]
                #
                # presynCells = getPresynapticCellsForCell(tm, reqCellID)
                #
                # # printLog("PRESYN CELLS:"+str(presynCells))
                # # winners = tm.getWinnerCells()
                #
                # # print(winners)
                #
                # self.ClearNonStaticData()  # clear previous data (e.g. for other layers)
                #
                # self.serverData.HTMObjects[HTMObjectName].layers[
                #     layerName
                # ].distalSynapses = [
                #     [requestedColumn, requestedCell, presynCells]]  # sending just one pack for one cell

def getPresynapticCellsForCell(tm, cellID):
    start_time = time.time()
    segments = tm.connections.segmentsForCell(cellID)

    synapses = []
    res = []
    for seg in segments:
        for syn in tm.connections.synapsesForSegment(seg):
            synapses += [syn]

        presynapticCells = []
        for syn in synapses:
            presynapticCells += [tm.connections.presynapticCellForSynapse(syn)]

        res += [presynapticCells]

    Log("getPresynapticCellsForCell() took %s seconds " % (time.time() - start_time), verbosityHigh)
    return res

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

