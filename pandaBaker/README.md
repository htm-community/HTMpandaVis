## Baking
Baking is the process of creating data for vizualization.

Basically, SQLite3 dabase file is filled in and also binary dump of distal synapases is created.

There are these python classes for storing data:
* cInput
* cLayer
* cDataStream

cInput -> SDR input to the system
cLayer -> this represents layer with cells & minicolumns, with or without SP and TM algorithms applied
cDataStream -> object for storing scalar data, for purpose of plot "Dash vizualization" (plots in web browser on localhost)

## Setup the system:
- add inputs
```
pandaBaker.inputs["myInputName1"] = cInput(inputSize)
...
```
- add layers and connect proximal/distal inputs to it
```
pandaBaker.layers["myLayerName"] = cInput(inputSize)
pandaBaker.layers["myLayerName"].proximalInputs = [
          "myInputName1",
          "myInputName2",
      ]
pandaBaker.layers["myLayerName"].distalInputs = [
          "myInputName1"
      ]      
...
```

- add custom data streams
```
pandaBaker.dataStreams["myStreamName1"] = cDataStream()
pandaBaker.dataStreams["myStreamName2"] = cDataStream()
...
```

## Fill in values each iteration

Like this:
```
pandaBaker.inputs["myInputName1"].stringValue = str(ts)
pandaBaker.inputs["myInputName1"].bits = dateBits.sparse

pandaBaker.layers["myLayerName"].activeColumns = activeColumns.sparse
pandaBaker.layers["myLayerName"].winnerCells = self.tm.getWinnerCells().sparse
pandaBaker.layers["myLayerName"].predictiveCells = predictiveCells.sparse
pandaBaker.layers["myLayerName"].activeCells = self.tm.getActiveCells().sparse

pandaBaker.dataStreams["myStreamName1"].value = temporalAnomaly
pandaBaker.dataStreams["myStreamName2"].value = val

```

See hotgym example for more informations
