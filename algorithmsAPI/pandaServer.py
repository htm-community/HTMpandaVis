#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:22:19 2019

@author: osboxes
"""

import socket, pickle
from socket import error as SocketError
import threading
import sys
from dataExchange import ServerData, CLIENT_CMD, SERVER_CMD
import numpy
from htm.bindings.algorithms import SpatialPooler
from htm.bindings.algorithms import TemporalMemory

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
            rawData = pickle.dumps(d, protocol=2)
        else:
            print("Packed data is multiple of chunck size, but not known instance")

    return rawData


class PandaServer:
    def __init__(self):
        self.serverData = ServerData() 
        self.runOneStep = False
        self.runInLoop = False
        self.newDataReadyForVis = False
        self.mainThreadQuitted = False
        
        self.serverThread = ServerThread(self,1, "ServerThread-1")
        
        self.sp = None
        self.tm = None
        
    def Start(self):
        self.serverThread.start()

    def MainThreadQuitted(self):#if the parent thread is terminated, end this one too
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
    
        print("Server listening")
    
        clientConnected = False
    
        while not clientConnected and not self.mainThreadQuitted:
            try:
                conn, addr = s.accept()
                conn.settimeout(5)
                print("Connected by" + str(addr))
                clientConnected = True
            except socket.timeout:
                continue
    
            if not clientConnected:
                print("Client is not connected anymore")
                return
    
            quitServer = False
    
            while not quitServer and not self.mainThreadQuitted:
                try:
                    rxRawData = conn.recv(4096)
    
                    rxData = pickle.loads(rxRawData)
    
                    if rxData[0] == CLIENT_CMD.REQ_DATA:
                        #print("Data requested")
                        if self.newDataReadyForVis:
    
                            conn.send(PackData(SERVER_CMD.SEND_DATA, self.serverData))
    
                            self.newDataReadyForVis = False
                        else:
                            conn.send(
                                PackData(SERVER_CMD.NA, [])
                            )  # we dont have any new data for client
    
                    elif rxData[0] == CLIENT_CMD.CMD_GET_COLUMN_DATA:
                        print("column data")
                        connectedSynapses = numpy.zeros(
                            sum([len(x) for x in self.serverData.inputs]), dtype=numpy.int32
                        )  # sum size of all inputs
                        self.sp.getConnectedSynapses(1, connectedSynapses)
    
                        serverData = ServerData()
                        serverData.connectedSynapses = connectedSynapses
                        conn.send(PackData(SERVER_CMD.SEND_COLUMN_DATA, serverData))
    
                        print("GETTING COLUMN DATA:")
                        print(connectedSynapses)
    
                    elif rxData[0] == CLIENT_CMD.CMD_RUN:
                        self.runInLoop = True
                        print("RUN")
                    elif rxData[0] == CLIENT_CMD.CMD_STOP:
                        self.runInLoop = False
                        print("STOP")
                    elif rxData[0] == CLIENT_CMD.CMD_STEP_FWD:
                        self.runOneStep = True
                        print("STEP")
                    elif rxData[0] == CLIENT_CMD.QUIT:
                        print("Client quitted!")
                        # quitServer=True
                except socket.timeout:
                    continue
                except SocketError as e:
                    print("SocketError")
                    print(e)
                    clientConnected = False
                    break
                except EOFError:
                    print("EOFError")
                    clientConnected = False
                    break
                except Exception as e:
                    print("Exception" + str(sys.exc_info()[0]))
                    print(str(e))
    
                    # quitServer=True
    
        print("Server quit")
        conn.close()

class ServerThread(threading.Thread):
    def __init__(self,serverInstance, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.serverInstance = serverInstance
		
    def run(self):
        print("Starting " + self.name)
        self.serverInstance.RunServer()
        print("Exiting " + self.name)



