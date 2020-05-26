from pandaBaker.pandaBakeReader import PandaBakeReader
from pandaBaker.dataStructs import cHTMObject,cLayer,cInput

pandaBakeReader = PandaBakeReader("C:\\Users\\43010600\\Desktop\\test1.db")

##pandaBaker.HTMObjects["HTM1"] = cHTMObject()
##pandaBaker.HTMObjects["HTM1"].inputs["SL_Consumption"] = cInput(10)
##pandaBaker.HTMObjects["HTM1"].inputs["SL_TimeOfDay"] = cInput(10)
##
##pandaBaker.HTMObjects["HTM1"].layers["SensoryLayer"] = cLayer(None,None)
##pandaBaker.HTMObjects["HTM1"].layers["SensoryLayer"].proximalInputs = [
##    "SL_Consumption",
##    "SL_TimeOfDay",
##]
##
##pandaBaker.PrepareDatabase()
    
pandaBakeReader.OpenDatabase()
print(pandaBakeReader.db.getTableNames())
