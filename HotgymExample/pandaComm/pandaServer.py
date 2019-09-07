#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:22:19 2019

@author: osboxes
"""

import socket, pickle, struct
from socket import error as SocketError
import threading
from pandaComm.dataExchange import ServerData, CLIENT_CMD, SERVER_CMD
import numpy

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
        self.runOneStep = False
        self.runInLoop = False
        self.newDataReadyForVis = False
        self.mainThreadQuitted = False

        self.serverThread = ServerThread(self, 1, "ServerThread-1")

        self.spatialPoolers = {}  # dict of pairs layer:spatialPooler
        self.temporalMemories = {}  # dict of pairs layer:temporalMemory

    def Start(self):
        self.serverThread.start()

    def MainThreadQuitted(self):  # if the parent thread is terminated, end this one too
        self.mainThreadQuitted = True
        self.serverThread.join()

    def NewDataReady(self):
        self.newDataReadyForVis = True

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
                self.newDataReadyForVis = True
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

                    if rxData[0] == CLIENT_CMD.REQ_DATA:
                        printLog("Data requested", verbosityHigh)
                        if self.newDataReadyForVis:

                            send_one_message(
                                conn, PackData(SERVER_CMD.SEND_DATA, self.serverData)
                            )

                            self.newDataReadyForVis = False
                        else:
                            send_one_message(
                                conn, PackData(SERVER_CMD.NA, [])
                            )  # we dont have any new data for client
                            printLog("But no new data available", verbosityHigh)

                    elif rxData[0] == CLIENT_CMD.CMD_GET_COLUMN_DATA:
                        printLog("Column req by client", verbosityMedium)
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

                        sp = self.spatialPoolers[HTMObjectName]
                        connectedSynapses = numpy.zeros(
                            sp.getNumInputs(), dtype=numpy.int32
                        )
                        sp.getConnectedSynapses(requestedCol, connectedSynapses)

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
                            conn, PackData(SERVER_CMD.SEND_COLUMN_DATA, self.serverData)
                        )

                        printLog(
                            "Sent synapses of len:" + str(len(connectedSynapses)),
                            verbosityHigh,
                        )
                        # printLog("GETTING COLUMN DATA:")
                        # printLog(self.serverData.connectedSynapses)

                    elif rxData[0] == CLIENT_CMD.CMD_RUN:
                        self.runInLoop = True
                        printLog("RUN", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.CMD_STOP:
                        self.runInLoop = False
                        printLog("STOP", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.CMD_STEP_FWD:
                        self.runOneStep = True
                        printLog("STEP", verbosityHigh)
                    elif rxData[0] == CLIENT_CMD.QUIT:
                        printLog("Client quitted!")
                        # quitServer=True
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
