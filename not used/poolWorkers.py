# ---------------- DISTAL SYNAPSES ----------------------------------
           timeStartDistalSynapsesCalc = time.time()
           tm = layer.tm
           if self.bakeDistalSynapses:
               if tm is None:
                   Log("This layer doesn't have TM, can't get distal synapses.. skipping")
                   continue

               columnCount = layer.params['sp_columnCount']
               oneBatchSize = int(columnCount/CPU_CORES)
               split_startColIdx = [x*oneBatchSize for x in range(CPU_CORES)]

               # the division can be with remainder so add to the last thread the rest
               if split_startColIdx[CPU_CORES-1]+oneBatchSize<columnCount-1:
                   remainderCols = columnCount-1 - split_startColIdx[CPU_CORES-1]+oneBatchSize

               # Setup a pool of worker threads equal to CPU_CORES
               with get_context("spawn").Pool(processes=CPU_CORES) as pool:
                   results = [pool.apply_async(CalcPresynCells, args=(layer, split_startColIdx[x],oneBatchSize+(remainderCols if x==CPU_CORES-1 else 0))) for x in range(CPU_CORES)]

                   for result in results:
                       data = result.get()
                       for row in data:
                           self.db.InsertDataArray4('layer_distalSynapses_' + ly,
                                                    iteration, row[0], row[1], row[2], row[3])

               Log("Gathering of distal synapses took took {:.3f} s ".format((time.time() - timeStartDistalSynapsesCalc)))

			
			
			
			
			
			
def CalcPresynCells(layer, startCol, colCount):
    print('process id:', os.getpid())

    tm = layer.tm
    print("Process start for column range:"+str(startCol)+ " - "+str(startCol+colCount))
    output = []
    #cellCnt = 0
    #segmentCnt = 0
    for col in range(startCol, startCol+colCount ):
        for cell in range(layer.params['tm_cellsPerColumn']):
            reqCellID = col * layer.params['tm_cellsPerColumn'] + cell

            # bake distal synapses only for active or predictive cells, about others we don't care, it would take too much time
            if reqCellID in layer.activeCells or reqCellID in layer.predictiveCells:
                # presynCells = getPresynapticCellsForCell(tm, reqCellID)

                segments = tm.connections.segmentsForCell(reqCellID)

                segmentNo = 0
                for seg in segments:  # seg is ID of segments data
                    synapsesForSegment = tm.connections.synapsesForSegment(seg)

                    presynapticCells = []
                    for syn in synapsesForSegment:
                        presynapticCells += [tm.connections.presynapticCellForSynapse(syn)]
                    output += [[col, cell, segmentNo, np.array(presynapticCells)]]
                    segmentNo = segmentNo + 1

                #segmentCnt = segmentCnt + segmentNo
                #cellCnt = cellCnt + 1
                #print("Cell:"+str(cell)+" for col:"+str(col))
    #if not hasSomeOutput:
        #output.put(None) # need to put something, otherwise output.get() hangs forever
    print("Finished")
    return output