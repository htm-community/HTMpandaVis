import csv
import datetime
import os
import numpy as np
import math
import threading
import sys

import socket, pickle
from socket import error as SocketError
from dataExchange import ClientData,ServerData,CLIENT_CMD,SERVER_CMD

from htm.bindings.sdr import SDR, Metrics
from htm.encoders.rdse import RDSE, RDSE_Parameters
from htm.encoders.date import DateEncoder
from htm.bindings.algorithms import SpatialPooler
from htm.bindings.algorithms import TemporalMemory
from htm.algorithms.anomaly_likelihood import AnomalyLikelihood
from htm.bindings.algorithms import Predictor

_EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_INPUT_FILE_PATH = os.path.join(_EXAMPLE_DIR, "gymdata.csv")

default_parameters = {
    # there are 2 (3) encoders: "value" (RDSE) & "time" (DateTime weekend, timeOfDay)
    "enc": {
        "value": {"resolution": 0.88, "size": 700, "sparsity": 0.02},
        "time": {"timeOfDay": (30, 1), "weekend": 21},
    },
    "predictor": {"sdrc_alpha": 0.1},
    "sp": {
        "boostStrength": 3.0,
        "columnCount": 1638,
        "localAreaDensity": 0.04395604395604396,
        "potentialPct": 0.85,
        "synPermActiveInc": 0.04,
        "synPermConnected": 0.13999999999999999,
        "synPermInactiveDec": 0.006,
    },
    "tm": {
        "activationThreshold": 17,
        "cellsPerColumn": 13,
        "initialPerm": 0.21,
        "maxSegmentsPerCell": 128,
        "maxSynapsesPerSegment": 64,
        "minThreshold": 10,
        "newSynapseCount": 32,
        "permanenceDec": 0.1,
        "permanenceInc": 0.1,
    },
    "anomaly": {
        "likelihood": {  #'learningPeriod': int(math.floor(self.probationaryPeriod / 2.0)),
            #'probationaryPeriod': self.probationaryPeriod-default_parameters["anomaly"]["likelihood"]["learningPeriod"],
            "probationaryPct": 0.1,
            "reestimationPeriod": 100,
        }  # These settings are copied from NAB
    },
}


dateBits=None
consumptionBits=None
newDataReadyForVis=False
activeColumns=None
activeCells=None
modelParams=None
timeOfDayString=None
consumption=None

runInLoop=False
runOneStep=False

sp=None

