# HTMpandaVis

This project aspires to create tool that helps visualize HTM systems in 3D by using opensource framework for 3D rendering https://www.panda3d.org/

It should allow to see architecture of the system in 3D, e.g. connection of layers and inputs and to see input representation,
activity of columns and even individual neurons in each simulation step.
I was inspired by following:
- [HTM school Episode 10 visualization - Topology](https://www.youtube.com/watch?v=HTW2Q_UrkAw&t=688s)
- [Highbrow](https://github.com/htm-community/highbrow)
- [Sanity](https://github.com/htm-community/sanity-nupic) 

The visualization is application written in Python3 and strictly separated from "computation script" by TCP sockets.

Currently the "computation script" is hotgym example using Algorithm API from Nupic extended by
small amout of code to communicate with visualization.

![Diagram](readmeDiagram.png)

