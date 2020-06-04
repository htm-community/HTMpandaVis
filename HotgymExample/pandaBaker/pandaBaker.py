# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database
from pandaBaker.dataStructs import cLayer,cInput
from htm.algorithms.anomaly import Anomaly
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
        self.bakeProximalSynapses = True
        self.bakeDistalSynapses = True
        self.bakeRawAnomalyScore = False

        # for raw anomaly calculation
        self.previousPredictiveCells = {} # dict storing predictive cells for previous timestamp for each layer


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
            self.db.CreateTable('layer_proximalSynapses_'+ ly, "iteration INTEGER, column INTEGER, data SDR")
            self.db.CreateTable('layer_distalSynapses_' + ly, "iteration INTEGER, column INTEGER, cell INTEGER, data SDR")
            self.db.CreateTable('layer_rawAnomaly_' + ly,
                                "iteration INTEGER, value REAL")

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
            # ---------------- PROXIMAL SYNAPSES ----------------------------------
            sp = layer.sp
            if sp is not None and self.bakeProximalSynapses:

                layer.proximalSynapses = [] # erase
                for col in range(layer.params['sp_columnCount']):
                    #proximal synapses
                    synapses = np.zeros(
                        sp.getNumInputs(), dtype=np.float32
                    )
                    sp.getPermanence(col, synapses,
                                     0.0)#get all permanences

                    #layer.proximalSynapses.append(synapses) no need to store it probably
                    self.db.InsertDataArray2('layer_proximalSynapses_' + ly,
                                            iteration, col, synapses)

            # ---------------- DISTAL SYNAPSES ----------------------------------
            tm = layer.tm
            if self.bakeDistalSynapses:
                if tm is None:
                    Log("This layer doesn't have TM, can't get distal synapses.. skipping")
                    continue
                cellCnt = 0
                for col in range(layer.params['sp_columnCount']):
                    for cell in range(layer.params['tm_cellsPerColumn']):
                        reqCellID = col * layer.params['tm_cellsPerColumn'] + cell

                        # bake distal synapses only for active or predictive cells, about others we don't care, it would take too much time
                        if reqCellID in self.layers[ly].activeCells or reqCellID in self.layers[ly].predictiveCells:
                            presynCells = getPresynapticCellsForCell(tm, reqCellID)

                            self.db.InsertDataArray3('layer_distalSynapses_' + ly,
                                                 iteration, col, cell, presynCells)
                            cellCnt = cellCnt + 1

                Log("Baked distal data for "+str(cellCnt)+" cells in layer "+str(ly))

            # ---------------- RAW anomaly score -----------------------------------

            if self.bakeRawAnomalyScore:
                if layer in self.previousPredictiveCells:
                    rawAnomaly = Anomaly.calculateRawAnomaly(self.layers[ly].activeColumns,
                                        tm.cellsToColumns(self.previousPredictiveCells[layer]))
                else:
                    rawAnomaly = 1.0 # first timestamp

                self.db.InsertDataArray("layer_rawAnomaly_"+str(ly), iteration, rawAnomaly)

                self.previousPredictiveCells[layer] = self.layers[ly].predictiveCells



def getPresynapticCellsForCell(tm, cellID):
    start_time = time.time()
    segments = tm.connections.segmentsForCell(cellID)

    #synapses = []
    res = []

    #if len(segments) > 0:
        #Log("segments len:"+str(len(segments)))
    for seg in segments:
        time1 = time.time()
        synapsesForSegment = tm.connections.synapsesForSegment(seg)
        #Log("synapsesForSegment() took %s ms " % ((time.time() - time1)*1000))
        #Log("synapses for segment len:" + str(len(segments)))
        #Log("datatype:" + str(type(synapsesForSegment)))
        #Log("synapsesForSegment len:" + str(len(synapsesForSegment)))

        #for syn in synapsesForSegment:
            #synapses += [syn]

        presynapticCells = []
        for syn in synapsesForSegment:
            #time2 = time.time()
            presynapticCells += [tm.connections.presynapticCellForSynapse(syn)]
            #Log("presynapticCellForSynapse() took %s ms " % ((time.time() - time2)*1000))

        res += [presynapticCells]

    #if len(segments) > 0:
        #Log("getPresynapticCellsForCell() took %s ms " % ((time.time() - start_time)*1000))
    return np.array(res) # TODO figure out if using directly numpy is faster

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

