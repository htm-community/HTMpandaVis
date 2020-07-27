from objects.region import cRegion
from objects.minicolumn import cMinicolumn

class cApicalTMPairRegion(cRegion):

    def __init__(self, name, cellData):
        super().__init__(name, cellData)




        for i in range(self.parameters['columnCount']):
            c = cMinicolumn(name, self.parameters['cellsPerColumn'])
            self.minicolumns.append(c)
