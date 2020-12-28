# -*- coding: utf-8 -*-

from pandaBaker.bakerDatabase import Database

import numpy as np
import os
import json
import time


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
            if not os.path.exists(os.path.dirname(self.databaseFilePath)):
                os.mkdir(os.path.dirname(self.databaseFilePath))

        # dump folder path
        self.dumpFolderPath = os.path.splitext(self.databaseFilePath)[0] + "_dumpData"
        if not os.path.exists(self.dumpFolderPath):
            os.mkdir(self.dumpFolderPath)

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
            outs = getOutputsOfRegion(regInstance[1])#get outputs from name
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
            for out in getOutputsOfRegion(regInstance[1]):
                regionOutArr = np.array(network.getRegion(regName).getOutputArray(out), dtype=np.float32)

                self.db.InsertDataArray('region__'+regName+'__'+out,
                                iteration, regionOutArr)


            if regInstance[0] in ["SPRegion", "py.ApicalTMPairRegion", "TMRegion", 'py.ColumnPoolerRegion', 'py.GridCellLocationRegion']: # here list all regions that have connections
                regInstance[1].executeCommand("saveConnectionsToFile",
                                                           os.path.join(self.dumpFolderPath,str(regName) + "_" + str(iteration)))

        # ---------------- DATA STREAMS -----------------------------------

        for pl in self.dataStreams:
            tableName = 'dataStream_' + pl

            if(type(self.dataStreams[pl].value)not in [float, int]):
                raise RuntimeError("Datatype:"+str(type(self.dataStreams[pl].value))+" is not supported!")
            self.db.InsertDataArray(tableName, iteration, self.dataStreams[pl].value)


def getOutputsOfRegion(region):
    outs = json.loads(region.getSpec().toString().replace("\n", ""))["outputs"].keys()
    return outs

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

