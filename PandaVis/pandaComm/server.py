#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:22:19 2019

@author: osboxes
"""

import socket, pickle, struct
from socket import error as SocketError
import threading
from PandaVis.pandaComm.dataExchange import ServerData, CLIENT_CMD, SERVER_CMD
import numpy
import time

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityMedium
)  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


def PackData(cmd, data):
    d = [cmd, data]
    # Pickle the object and send it to the server
    # protocol must be specified to be able to work with py2 on server side
    rawData = pickle.dumps(d, protocol=2)

    if len(rawData) % 4096 == 0:  # if length of data is multiple of chunck size
        # increase the data by 1 byte to prevent it - it causes problems in recv function
        # on the client side - because client doesn't know how long data to expect
        if isinstance(data, ServerData):
            data.compensateSize.append(1)  # increase size by some dummy bytes
            d = [cmd, data]
            rawData = pickle.dumps(d)  # , protocol=2)
        else:
            printLog("Packed data is multiple of chunck size, but not known instance")

    return rawData


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack("!I", length))
    sock.sendall(data)


def recv_one_message(sock):
    lengthbuf = sock.recv(4)
    length, = struct.unpack("!I", lengthbuf)
    return sock.recv(length)


class PandaServer:
    def __init__(self):
        self.serverData = ServerData()
        self.cmdRunOneStep = False
        self.cmdRunInLoop = False
        self.cmdGotoIteration = False
        self.gotoIteration = 0
        self.currentIteration = 0
        self.newStateDataReadyForVis = False
        self.mainThreadQuitted = False

        self.serverThread = ServerThread(self, 1, "ServerThread-1")

        self.spatialPoolers = {}  # two level dict, {'HTMobject' : {'layer' : spatialPoolerInstance}}
        self.temporalMemories = {}  #two level dict, {'HTMobject' : {'layer' : temporalMemoryInstance}}

    def Start(self):
        self.serverThread.start()

    def MainThreadQuitted(self):  # if the parent thread is terminated, end this one too
        self.mainThreadQuitted = True
        self.serverThread.join()

    def NewStateDataReady(self):
        self.newStateDataReadyForVis = True

    def RunServer(self):
        HOST = "localhost"
        PORT = 50007

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # prevent "adress in use" exception
        s.settimeout(5)
        s.bind((HOST, PORT))
        s.listen(1)

        printLog("Server listening")

        clientConnected = False

        while not clientConnected and not self.mainThreadQuitted:
            try:
                conn, addr = s.accept()
                conn.settimeout(5)
                printLog("Connected by" + str(addr))
                clientConnected = True
                self.newStateDataReadyForVis = True
            except socket.timeout:
                continue

            if not clientConnected:
                printLog("Client is not connected anymore")
                return

            quitServer = False

            while not quitServer and not self.mainThreadQuitted:
                try:
                    rxRawData = recv_one_message(conn)
                    # rxRawData = conn.recv(4096)

                    rxData = pickle.loads(rxRawData)

                    #self.serverData = ServerData() # clear server data to start with blank structure

                    if rxData[0] == CLIENT_CMD.CMD_GET_STATE_DATA:
                        #printLog("State data requested", verbosityHigh)
                        if self.newStateDataReadyForVis:

                            send_one_message(
                                conn, PackData(SERVER_CMD.SEND_STATE_DATA, self.serverData)
                            )

                            self.newStateDataReadyForVis = False
                        else:
                            send_one_message(
                                conn, PackData(SERVER_CMD.NA, [])
                            )  # we dont have any new data for client
                            #printLog("But no new data available", verbosityHigh)

                    elif rxData[0] == CLIENT_CMD.CMD_GET_PROXIMAL_DATA:
                        printLog("Proximal data req by client", verbosityMedium)
                        printLog(rxData, verbosityHigh)

                        HTMObjectName = rxData[1][0][0]
                        layerName = rxData[1][0][1]
                        requestedCol = int(rxData[1][1])

                        printLog(
                            "HTM object:"
                            + str(HTMObjectName)
                            + " layerName:"
                            + str(layerName)
                            + " reqCol:"
                            + str(requestedCol),
                            verbosityMedium,
                        )
                        # SP - proximal synapses
                        sp = self.spatialPoolers[HTMObjectName][layerName]
                        connectedSynapses = numpy.zeros(
                            sp.getNumInputs(), dtype=numpy.float32
                        )
                        sp.getPermanence(requestedCol, connectedSynapses, sp.getSynPermConnected())#sp.getConnectedSynapses(requestedCol, connectedSynapses)

                        self.ClearNonStaticData()  # clear previous data (e.g. for other layers)

                        self.serverData.HTMObjects[HTMObjectName].layers[
                            layerName
                        ].proximalSynapses = [[requestedCol, connectedSynapses]]

                        printLog(
                            "Sending:"
                            + str(
                                self.serverData.HTMObjects[HTMObjectName]
                                .layers[layerName]
                                .proximalSynapses
                            ),
                            verbosityHigh,
                        )
                            
                        send_one_message(
                            conn, PackData(SERVER_CMD.SEND_PROXIMAL_DATA, self.serverData)
                        )

                        printLog(
                            "Sent synapses of len:" + str(len(connectedSynapses)),
                            verbosityHigh,
                        )
                        # printLog("GETTING CELL DATA:")
                        # printLog(self.serverData.connectedSynapses)
                    elif rxData[0] == CLIENT_CMD.CMD_GET_DISTAL_DATA:
                        printLog("Distal data req by client", verbosityMedium)
                        printLog(rxData, verbosityHigh)

                        HTMObjectName = rxData[1][0][0]
                        layerName = rxData[1][0][1]
                        requestedColumn = int(rxData[1][1])
                        requestedCell = int(rxData[1][2])
                        
                        cellsPerColumn = self.serverData.HTMObjects[HTMObjectName].layers[layerName].cellsPerColumn
                        reqCellID = requestedColumn*cellsPerColumn + requestedCell
                        
                        printLog("Requested cell ID:"+str(reqCellID),verbosityMedium)

                        if not layerName in self.temporalMemories[HTMObjectName]:
                            printLog("This layer doesn't have TM, can't request distal connections.. skipping")
                            continue
                        tm = self.temporalMemories[HTMObjectName][layerName]

                        presynCells = getPresynapticCellsForCell(tm,reqCellID)
                        
                        #printLog("PRESYN CELLS:"+str(presynCells))
                        #winners = tm.getWinnerCells()
                        
                        #print(winners)

                        self.ClearNonStaticData() # clear previous data (e.g. for other layers)

                        self.serverData.HTMObjects[HTMObjectName].layers[
                            layerName
                        ].distalSynapses = [[requestedColumn,requestedCell,presynCells]]#sending just one pack for one cell
                        send_one_message(
                            conn, PackData(SERVER_CMD.SEND_DISTAL_DATA, self.serverData)
                        )

                        
                    elif rxData[0] == CLIENT_CMD.CMD_RUN:
                        self.cmdRunInLoop = True
                        printLog("RUN", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.CMD_STOP:
                        self.cmdRunInLoop = False
                        printLog("STOP", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.CMD_STEP_FWD:
                        self.cmdRunOneStep = True
                        printLog("STEP", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.CMD_GOTO:
                        self.cmdGotoIteration = True
                        self.gotoIteration = rxData[1]
                        printLog("GOTO:"+str(self.gotoIteration), verbosityHigh)

                        if self.serverData.iterationNo >= self.gotoIteration: # handle when current iteration is above or equal requested
                            self.cmdGotoIteration = False

                    elif rxData[0] == CLIENT_CMD.QUIT:
                        printLog("Client quitted!")
                        # quitServer=True
                except struct.error as e:
                    printLog("StructError:")
                    printLog(e)
                    clientConnected = False
                    break
                except socket.timeout:
                    printLog("SocketTimeout")
                    continue
                except SocketError as e:
                    printLog("SocketError")
                    printLog(e)
                    clientConnected = False
                    break
                except EOFError:
                    printLog("EOFError")
                    clientConnected = False
                    break
                # except Exception as e:
                #    printLog("Exception" + str(sys.exc_info()[0]))
                #    printLog(str(e))

                # quitServer=True

        printLog("Server quit")
        conn.close()

    def ClearNonStaticData(self):# we need to clean up previous data, for example last time distal connections was requested, but now state data is requested

        for obj in self.serverData.HTMObjects.values():
            for ly in obj.layers.values():
                ly.proximalSynapses = {}
                ly.distalSynapses = {}

                ly.activeColumns = []  # currently active columns (sparse) in this layer
                ly.activeCells = []
                ly.winnerCells = []
                ly.predictiveCells = []

            for inp in obj.inputs.values():
                inp.bits = []

    def BlockExecution(self):
        if self.cmdGotoIteration:
          if self.gotoIteration <= self.currentIteration:
              self.cmdGotoIteration = False

        if not self.cmdGotoIteration:
            printLog("One step finished")
            while not self.cmdRunInLoop and not self.cmdRunOneStep and not self.cmdGotoIteration:
              pass
            self.cmdRunOneStep = False
            printLog("Proceeding one step...")

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

    printLog("getPresynapticCellsForCell() took %s seconds " % (time.time() - start_time), verbosityHigh)
    return res

class ServerThread(threading.Thread):
    def __init__(self, serverInstance, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.serverInstance = serverInstance

    def run(self):
        printLog("Starting " + self.name)
        self.serverInstance.RunServer()
        printLog("Exiting " + self.name)
