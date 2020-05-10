#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from objects.minicolumn import cMinicolumn
from panda3d.core import NodePath, PandaNode, TextNode

class cLayer:
    ONE_ROW_SIZE = 150
    MAX_CREATED_COL_PER_CYCLE = 50

    def __init__(self, name, nOfColumns, nOfCellsPerColumn):

        self.name = name
        self.nOfCellsPerColumn = nOfCellsPerColumn
        self.minicolumns = []
        for i in range(nOfColumns):
            c = cMinicolumn(name, nOfCellsPerColumn)
            self.minicolumns.append(c)

        # for creation of GFX
        self.offset_y = 0
        self.offset_idx = 0
        self.offset_row = 0
        self.loader = None
        self.gfxCreationFinished = False

    def CreateGfx(self, loader):

        self.__node = NodePath(
            PandaNode(self.name)
        )  # TextNode('layerText')#loader.loadModel("models/teapot")

        self.text = TextNode("Layer text node")
        self.text.setText(self.name)

        textNodePath = self.__node.attachNewNode(self.text)
        textNodePath.setScale(5)

        textNodePath.setPos(0, -5, 0)

        self.__node.setPos(0, 0, 0)
        self.__node.setScale(1, 1, 1)

        self.loader = loader
        self.offset_y = 0
        self.offset_idx = 0
        self.offset_row = 0


    def CreateGfxProgressively(self):
        createdCols = 0
        currentlyCreatedCols = 0
        allFinished = True
        for c in self.minicolumns:
            if not c.gfxCreated:
                c.CreateGfx(self.loader, self.offset_idx)
                self.offset_idx += 1
                c.getNode().setPos(self.offset_row * 10, self.offset_y, 0)
                self.offset_y += 3

                if self.offset_y > cLayer.ONE_ROW_SIZE:
                    self.offset_y = 0
                    self.offset_row += 1
                c.getNode().reparentTo(self.__node)
                c.gfxCreated = True
                currentlyCreatedCols += 1

                if currentlyCreatedCols >= cLayer.MAX_CREATED_COL_PER_CYCLE:
                    allFinished = False
                    break
            else:
                createdCols += 1

        if allFinished:
            if not self.gfxCreationFinished:
                self.gfxCreationFinished = True
                self.text.setText(self.name)
        else:
            self.text.setText(self.name+"(creating:"+str(int(100*createdCols/len(self.minicolumns)))+" %)")

    def UpdateState(self, activeColumns, activeCells, winnerCells, predictiveCells, newStep = False, showPredictionCorrectness = False, showBursting = False):

        # print("COLUMNS SIZE:"+str(len(self.minicolumns)))
        #print("winners:"+str(winnerCells))
        #print("predictive:"+str(predictiveCells))
        
        for colID in range(len(self.minicolumns)):# go through all columns
            oneOfCellPredictive=False
            oneOfCellCorrectlyPredicted = False
            oneOfCellFalselyPredicted = False
            nOfActiveCells = 0

            for cellID in range(len(self.minicolumns[colID].cells)): # for each cell in column
                isActive = cellID+(colID*self.nOfCellsPerColumn) in activeCells
                isWinner = cellID + (colID * self.nOfCellsPerColumn) in winnerCells
                isPredictive = cellID+(colID*self.nOfCellsPerColumn) in predictiveCells

                if isPredictive:
                    oneOfCellPredictive=True

                if isActive:
                    nOfActiveCells = nOfActiveCells + 1


                self.minicolumns[colID].cells[cellID].UpdateState(active = isActive, predictive = isPredictive,winner = isWinner, newStep=newStep, showPredictionCorrectness = showPredictionCorrectness)

                if showPredictionCorrectness:
                    #get correct/false prediction info
                    if self.minicolumns[colID].cells[cellID].correctlyPredicted:
                        oneOfCellCorrectlyPredicted = True

                    if self.minicolumns[colID].cells[cellID].falselyPredicted:
                        oneOfCellFalselyPredicted = True

            if showBursting:
                bursting = nOfActiveCells == self.nOfCellsPerColumn #if all cells in column are active -> the column is bursting
            else:
                bursting = False

            self.minicolumns[colID].UpdateState(bursting=bursting, activeColumn = colID in activeColumns, oneOfCellPredictive=oneOfCellPredictive,
                                                    oneOfCellCorrectlyPredicted=oneOfCellCorrectlyPredicted, oneOfCellFalselyPredicted=oneOfCellFalselyPredicted)
        
        
#        for cellID in winnerCells:
#            self.minicolumns[(int)(cellID/self.nOfCellsPerColumn)].cells[(int)(cellID%self.nOfCellsPerColumn)].UpdateState(active = True, predictive = False)
#        
#        for cellID in predictiveCells:
#            self.minicolumns[(int)(cellID/self.nOfCellsPerColumn)].cells[(int)(cellID%self.nOfCellsPerColumn)].UpdateState(active = True, predictive = True)
        

    def updateWireframe(self, value):
        for col in self.minicolumns:
            col.updateWireframe(value)
            
    def getNode(self):
        return self.__node

    def DestroyProximalSynapses(self):
        for col in self.minicolumns:
            col.DestroyProximalSynapses()
    
    def DestroyDistalSynapses(self):
        for col in self.minicolumns:
            col.DestroyDistalSynapses()
            
    def setTransparency(self,transparency):
        self.transparency = transparency
        for col in self.minicolumns:
            col.setTransparency(transparency)

    def LODUpdateSwitch(self, lodDistance, lodDistance2):
        for col in self.minicolumns:
            col.LODUpdateSwitch(lodDistance, lodDistance2)