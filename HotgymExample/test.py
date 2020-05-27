from pandaBaker.pandaBakeReader import PandaBakeReader
from pandaBaker.dataStructs import cLayer,cInput

pandaBakeReader = PandaBakeReader('/home/zz/Desktop/test1.db')


pandaBakeReader.OpenDatabase()

pandaBakeReader.BuildStructure()

iteration = 100
pandaBakeReader.LoadActiveColumns('SensoryLayer', iteration)
pandaBakeReader.LoadWinnerCells('SensoryLayer', iteration)
pandaBakeReader.LoadPredictiveCells('SensoryLayer', iteration)
pandaBakeReader.LoadActiveCells('SensoryLayer', iteration)
