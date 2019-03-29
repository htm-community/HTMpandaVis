#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 21:22:17 2019

@author: zz
"""

import csv
import datetime
import numpy
import os
import yaml

#--------------HTMpandaVis
import socket, pickle
import thread
from socket import error as SocketError
import sys
from dataExchange import ClientData,ServerData,CLIENT_CMD,SERVER_CMD
#-------------------------


from nupic.algorithms.sdr_classifier_factory import SDRClassifierFactory
from nupic.algorithms.spatial_pooler import SpatialPooler
from nupic.algorithms.temporal_memory import TemporalMemory
from nupic.encoders.date import DateEncoder
from nupic.encoders.random_distributed_scalar import \
  RandomDistributedScalarEncoder

_NUM_RECORDS = 3000
_EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_INPUT_FILE_PATH = os.path.join(_EXAMPLE_DIR,"gymdata.csv")
_PARAMS_PATH = os.path.join(_EXAMPLE_DIR,"model.yaml")


timeOfDayBits=None
weekendBits=None
consumptionBits=None
newDataReadyForVis=False
activeColumnIndices=None
activeCells=None
modelParams=None
timeOfDayString=None
consumption=None

runInLoop=False
runOneStep=False

sp=None

def runHotgym(numRecords):
  global sp
  global timeOfDayBits,weekendBits,consumptionBits,activeColumnIndices,activeCells,modelParams
  global runInLoop,runOneStep,newDataReadyForVis,timeOfDayString,consumption
  
  with open(_PARAMS_PATH, "r") as f:
    modelParams = yaml.safe_load(f)["modelParams"]
    enParams = modelParams["sensorParams"]["encoders"]
    spParams = modelParams["spParams"]
    tmParams = modelParams["tmParams"]

  timeOfDayEncoder = DateEncoder(
    timeOfDay=enParams["timestamp_timeOfDay"]["timeOfDay"])
  weekendEncoder = DateEncoder(
    weekend=enParams["timestamp_weekend"]["weekend"])
  scalarEncoder = RandomDistributedScalarEncoder(
    enParams["consumption"]["resolution"])

  encodingWidth = (timeOfDayEncoder.getWidth()
                   + weekendEncoder.getWidth()
                   + scalarEncoder.getWidth())

  sp = SpatialPooler(
    inputDimensions=(encodingWidth,),
    columnDimensions=(spParams["columnCount"],),
    potentialPct=spParams["potentialPct"],
    potentialRadius=encodingWidth,
    globalInhibition=spParams["globalInhibition"],
    localAreaDensity=spParams["localAreaDensity"],
    numActiveColumnsPerInhArea=spParams["numActiveColumnsPerInhArea"],
    synPermInactiveDec=spParams["synPermInactiveDec"],
    synPermActiveInc=spParams["synPermActiveInc"],
    synPermConnected=spParams["synPermConnected"],
    boostStrength=spParams["boostStrength"],
    seed=spParams["seed"],
    wrapAround=True
  )

  tm = TemporalMemory(
    columnDimensions=(tmParams["columnCount"],),
    cellsPerColumn=tmParams["cellsPerColumn"],
    activationThreshold=tmParams["activationThreshold"],
    initialPermanence=tmParams["initialPerm"],
    connectedPermanence=spParams["synPermConnected"],
    minThreshold=tmParams["minThreshold"],
    maxNewSynapseCount=tmParams["newSynapseCount"],
    permanenceIncrement=tmParams["permanenceInc"],
    permanenceDecrement=tmParams["permanenceDec"],
    predictedSegmentDecrement=0.0,
    maxSegmentsPerCell=tmParams["maxSegmentsPerCell"],
    maxSynapsesPerSegment=tmParams["maxSynapsesPerSegment"],
    seed=tmParams["seed"]
  )

  classifier = SDRClassifierFactory.create()
  results = []
  
  print("Experiment prepared")
   
  
  with open(_INPUT_FILE_PATH, "r") as fin:
    reader = csv.reader(fin)
    headers = reader.next()
    reader.next()
    reader.next()

    for count, record in enumerate(reader):

      if count >= numRecords: break

      # Convert data string into Python date object.
      dateString = datetime.datetime.strptime(record[0], "%m/%d/%y %H:%M")
      
      timeOfDayString = "time of day: {:02d}:{:02d}".format(dateString.hour,dateString.minute)
      
      # Convert data value string into float.
      consumption = float(record[1])

      # To encode, we need to provide zero-filled numpy arrays for the encoders
      # to populate.
      timeOfDayBits = numpy.zeros(timeOfDayEncoder.getWidth())
      weekendBits = numpy.zeros(weekendEncoder.getWidth())
      consumptionBits = numpy.zeros(scalarEncoder.getWidth())

      # Now we call the encoders to create bit representations for each value.
      timeOfDayEncoder.encodeIntoArray(dateString, timeOfDayBits)
      weekendEncoder.encodeIntoArray(dateString, weekendBits)
      scalarEncoder.encodeIntoArray(consumption, consumptionBits)

      

      # Concatenate all these encodings into one large encoding for Spatial
      # Pooling.
      encoding = numpy.concatenate(
        [timeOfDayBits, weekendBits, consumptionBits]
      )

      # Create an array to represent active columns, all initially zero. This
      # will be populated by the compute method below. It must have the same
      # dimensions as the Spatial Pooler.
      activeColumns = numpy.zeros(spParams["columnCount"])

      # Execute Spatial Pooling algorithm over input space.
      sp.compute(encoding, True, activeColumns)
      activeColumnIndices = numpy.nonzero(activeColumns)[0]

      # Execute Temporal Memory algorithm over active mini-columns.
      tm.compute(activeColumnIndices, learn=True)

      activeCells = tm.getActiveCells()

      # Get the bucket info for this input value for classification.
      bucketIdx = scalarEncoder.getBucketIndices(consumption)[0]

      # Run classifier to translate active cells back to scalar value.
      classifierResult = classifier.compute(
        recordNum=count,
        patternNZ=activeCells,
        classification={
          "bucketIdx": bucketIdx,
          "actValue": consumption
        },
        learn=True,
        infer=True
      )

      # Print the best prediction for 1 step out.
      oneStepConfidence, oneStep = sorted(
        zip(classifierResult[1], classifierResult["actualValues"]),
        reverse=True
      )[0]
      
      #print("1-step: {:16} ({:4.4}%)".format(oneStep, oneStepConfidence * 100))
      
      results.append([oneStep, oneStepConfidence * 100, None, None])

      #------------------HTMpandaVis----------------------
      if not newDataReadyForVis:
        newDataReadyForVis=True
        
      print("One step finished")
      while(not runInLoop and not runOneStep):
        pass
      runOneStep=False
      print("Proceeding one step...")
      
      #------------------HTMpandaVis----------------------
      
    return results
 
    
def PackData(cmd,data):
  d = [cmd,data]
  # Pickle the object and send it to the server
  #protocol must be specified to be able to work with py2 on server side
  rawData = pickle.dumps(d,protocol=2)
  
  if len(rawData)%4096==0:#if length of data is multiple of chunck size
    #increase the data by 1 byte to prevent it - it causes problems in recv function
    #on the client side - because client doesn't know how long data to expect
    if isinstance(data,ServerData):
      data.compensateSize.append(1)#increase size by some dummy bytes
      d = [cmd,data]
      rawData = pickle.dumps(d,protocol=2)
    else:
      print("Packed data is multiple of chunck size, but not known instance")
  
  return rawData

  
def InitServer():
  thread.start_new_thread( RunServer, () )

mainThreadQuitted=False

def RunServer():
    global runInLoop,runOneStep,newDataReadyForVis
 
    HOST = 'localhost'
    PORT = 50007
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#prevent "adress in use" exception
    s.settimeout(5)
    s.bind((HOST, PORT))
    s.listen(1)
    
    print("Server listening")
    
    clientConnected=False
    
    while(not clientConnected and not mainThreadQuitted):
      try:
        conn, addr = s.accept()
        conn.settimeout(5)
        print('Connected by'+str(addr))
        clientConnected=True
      except socket.timeout:
        continue
    
      if not clientConnected:
        print("Main thread quitted")
        return
    
      quitServer=False
      
      while(not quitServer and not mainThreadQuitted):
        try:
          rxRawData = conn.recv(4096)
          
          rxData = pickle.loads(rxRawData)
          
          if (rxData[0] == CLIENT_CMD.REQ_DATA):
            #print("Data requested")
            if newDataReadyForVis:  
              
              serverData = ServerData()
              serverData.inputs = [timeOfDayBits,weekendBits,consumptionBits]
              serverData.activeColumnIndices=activeColumnIndices
              serverData.activeCells=activeCells
              serverData.columnDimensions=modelParams["spParams"]["columnCount"]
              serverData.cellsPerColumn=modelParams["tmParams"]["cellsPerColumn"]
              serverData.inputsValueString = [timeOfDayString,"Weekend?","consumption: {:.2f}".format(consumption)]
              
              #print("Data sent")
              
              conn.send(PackData(SERVER_CMD.SEND_DATA,serverData))
              
              newDataReadyForVis = False
            else:
              conn.send(PackData(SERVER_CMD.NA,[]))#we dont have any new data for client
              
          elif (rxData[0] == CLIENT_CMD.CMD_GET_COLUMN_DATA):
            connectedSynapses = numpy.zeros(sum([len(x) for x in serverData.inputs]))#sum size of all inputs
            sp.getConnectedSynapses(1,connectedSynapses)
            
            
            serverData = ServerData()
            serverData.connectedSynapses = connectedSynapses
            conn.send(PackData(SERVER_CMD.SEND_COLUMN_DATA,serverData))
            
            print("GETTING COLUMN DATA:")
            print(connectedSynapses)
            
            
          elif (rxData[0] == CLIENT_CMD.CMD_RUN):
            runInLoop = True
            print("RUN")
          elif (rxData[0] == CLIENT_CMD.CMD_STOP):
            runInLoop = False
            print("STOP")
          elif (rxData[0] == CLIENT_CMD.CMD_STEP_FWD):
            runOneStep = True
            print("STEP")
          elif (rxData[0] == CLIENT_CMD.QUIT):
            print("Client quitted!")  
            #quitServer=True
        except socket.timeout:
          continue
        except SocketError as e:
          print("SocketError")
          print(e)
          clientConnected=False
          break
        except EOFError:
          print("EOFError")
          clientConnected=False
          break
        except Exception as e:
          print("Exception"+str(sys.exc_info()[0]))
          print(str(e.message))
            

          #quitServer=True
        
      
    print("Server quit")
    conn.close()


if __name__ == "__main__":
    
  try:
    InitServer()
    
    while(True): # run infinitely
      runHotgym(_NUM_RECORDS)    
    
  except KeyboardInterrupt:
    print("Keyboard interrupt")
    mainThreadQuitted=True