def main(parameters=default_parameters, argv=None, verbose=True):
    global sp
    global dateBits,consumptionBits,activeColumns,activeCells,modelParams
    global runInLoop,runOneStep,newDataReadyForVis,timeOfDayString,consumption
 
    modelParams = parameters
    
    if verbose:
        import pprint

        print("Parameters:")
        pprint.pprint(parameters, indent=4)
        print("")

    # Read the input file.
    records = []
    with open(_INPUT_FILE_PATH, "r") as fin:
        reader = csv.reader(fin)
        headers = next(reader)
        next(reader)
        next(reader)
        for record in reader:
            records.append(record)

    # Make the Encoders.  These will convert input data into binary representations.
    dateEncoder = DateEncoder(
        timeOfDay=parameters["enc"]["time"]["timeOfDay"],
        weekend=parameters["enc"]["time"]["weekend"],
    )

    scalarEncoderParams = RDSE_Parameters()
    scalarEncoderParams.size = parameters["enc"]["value"]["size"]
    scalarEncoderParams.sparsity = parameters["enc"]["value"]["sparsity"]
    scalarEncoderParams.resolution = parameters["enc"]["value"]["resolution"]
    scalarEncoder = RDSE(scalarEncoderParams)
    encodingWidth = dateEncoder.size + scalarEncoder.size
    enc_info = Metrics([encodingWidth], 999999999)

    # Make the HTM.  SpatialPooler & TemporalMemory & associated tools.
    spParams = parameters["sp"]
    sp = SpatialPooler(
        inputDimensions=(encodingWidth,),
        columnDimensions=(spParams["columnCount"],),
        potentialPct=spParams["potentialPct"],
        potentialRadius=encodingWidth,
        globalInhibition=True,
        localAreaDensity=spParams["localAreaDensity"],
        synPermInactiveDec=spParams["synPermInactiveDec"],
        synPermActiveInc=spParams["synPermActiveInc"],
        synPermConnected=spParams["synPermConnected"],
        boostStrength=spParams["boostStrength"],
        wrapAround=True,
    )
    sp_info = Metrics(sp.getColumnDimensions(), 999999999)

    tmParams = parameters["tm"]
    tm = TemporalMemory(
        columnDimensions=(spParams["columnCount"],),
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
    )
    tm_info = Metrics([tm.numberOfCells()], 999999999)

    # setup likelihood, these settings are used in NAB
    anParams = parameters["anomaly"]["likelihood"]
    probationaryPeriod = int(
        math.floor(float(anParams["probationaryPct"]) * len(records))
    )
    learningPeriod = int(math.floor(probationaryPeriod / 2.0))
    anomaly_history = AnomalyLikelihood(
        learningPeriod=learningPeriod,
        estimationSamples=probationaryPeriod - learningPeriod,
        reestimationPeriod=anParams["reestimationPeriod"],
    )

    predictor = Predictor(steps=[1, 5], alpha=parameters["predictor"]["sdrc_alpha"])
    predictor_resolution = 1

    # Iterate through every datum in the dataset, record the inputs & outputs.
    inputs = []
    anomaly = []
    anomalyProb = []
    predictions = {1: [], 5: []}
    for count, record in enumerate(records):

        # Convert date string into Python date object.
        dateString = datetime.datetime.strptime(record[0], "%m/%d/%y %H:%M")
        # Convert data value string into float.
        consumption = float(record[1])
        inputs.append(consumption)

        # Call the encoders to create bit representations for each value.  These are SDR objects.
        dateBits = dateEncoder.encode(dateString)
        consumptionBits = scalarEncoder.encode(consumption)

        # Concatenate all these encodings into one large encoding for Spatial Pooling.
        encoding = SDR(encodingWidth).concatenate([consumptionBits, dateBits])
        enc_info.addData(encoding)

        # Create an SDR to represent active columns, This will be populated by the
        # compute method below. It must have the same dimensions as the Spatial Pooler.
        activeColumns = SDR(sp.getColumnDimensions())

        # Execute Spatial Pooling algorithm over input space.
        sp.compute(encoding, True, activeColumns)
        sp_info.addData(activeColumns)

        # Execute Temporal Memory algorithm over active mini-columns.
        tm.compute(activeColumns, learn=True)
        tm_info.addData(tm.getActiveCells().flatten())
        
        activeCells = tm.getActiveCells()

        # Predict what will happen, and then train the predictor based on what just happened.
        pdf = predictor.infer(count, tm.getActiveCells())
        for n in (1, 5):
            if pdf[n]:
                predictions[n].append(np.argmax(pdf[n]) * predictor_resolution)
            else:
                predictions[n].append(float("nan"))
        predictor.learn(
            count, tm.getActiveCells(), int(consumption / predictor_resolution)
        )

        anomalyLikelihood = anomaly_history.anomalyProbability(consumption, tm.anomaly)
        anomaly.append(tm.anomaly)
        anomalyProb.append(anomalyLikelihood)
        
         #------------------HTMpandaVis----------------------
         
        timeOfDayString = record[0]
        
        if not newDataReadyForVis:
            newDataReadyForVis=True
        
        print("One step finished")
        while(not runInLoop and not runOneStep):
            pass
        runOneStep=False
        print("Proceeding one step...")
      
      #------------------HTMpandaVis----------------------

    # Print information & statistics about the state of the HTM.
    print("Encoded Input", enc_info)
    print("")
    print("Spatial Pooler Mini-Columns", sp_info)
    print(str(sp))
    print("")
    print("Temporal Memory Cells", tm_info)
    print(str(tm))
    print("")

    # Shift the predictions so that they are aligned with the input they predict.
    for n_steps, pred_list in predictions.items():
        for x in range(n_steps):
            pred_list.insert(0, float("nan"))
            pred_list.pop()

    # Calculate the predictive accuracy, Root-Mean-Squared
    accuracy = {1: 0, 5: 0}
    accuracy_samples = {1: 0, 5: 0}
    for idx, inp in enumerate(inputs):
        for (
            n
        ) in predictions:  # For each [N]umber of time steps ahead which was predicted.
            val = predictions[n][idx]
            if not math.isnan(val):
                accuracy[n] += (inp - val) ** 2
                accuracy_samples[n] += 1
    for n in sorted(predictions):
        accuracy[n] = (accuracy[n] / accuracy_samples[n]) ** 0.5
        print("Predictive Error (RMS)", n, "steps ahead:", accuracy[n])

    # Show info about the anomaly (mean & std)
    print("Anomaly Mean", np.mean(anomaly))
    print("Anomaly Std ", np.std(anomaly))

    # Plot the Predictions and Anomalies.
    if verbose:
        try:
            import matplotlib.pyplot as plt
        except:
            print("WARNING: failed to import matplotlib, plots cannot be shown.")
            return -accuracy[5]

        plt.subplot(2, 1, 1)
        plt.title("Predictions")
        plt.xlabel("Time")
        plt.ylabel("Power Consumption")
        plt.plot(
            np.arange(len(inputs)),
            inputs,
            "red",
            np.arange(len(inputs)),
            predictions[1],
            "blue",
            np.arange(len(inputs)),
            predictions[5],
            "green",
        )
        plt.legend(
            labels=(
                "Input",
                "1 Step Prediction, Shifted 1 step",
                "5 Step Prediction, Shifted 5 steps",
            )
        )

        plt.subplot(2, 1, 2)
        plt.title("Anomaly Score")
        plt.xlabel("Time")
        plt.ylabel("Power Consumption")
        inputs = np.array(inputs) / max(inputs)
        plt.plot(
            np.arange(len(inputs)),
            inputs,
            "red",
            np.arange(len(inputs)),
            anomaly,
            "blue",
        )
        plt.legend(labels=("Input", "Anomaly Score"))
        plt.show()

    return -accuracy[5]

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
  serverThread = ServerThread(1, "ServerThread-1")
  
  serverThread.start()

mainThreadQuitted=False

class ServerThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      
   def run(self):
      print ("Starting " + self.name)
      RunServer()
      print ("Exiting " + self.name)
      
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
              serverData.inputs = [dateBits.dense, consumptionBits.dense] # TODO better use sparse
              serverData.activeColumnIndices=activeColumns.sparse
              serverData.activeCells=activeCells
              serverData.columnDimensions=modelParams["sp"]["columnCount"]
              serverData.cellsPerColumn=modelParams["tm"]["cellsPerColumn"]
              serverData.inputsValueString = [timeOfDayString,"consumption: {:.2f}".format(consumption)]
              
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
          print(str(e))
            

          #quitServer=True
        
      
    print("Server quit")
    conn.close()
    
if __name__ == "__main__":    
    try:
        InitServer()
    
        while(True): # run infinitely
          main()    
    
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        mainThreadQuitted=True
