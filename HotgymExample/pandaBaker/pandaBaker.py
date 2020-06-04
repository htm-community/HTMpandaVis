# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database
from pandaBaker.dataStructs import cLayer,cInput
from htm.algorithms.anomaly import Anomaly
import numpy as np
import os
import time

import multiprocessing as mp

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
            self.db.CreateTable('layer_distalSynapses_' + ly, "iteration INTEGER, column INTEGER, cell INTEGER, segment INTEGER, data SDR")
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

                #run in threads, this is CPU consuming ------------
                # Define an output queue
                output = mp.Queue()

                CPU_CORES = 4
                columnCount = layer.params['sp_columnCount']
                oneBatchSize = int(columnCount/CPU_CORES)
                split_startColIdx = [x*oneBatchSize for x in range(CPU_CORES)]

                print(split_startColIdx)
                # the division can be with remainder so add to the last thread the rest
                if split_startColIdx[CPU_CORES-1]+oneBatchSize<columnCount-1:
                    remainderCols = columnCount-1 - split_startColIdx[CPU_CORES-1]+oneBatchSize

                # Setup a list of processes that we want to run
                processes = [mp.Process(target=self.CalcPresynCells, args=(
                    ly, split_startColIdx[x],oneBatchSize+(remainderCols if x==CPU_CORES-1 else 0) , output)) for x in range(CPU_CORES)]

                # Run processes
                for p in processes:
                    p.start()

                # Wait for completion
                for p in processes:
                    p.join()

                # Get process results from the output queue
                results = [output.get() for p in processes]

                cellCnt = 0
                segmentsCnt = 0
                for result in results:
                     if result is None:
                         continue
                     self.db.InsertDataArray4('layer_distalSynapses_' + ly,
                      iteration, result[0],result[1],result[2],result[3])

                     # cellCnt = cellCnt + result[0]
                    # segmentsCnt = segmentsCnt + result[1]


                #Log("Baked distal data for " + str(cellCnt) + " cells in layer " + str(ly) + " ("+str(segmentsCnt)+"")
                    #self.db.InsertDataArray4('layer_distalSynapses_' + ly,
                                             #iteration, result[0],result[1],result[2],result[3])




            # ---------------- RAW anomaly score -----------------------------------

            if self.bakeRawAnomalyScore:
                if layer in self.previousPredictiveCells:
                    rawAnomaly = Anomaly.calculateRawAnomaly(self.layers[ly].activeColumns,
                                        tm.cellsToColumns(self.previousPredictiveCells[layer]))
                else:
                    rawAnomaly = 1.0 # first timestamp

                self.db.InsertDataArray("layer_rawAnomaly_"+str(ly), iteration, rawAnomaly)

                self.previousPredictiveCells[layer] = self.layers[ly].predictiveCells


    def CalcPresynCells(self, layerName, startCol, colCount, output):

        layer = self.layers[layerName]
        tm = layer.tm
        print("Process start for column range:"+str(startCol)+ " - "+str(startCol+colCount))
        hasSomeOutput = False
        cellCnt = 0
        segmentCnt = 0
        for col in range(startCol, startCol+colCount ):
            for cell in range(layer.params['tm_cellsPerColumn']):
                reqCellID = col * layer.params['tm_cellsPerColumn'] + cell

                # bake distal synapses only for active or predictive cells, about others we don't care, it would take too much time
                if reqCellID in layer.activeCells or reqCellID in layer.predictiveCells:
                    # presynCells = getPresynapticCellsForCell(tm, reqCellID)

                    segments = tm.connections.segmentsForCell(reqCellID)

                    segmentNo = 0
                    for seg in segments:  # seg is ID of segments data
                        synapsesForSegment = tm.connections.synapsesForSegment(seg)

                        presynapticCells = []
                        for syn in synapsesForSegment:
                            presynapticCells += [tm.connections.presynapticCellForSynapse(syn)]

                        #print("putting")
                        output.put([col, cell, segmentNo, np.array(presynapticCells)])
                        #print("done")

                        # self.db.InsertDataArray4(tableName,
                        #                          iteration, col, cell, segmentNo, np.array(presynapticCells))
                        #hasSomeOutput = True
                        segmentNo = segmentNo + 1

                    segmentCnt = segmentCnt + segmentNo
                    cellCnt = cellCnt + 1
        if not hasSomeOutput:
            output.put(None) # need to put something, otherwise output.get() hangs forever
        print("Finished")

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
            print(type(presynapticCells))
        res += [seg, np.array(presynapticCells)]

    #if len(segments) > 0:
        #Log("getPresynapticCellsForCell() took %s ms " % ((time.time() - start_time)*1000))
    return res

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

