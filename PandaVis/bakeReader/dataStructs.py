# -*- coding: utf-8 -*-
import numpy as np
import json

# structs for easier manipulation with data from database
class cLinkData:
    def __init__(self, sourceRegion, sourceOutput, destinationRegion, destinationInput):
        self.sourceRegion = sourceRegion
        self.sourceOutput = sourceOutput
        self.destinationRegion = destinationRegion
        self.destinationInput = destinationInput

class cRegionData:
    def __init__(self, type, parameters):
        self.type = type
        self.parameters = json.loads(json.loads(parameters))  # must parse it twice, because sqlite adds backslashes like \\n and \\"

        # dict containing data like "activeCells", "predictiveCells" etc.. these corresponds to region outputs
        self.data = {}  # if empty, it contains np.empty(0)

        # contains connections accessible by column
        # {
        #   connType:[
        #       [col1,
        #           [[seg0_cell0,seg0_cell1...],[seg1_cell0,seg1_cell1...],...],
        #          ...
        #       ],
        #       [col2,
        #           [[seg0_cell0,seg0_cell1...],[seg1_cell0,seg1_cell1...],...],
        #           ...
        #       ]
        #       ...
        #   ],
        #   connType2:
        #       ....
        #   ]
        # }
        self.columnConnections = {}

        # contains connections accessible by individual cells
        # same as above, but instead col1 and col2 there is cell1 and cell2
        self.cellConnections = {}

class cDataStream(object):
    def __init__(self, dataType="REAL"):
        self.dataType = dataType
        self.value = None


