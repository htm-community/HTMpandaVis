from .region import cRegion
from objects.cell import cCell


class cRawValuesRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)


  def getVerticalSize(self):
    return 2

  def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
    super().UpdateState(regionData)

