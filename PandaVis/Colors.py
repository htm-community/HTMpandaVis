from panda3d.core import LColor


COL_SEPARATOR = LColor(0.0, 0.0, 0.0, 0.0)#none

COL_CELL_ACTIVE = LColor(1.0, 0.0, 0.0, 1.0)#red
COL_CELL_PREDICTIVE = LColor(0.0, 0.0, 1.0, 1.0)#blue
COL_CELL_WINNER = LColor(1.0, 0.5, 0.0, 1.0)#orange
COL_CELL_ACTIVE_AND_PREDICTIVE = LColor(1.0, 0.0, 1.0, 1.0)#violet
COL_CELL_FOCUSED = LColor(1.0, 1.0, 0.0, 1.0) # yellow
COL_CELL_INACTIVE = LColor(1.0, 1.0, 1.0, 1.0)#white
COL_CELL_CORRECTLY_PREDICTED = LColor(0.0, 1.0, 0.0, 1.0)#green
COL_CELL_FALSELY_PREDICTED = LColor(1.0, 0.7, 0.7, 1.0)#pink
COL_CELL_PRESYNAPTIC_FOCUS = LColor(0.5, 0.8, 1.0, 1.0)# bright blue

COL_COLUMN_ACTIVE = LColor(1.0, 0.0, 0.0, 1.0) # red
COL_COLUMN_BURSTING = LColor(0.8, 1.0, 0.0, 1.0) # yellow-green
COL_COLUMN_ONEOFCELLCORRECTLY_PREDICTED = LColor(0.0, 1.0, 0.0, 1.0) # green
COL_COLUMN_ONEOFCELLFALSELY_PREDICTED = LColor(1.0, 0.7, 0.7, 1.0)#pink

COL_COLUMN_ONEOFCELLPREDICTIVE = LColor(0.0, 0.0, 1.0, 1.0) # blue
COL_COLUMN_ACTIVE_AND_ONEOFCELLPREDICTIVE = LColor(1.0, 0.0, 1.0, 1.0)#violet
COL_COLUMN_INACTIVE = LColor(1.0, 1.0, 1.0, 1.0) # white

COL_PROXIMAL_SYNAPSES_INACTIVE = LColor(1.0, 1.0, 1.0, 1.0)#white
COL_PROXIMAL_SYNAPSES_ACTIVE = LColor(0.0, 0.6, 0.0, 1.0)#lime
COL_DISTAL_SYNAPSES_ACTIVE = LColor(1.0, 0.0, 1.0, 1.0)#purple
COL_DISTAL_SYNAPSES_INACTIVE = LColor(0.2, 0.2, 1.0, 1.0)#blue


IN_BIT_FOCUSED = LColor(1.0, 1.0, 0.0, 1.0) # yellow
IN_BIT_ACTIVE = LColor(0.0, 1.0, 0.0, 1.0)#green
IN_BIT_OVERLAPPING  = LColor(1.0, 0.0, 0.5, 1.0)# dark red
IN_BIT_DISTAL_FOCUS = LColor(0.5, 0.8, 1.0, 1.0)# bright blue
IN_BIT_PROXIMAL_FOCUS = LColor(0.5, 0.8, 1.0, 1.0)# bright blue
IN_BIT_INACTIVE = LColor(1.0, 1.0, 1.0, 1.0) # white


