# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database

import numpy as np
import os
import json
import time

#import multiprocessing as mp
#from multiprocessing import Pool
#from multiprocessing import get_context

from htm.bindings.sdr import SDR

#algorithm classes
from htm.bindings.algorithms import TemporalMemory
from htm.advanced.algorithms.apical_tiebreak_temporal_memory import ApicalTiebreakTemporalMemory


# import all python regions
from htm.advanced.regions.ApicalTMPairRegion import ApicalTMPairRegion
from htm.advanced.regions.ApicalTMSequenceRegion import ApicalTMSequenceRegion
from htm.advanced.regions.ColumnPoolerRegion import ColumnPoolerRegion
from htm.advanced.regions.GridCellLocationRegion import GridCellLocationRegion
from htm.advanced.regions.ColumnPoolerRegion import ColumnPoolerRegion
from htm.advanced.regions.RawSensor import RawSensor
from htm.advanced.regions.RawValues import RawValues


#CPU_CORES = 4

class PandaBaker(object):
    def __init__(self, databaseFilePath, bakeProximalSynapses = True, bakeDistalSynapses = True):
        self.databaseFilePath = databaseFilePath
        self.db = None

        self.regions = {}
        self.links = {}

        self.structure = {}

        self.dataStreams = {}  # can contain cDataStream instances

        #flags what to bake
        self.bakeProximalSynapses = bakeProximalSynapses
        self.bakeDistalSynapses = bakeDistalSynapses

        # for raw anomaly calculation
        self.previousPredictiveCells = {} # dict storing predictive cells for previous timestamp for each layer


    # creates database tables according to given dict
    def PrepareDatabase(self, structure):
        self.structure = structure
        #create database file, delete if exists
        if os.path.exists(self.databaseFilePath):
            Log("database file "+self.databaseFilePath+" exists, deleting...")
            os.remove(self.databaseFilePath)
        else:
            Log("Creating new database file:"+self.databaseFilePath)

        self.db = Database(self.databaseFilePath)  # connect to the database


        # structure definition tables creation -------------------------------------------------------------------------

        tableName = 'region_parameters'
        self.db.CreateTable(tableName, "region TEXT, regionType TEXT, parameters TEXT")

        for regionName, regionInstance in structure["regions"].items():
            self.db.Insert(tableName, regionName,regionInstance[0], json.dumps(regionInstance[1].getParameters()))

        self.db.CreateTable('links',
                            "id INTEGER, sourceRegion TEXT, sourceOutput TEXT, destinationRegion TEXT, destinationInput TEXT")
        for idx, data in structure['links'].items():
            self.db.Insert("links", str(idx), data[0], data[1], data[2], data[3])

        # DATA carying tables creation ---------------------------------------------------------------------------------
        for regName, regInstance in structure["regions"].items():
            outs = getOutputsOfRegion(regInstance[0])#get outputs from name
            for out in outs:
                self.db.CreateTable('region__'+regName+'__'+out, "iteration INTEGER, data ARRAY")
            #self.db.CreateTable('layer_proximalSynapses_'+ ly, "iteration INTEGER, column INTEGER, data array")#using float numpy array, not sparse SDR

        self.CommitBatch()

    def CreateDataStream(self, datastreamName, datastreamInstance): # datastreams are created on-the-go to avoid non-comfortable defining at start
        self.dataStreams[datastreamName] = datastreamInstance # add it
        # data streams ----------------
        if (datastreamName.find(' ') != -1):
            raise RuntimeError("Name of datastream can't contain whitespaces. Name:" + str(datastreamName))

        tableName = 'dataStream_' + datastreamName
        self.db.CreateTable(tableName, "iteration INTEGER PRIMARY KEY, value " + datastreamInstance.dataType)

    def CommitBatch(self):# writes to the file, do it reasonably, it takes time
        self.db.conn.commit()

    def StoreIteration(self, network, iteration):

        #region data
        for regName, regInstance in self.structure['regions'].items():
            for out in getOutputsOfRegion(regInstance[0]):
                regionOutArr = np.array(network.getRegion(regName).getOutputArray(out), dtype=np.float32)
                #regionOutSDR = SDR(regionOutArr.size)
                #regionOutSDR.dense = regionOutArr

                self.db.InsertDataArray('region__'+regName+'__'+out,
                                iteration, regionOutArr)

            dumpFolderPath = os.path.splitext(self.databaseFilePath)[0] + "_dumpData"


            print(str(regName) + " is type of "+str(type(regInstance[1])))
            object_methods = [method_name for method_name in dir(regInstance[1])
                              if callable(getattr(regInstance[1], method_name))]
            conn = regInstance[1].getConnections("dummyName")
            print(object_methods)
            if regInstance[0]=="py.ApicalTMPairRegion":
                regInstance[0].__class__ = ApicalTiebreakTemporalMemory
                byteStream = regInstance[1].basalConnections.save()
            if isinstance(regInstance[1], TemporalMemory):
                layer.tm.saveToFile(os.path.join(dumpFilePath, str(regName) + "_completeTM_" + str(iteration) + ".dump"))

                #f = open(os.path.join(os.path.splitext(self.databaseFilePath)[0]+"_distalDump", str(ly)+"_version.txt"), 'wt')
                #f.write("1")
                #f.close()
            elif isinstance(regInstance[1], ApicalTiebreakTemporalMemory):
                byteStream = layer.tm.basalConnections.save()
                f = open(os.path.join(dumpFilePath, str(regName) + "_basalConn_" + str(iteration) + ".dump"), 'wb')
                f.write(byteStream)
                f.close()

                byteStream = layer.tm.apicalConnections.save()
                f = open(os.path.join(dumpFilePath, str(regName) + "_apicalConn_" + str(iteration) + ".dump"), 'wb')
                f.write(byteStream)
                f.close()

        # ---------------- DATA STREAMS -----------------------------------

        for pl in self.dataStreams:
            tableName = 'dataStream_' + pl

            if(type(self.dataStreams[pl].value)not in [float, int]):
                raise RuntimeError("Datatype:"+str(type(self.dataStreams[pl].value))+" is not supported!")
            self.db.InsertDataArray(tableName, iteration, self.dataStreams[pl].value)


def getOutputsOfRegion(regionType):
    if 'py.' in regionType:
        # python region
        return list(eval(regionType.split('.')[1]).getSpec()['outputs'].keys())
    else:
        # c++ region
        return list(eval(regionType).getSpec()['outputs'].keys())


def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #create directory if not exists
    logPath = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    with open(os.path.join(logPath,"pandaBaker.log"),"a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

