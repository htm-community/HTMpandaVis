## Baking
Baking is the process of creating data for vizualization.

Basically, SQLite3 dabase file is filled in and also binary dumps of synapses are created.

PandaVis uses NetworkAPI to get everything it needs.

User can create custom datastreams to record them and show in dash 'plot' visualization in web browser.

## Setup datastreams for dash visualization:

setup callback for filling values each iteration
```
# data for dash plots
self.network.network.updateDataStreams = self.updateDataStreams
```

create method for example like this and fill actual values to your custom datastreams that you want to visualize with plots in web browser
```
def updateDataStreams(self):
          # for first column
          col = 0
          self.network.network.UpdateDataStream("L4PredictedCellCnt", len(self.network.getL4PredictedCells()[col]))
          self.network.network.UpdateDataStream("L4ActiveCellCnt", len(self.network.getL4Representations()[col]))
          self.network.network.UpdateDataStream("L6ActiveCellCnt", len(self.network.getL6aRepresentations()[col]))
```

See hotgym example for more informations
