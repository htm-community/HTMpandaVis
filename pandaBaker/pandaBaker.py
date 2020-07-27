# -*- coding: utf-8 -*-

from bakerDatabase import Database
import dataStructs as dataStructs

import numpy as np
import os
import json
import time
from htm.bindings.algorithms import TemporalMemory
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing import get_context

# import all python regions
from htm.advanced.regions.ApicalTMPairRegion import ApicalTMPairRegion
from htm.advanced.regions.ApicalTMSequenceRegion import ApicalTMSequenceRegion
from htm.advanced.regions.ColumnPoolerRegion import ColumnPoolerRegion
from htm.advanced.regions.GridCellLocationRegion import GridCellLocationRegion
from htm.advanced.regions.ColumnPoolerRegion import ColumnPoolerRegion
from htm.advanced.regions.RawSensor import RawSensor
from htm.advanced.regions.RawValues import RawValues


CPU_CORES = 4

a= ColumnPoolerRegion()

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
            self.db.Insert(tableName, regionName,regionInstance[0], json.dumps(getParametersOfRegion(regionInstance[0], regionInstance[1])))

        self.db.CreateTable('links',
                            "id INTEGER, sourceRegion TEXT, sourceOutput TEXT, destinationRegion TEXT, destinationInput TEXT")
        for idx, data in structure['links'].items():
            self.db.Insert("links", str(idx), data[0], data[1], data[2], data[3])

        # DATA carying tables creation ---------------------------------------------------------------------------------
        for regName, regInstance in structure["regions"].items():
            outs = getOutputsOfRegion(regInstance[0])#get outputs from name
            for out in outs:
                self.db.CreateTable('region__'+regName+'__'+out, "iteration INTEGER, data SDR")
            #self.db.CreateTable('layer_proximalSynapses_'+ ly, "iteration INTEGER, column INTEGER, data array")#using float numpy array, not sparse SDR

        # data streams ----------------
        for pl in self.dataStreams:
            if(pl.find(' ')!=-1):
                raise RuntimeError("Name of datastream can't contain whitespaces. Name:"+str(pl))
        
            tableName = 'dataStream_' + pl
            self.db.CreateTable(tableName, "iteration INTEGER PRIMARY KEY, value " + self.dataStreams[pl].dataType)

        self.CommitBatch()

    def CommitBatch(self):# writes to the file, do it reasonably, it takes time
        self.db.conn.commit()

    def StoreIteration(self, network, iteration):

        #region data
        for regName, regInstance in self.structure['regions'].items():
            for out in getOutputsOfRegion(regInstance[0]):
                self.db.InsertDataArray('region__'+regName+'__'+out,
                                iteration, network.getRegion(regName).getOutputArray(out))



            # dumpFilePath = os.path.join(os.path.splitext(self.databaseFilePath)[0]+"_distalDump",""+str(ly)+"_"+str(iteration)+".dump")
            #
            # if isinstance(layer.tm, TemporalMemory):
            #     layer.tm.saveToFile(dumpFilePath)
            #
            #     f = open(os.path.join(os.path.splitext(self.databaseFilePath)[0]+"_distalDump", str(ly)+"_version.txt"), 'wt')
            #     f.write("1")
            #     f.close()
            # else:
            #     #if apicalTM from advanced code
            #     byteStream = layer.tm.basalConnections.save()
            #     f = open(dumpFilePath, 'wb')
            #     f.write(byteStream)
            #     f.close()
            #
            #     f = open(os.path.join(os.path.splitext(self.databaseFilePath)[0] + "_distalDump",
            #                                        str(ly) + "_version.txt"), 'wt')
            #     f.write("2")
            #     f.close()

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

def getParametersOfRegion(regionType, regionInstance):
    if 'py.' in regionType:
        # python region
        parList = list(eval(regionType.split('.')[1]).getSpec()['parameters'].keys())

        resultDict = {}
        for par in parList:
            resultDict[par] = regionInstance.eval(par)# nevim jestli to jde castnout abych dostal parametry..

        return resultDict
    else:
        # c++ region
        return list(eval(regionType).getSpec()['parameters'].keys())

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

