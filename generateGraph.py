import pyyed
import sys
import os
sys.path.append(os.path.join(os.getcwd(),'PandaVis'))# to make the bakeReader imports work
from PandaVis.bakeReader.bakeReader import BakeReader

reader = BakeReader('/media/D/Data/HTM/htm-2d-object-modeling/python/bakedDatabase/pandaVis.db')

reader.OpenDatabase()

regions, links = reader.LoadStructure()

g = pyyed.Graph()

for regName, regType in regions.items():
    g.add_node(regName, shape="roundrectangle")


for linkId, linkData in links.items():

    g.add_edge(linkData[0], linkData[2], label=linkData[1]+' -> '+ linkData[3], width="3.0", color="#0000FF",
               )

print(g.get_graph())

# To write to file:
with open('test_graph.graphml', 'w') as fp:
    fp.write(g.get_graph())

# Or:
g.write_graph('example.graphml')

# Or, to pretty-print with whitespace:
g.write_graph('pretty_example.graphml', pretty_print=True)