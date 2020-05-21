#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
)  # adds parent directory to path

import socket, pickle, struct
import _thread
import time
from PandaVis.pandaComm.dataExchange import ServerData, CLIENT_CMD, SERVER_CMD


verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityHigh
)  # change this to change printing verbosity of this file
SLOW_DEBUG = False


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)


def PackData(cmd, data=[]):
    d = [cmd, data]
    # Pickle the object and send it to the server
    # protocol must be specified to be able to work with py2 on server side
    rawData = pickle.dumps(d, protocol=2)

    if len(rawData) % 4096 == 0:  # if length of data is multiple of chunk size
        # increase the data by 1 byte to prevent it - it causes problems in recv function
        # on the client side - because client doesn't know how long data to expect
        if isinstance(data, ServerData):
            data.compensateSize.append(1)  # increase size by some dummy bytes
            d = [cmd, data]
            rawData = pickle.dumps(d)  # , protocol=2)
        else:
            printLog("Packed data is multiple of chunk size, but not known instance")

    return rawData


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack("!I", length))
    sock.sendall(data)


def recv_one_message(sock):
    buffer = sock.recv(4)
    if len(buffer)!=4:
        raise BrokenPipeError("Size of sock.recv was not 4 bytes!");
    length, = struct.unpack("!I", buffer)
    return sock.recv(length)


class SocketClient:
    def __init__(self):

        _thread.start_new_thread(self.RunThread, ())

        self.serverData = None
        self.terminateClientThread = False
        
        self.stateDataArrived = False
        self.proximalDataArrived = False
        self.distalDataArrived = False
        
        self._reqProximalData = False
        self._reqDistalData = False

        self._gui = None

        self.HOST = "localhost"
        self.PORT = 50007

        self.socket = None
        self.connected = False

        self.tmrReq = 0

    def setGui(self, gui):
        self._gui = gui

    def reqProximalData(self):
        self._reqProximalData=True
    def reqDistalData(self):
        self._reqDistalData=True
            
    def RunThread(self):

        # Create a socket connection, keep trying if no success
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.connected = False

        # s.send(SocketClient.PackData(CLIENT_CMD.REQ_DATA))
        while not self.terminateClientThread:

            if not self.connected:#try to reconnect each time (if server fails it can be restarted)
                self.ConnectToServer()

            try:
               # if time.time() - self.tmrReq > 1: # each 1 sec make request
                printLog("Sending REQ", verbosityMedium)
                send_one_message(self.socket, PackData(CLIENT_CMD.CMD_GET_STATE_DATA))
                    #self.tmrReq = time.time()

                if self._gui.cmdRun:
                    send_one_message(self.socket, PackData(CLIENT_CMD.CMD_RUN))
                    printLog("RUN req", verbosityMedium)
                elif self._gui.cmdStop:
                    send_one_message(self.socket, PackData(CLIENT_CMD.CMD_STOP))
                    printLog("STOP req", verbosityMedium)
                elif self._gui.gotoReq >= 0:
                    send_one_message(self.socket, PackData(CLIENT_CMD.CMD_GOTO, self._gui.gotoReq))
                    printLog("GOTO req", verbosityMedium)
                    self._gui.gotoReq = -1
                elif self._gui.cmdStepForward:
                    send_one_message(self.socket, PackData(CLIENT_CMD.CMD_STEP_FWD))
                    printLog("STEP", verbosityMedium)
                elif self._reqProximalData:
                    self._reqProximalData=False
                    send_one_message(
                        self.socket,
                        PackData(
                            CLIENT_CMD.CMD_GET_PROXIMAL_DATA,
                            [self._gui.focusedPath, self._gui.columnID],
                        ),
                    )
                    printLog(
                        "GET proximal data for col:" + str(self._gui.focusedCell.column),
                        verbosityMedium,
                    )
                elif self._reqDistalData:
                    self._reqDistalData=False
                    send_one_message(
                        self.socket,
                        PackData(
                            CLIENT_CMD.CMD_GET_DISTAL_DATA,
                            [self._gui.focusedPath, self._gui.columnID, self._gui.cellID],
                        ),
                    )
                    printLog(
                        "GET distal for cell: " + str(self._gui.cellID) + " on column: "+str(self._gui.columnID),
                        verbosityMedium,
                    )

                self._gui.ResetCommands()

                printLog("Data begin receiving", verbosityHigh)
                self.ReceiveData(self.socket)
                printLog("Data received", verbosityHigh)

            except (ConnectionResetError, BrokenPipeError):
                printLog("Connection was reset, probably by server side.")
                self.connected = False
                continue

        # send that we as a client are quitting
        if self.connected:
            send_one_message(self.socket, PackData(CLIENT_CMD.QUIT))

        self.socket.close()
        printLog("ClientThread terminated")

    def ConnectToServer(self):
        printLog("Continuously trying connect to server...")
        while not self.connected:
            try:
                try:
                    self.socket.connect((self.HOST, self.PORT))
                    self.connected = True
                except (TimeoutError,ConnectionRefusedError, ConnectionAbortedError):
                    time.sleep(1)
                    continue
            except Exception as e:
                printLog("Exception while trying connect to server:")
                printLog(str(e))
                time.sleep(5)
                continue

        printLog("Connected to server:" + self.HOST + ":" + str(self.PORT), verbosityLow)

    def ReceiveData(self, s):

        # wait till the previous data is processed! (in the Update() thread)
        while self.stateDataArrived or self.proximalDataArrived or self.distalDataArrived:
            continue

        rxRawData = b""

        try:
            rxRawData = recv_one_message(s)

            printLog("lenRaw:" + str(len(rxRawData)), verbosityHigh)
            #printLog(rxRawData, verbosityHigh)

            if len(rxRawData) == 0:
                printLog("Received data are empty!", verbosityHigh)
                return
            rxData = pickle.loads(rxRawData, encoding="latin1")

            printLog("lenRx:" + str(len(rxData)), verbosityHigh)

            printLog("RCV ID:" + str(rxData[0]), verbosityHigh)
            if len(rxData) > 1:
                printLog("RCV data:" + str(rxData[1]), verbosityHigh)



            if rxData[0] == SERVER_CMD.SEND_STATE_DATA:
                self.serverData = rxData[1]
                self.stateDataArrived = True
                printLog("Data income", verbosityMedium)

            elif rxData[0] == SERVER_CMD.SEND_PROXIMAL_DATA:
                self.serverData = rxData[1]
                self.proximalDataArrived = True
                printLog("proximal data arrived", verbosityMedium)

            elif rxData[0] == SERVER_CMD.SEND_DISTAL_DATA:
                self.serverData = rxData[1]
                self.distalDataArrived = True
                printLog("distal data arrived", verbosityMedium)
            

            elif rxData[0] == SERVER_CMD.NA:
                printLog("Server has data not available", verbosityHigh)
                if SLOW_DEBUG:
                    time.sleep(1)
            else:
                printLog("Unknown command:" + str(rxData[0]))

        except socket.timeout:
            printLog("SocketTimeout", verbosityHigh)
            return
