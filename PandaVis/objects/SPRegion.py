from objects.region import cRegion
from objects.cell import cCell

class cSPRegion(cRegion):

    def __init__(self, name, cellData, gui, unifiedWithTMRegion=False):
        super().__init__(name, cellData, gui)

        self.columnCount = self.parameters["columnCount"]
        self.unifiedWithTMRegion = unifiedWithTMRegion

        # if Spatial pooler exists at his own - does not have any minicolumns of other region to operate on
        if not unifiedWithTMRegion:
            self.cells = []

            for i in range(self.columnCount): # taking SP "minicolumns" as cells in 3D space
                c = cCell(None)
                self.cells.append(c)

            self.subObjects = self.cells

        self.COL_OFFSET = 0.4  # space between cells

        self.SUBOBJ_DISTANCE_X = 2 + self.COL_OFFSET
        self.SUBOBJ_DISTANCE_Y = 1 + self.COL_OFFSET


    def SetUnifiedTMRegion(self, region):
        print("Setting link for unification: SPregion -> "+region)
        self.unifiedTMRegion = region

    def getVerticalSize(self):
        return 1

    def UpdateState(self, regionData):
        super().UpdateState(regionData)
