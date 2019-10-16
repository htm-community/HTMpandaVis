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

Install htm.core (here building from source, see [repo readme](https://github.com/htm-community/htm.core) for other installation instructions)
```
sudo apt-get install cmake
git clone https://github.com/htm-community/htm.core.git
python3 setup.py install --user --force
```

Install prerequisities & clone pandaVis
```
python3 -m pip install numpy
python3 -m pip install matplotlib
python3 -m pip install panda3d
python3 -m pip install pysimplegui 

(sudo apt-get install python3-tk - this is probably not needed, not sure)

git clone https://github.com/Zbysekz/HTMpandaVis.git
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
