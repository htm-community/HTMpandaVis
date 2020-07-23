# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database
from pandaBaker.dataStructs import cLayer,cInput,cDataStream

import numpy as np
import os
import time
from htm.bindings.algorithms import TemporalMemory
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing import get_context

CPU_CORES = 4

class PandaBaker(object):
    def __init__(self, databaseFilePath, bakeProximalSynapses = True, bakeDistalSynapses = True):
        self.databaseFilePath = databaseFilePath
        self.db = None

        self.regions = {}
        self.links = {}
        self.dataStreams = {}  # can contain cDataStream instances

        #flags what to bake
        self.bakeProximalSynapses = bakeProximalSynapses
        self.bakeDistalSynapses = bakeDistalSynapses

        # for raw anomaly calculation
        self.previousPredictiveCells = {} # dict storing predictive cells for previous timestamp for each layer


    # creates database tables according to given dict
    def PrepareDatabase(self, structure):
        #create database file, delete if exists
        if os.path.exists(self.databaseFilePath):
            Log("database file "+self.databaseFilePath+" exists, deleting...")
            os.remove(self.databaseFilePath)
        else:
            Log("Creating new database file:"+self.databaseFilePath)

        self.db = Database(self.databaseFilePath)  # connect to the database


        # STATIC tables creation -----------------------------------------------------------------------------

        tableName = 'region_parameters'
        self.db.CreateTable(tableName, "region TEXT, parameters TEXT")

        for reg in structure["regions"]:
            self.db.Insert(tableName, reg[0], reg[1])

        self.db.CreateTable('links',
                            "sourceRegion TEXT, sourceOutput TEXT, destinationRegion TEXT, destinationInput TEXT")
        for l in self.links:
            self.db.Insert("links", [pi, ly, 'proximal'])

        # DYNAMIC tables creation -----------------------------------------------------------------------------

        for inp in self.inputs:
            self.db.CreateTable('inputs_'+inp, "iteration INTEGER, value TEXT, data SDR")

        for ly in self.layers:
            self.db.CreateTable('layer_activeColumns_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_predictiveCells_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_winnerCells_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_activeCells_'+ly, "iteration INTEGER, data SDR")
            self.db.CreateTable('layer_proximalSynapses_'+ ly, "iteration INTEGER, column INTEGER, data array")#using float numpy array, not sparse SDR
            self.db.CreateTable('layer_distalSynapses_' + ly, "iteration INTEGER, column INTEGER, cell INTEGER, segment INTEGER, data SDR")

        # data streams ----------------
        for pl in self.dataStreams:
            if(pl.find(' ')!=-1):
                raise RuntimeError("Name of datastream can't contain whitespaces. Name:"+str(pl))
        
            tableName = 'dataStream_' + pl
            self.db.CreateTable(tableName, "iteration INTEGER PRIMARY KEY, value " + self.dataStreams[pl].dataType)

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

            dumpFilePath = os.path.join(os.path.splitext(self.databaseFilePath)[0]+"_distalDump",""+str(ly)+"_"+str(iteration)+".dump")

            if isinstance(layer.tm, TemporalMemory):
                layer.tm.saveToFile(dumpFilePath)

                f = open(os.path.join(os.path.splitext(self.databaseFilePath)[0]+"_distalDump", str(ly)+"_version.txt"), 'wt')
                f.write("1")
                f.close()
            else:
                #if apicalTM from advanced code
                byteStream = layer.tm.basalConnections.save()
                f = open(dumpFilePath, 'wb')
                f.write(byteStream)
                f.close()

                f = open(os.path.join(os.path.splitext(self.databaseFilePath)[0] + "_distalDump",
                                                   str(ly) + "_version.txt"), 'wt')
                f.write("2")
                f.close()

            # ---------------- DATA STREAMS -----------------------------------

            for pl in self.dataStreams:
                tableName = 'dataStream_' + pl
                
                if(type(self.dataStreams[pl].value)not in [float, int]):
                    raise RuntimeError("Datatype:"+str(type(self.dataStreams[pl].value))+" is not supported!")
                self.db.InsertDataArray(tableName, iteration, self.dataStreams[pl].value)


def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(os.getcwd(), "logs","pandaBaker.log"),"a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

