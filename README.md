# HTMpandaVis
**See presentation [video](https://youtu.be/c1aJq0p-9uY)!**

Screenshots for visualization of the "hotgym" example
![img1](img1.png)
![img2](img2.png)
![img2](img3.png)

This project aspires to create tool that helps **visualize HTM systems in 3D** by using opensource framework for 3D rendering https://www.panda3d.org/

It should allow to see architecture of the system in 3D, e.g. connection of several layers and inputs and to see input representation,
activity of columns and even individual cells in each simulation step.
User can observe vast scalable space by moving as "ghost" and interact with objects.
It is supposed as tool for educational purpose or as an inspect tool.

I was inspired by following:
- [HTM school Episode 10 visualization - Topology](https://www.youtube.com/watch?v=HTW2Q_UrkAw&t=688s)
- [Highbrow](https://github.com/htm-community/highbrow)
- [Sanity](https://github.com/htm-community/sanity-nupic) 

The visualization is application written in Python3 and strictly separated from "computation script" by TCP sockets.

Currently the "computation script" is hotgym example using [htm.core](https://github.com/htm-community/htm.core) extended by
small amout of code to communicate with visualization.
That is also main idea, anybody can take his own current computation script, slightly modify it and use this vis tool.

![Diagram](readmeDiagram.png)


# How to install on Linux

Python >3.6 is recommended.
Also using one of the python environment managers is recommended,
like [Anaconda](https://www.anaconda.com/distribution/)

Install htm.core (here building from source, see [repo readme](https://github.com/htm-community/htm.core) if you need other installation instructions)
```
sudo apt-get install cmake
git clone https://github.com/htm-community/htm.core.git
python3 setup.py install --user --force
```

Install prerequisities & clone pandaVis
```
sudo apt-get install python3-tk

python3 -m pip install -r requirements.txt

git clone https://github.com/htm-community/HTMpandaVis.git
```
# How to run

Run server - example "hotgym"
```
cd HTMpandaVis/HotgymExample
python3 hotgym.py
```

Run client - pandaVis tool
```
cd HTMpandaVis/PandaVis
python3 pandaVis.py
```

# How to use with your computation script
1. **import packages for pandaVis**
```
from pandaComm.pandaServer import PandaServer
from pandaComm.dataExchange import ServerData, dataHTMObject, dataLayer, dataInput
```
2. **Create pandaServer intance and start it at init of your script**
```
pandaServer = PandaServer() # globally for example

#in init phase of your script
pandaServer.Start()
BuildPandaSystem()
```
3. **Announce that script finished**

Call this method when your script is terminated. Needed to ensure that threads in pandaServer and the client itself are quit properly.
```
pandaServer.MainThreadQuitted()
```
4. **Build your HTM system**

There is need to specify what is your HTM system architecture. It is simple done by using python dicts like following:
```
def BuildPandaSystem():
    global serverData
    serverData = ServerData()
    serverData.HTMObjects["HTM1"] = dataHTMObject()
    serverData.HTMObjects["HTM1"].inputs["SL_Consumption"] = dataInput()
    serverData.HTMObjects["HTM1"].inputs["SL_TimeOfDay"] = dataInput()

    serverData.HTMObjects["HTM1"].layers["SensoryLayer"] = dataLayer(
        default_parameters["sp"]["columnCount"],
        default_parameters["tm"]["cellsPerColumn"],
    )
    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].proximalInputs = [
        "SL_Consumption",
        "SL_TimeOfDay",
    ]
```
This means that we have 1 *HTM object* containing one *SensoryLayer* and two inputs *SL_Consumption* and *SL_TimeOfDay* connected to layer as proximal inputs.

5. **Update values each cycle**

Fill in values that you want to visualize in each execution cycle, like:
```
serverData.HTMObjects["HTM1"].inputs["SL_Consumption"].stringValue = "consumption: {:.2f}".format(consumption)
serverData.HTMObjects["HTM1"].inputs["SL_Consumption"].bits = consumptionBits.sparse
serverData.HTMObjects["HTM1"].inputs["SL_Consumption"].count = consumptionBits.size
# and so on for other objects....

pandaServer.NewStateDataReady()# say to pandaServer that it has new data
```
6. **Block your execution like following, if you want to control the run/stepping from pandaVis**
```
while not pandaServer.runInLoop and not pandaServer.runOneStep:
    pass
pandaServer.runOneStep = False
```
See example in "HotgymExample" folder for implementation.
Also see "/pandaComm/dataExchange.py" file for details what can be sent to client.
