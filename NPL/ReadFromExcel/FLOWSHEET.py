import sys
import os
basepath = os.path.dirname('__file__')
filepath = os.path.abspath(os.path.join(basepath, "..",".."))
if filepath not in sys.path:
    sys.path.append(filepath)

from CommonFunctions.ReadFlowSheet import ReadFlowSheet
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from CommonFunctions.Write2File import Write2File
from CommonFunctions.GenerateGraph import GenerateGraph
from optim.ipopt import ipopt
from GrossErrorDetection.GLRTest1 import GLR
from Units.PSA import PSA

from Component.Comp import Comp
from Thermo.Refprop import Refprop
from Reaction.Reaction import Reaction
from Sensor.Sensor import Sensor
from Streams.FixedConcStream import FixedConcStream
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.Mixer import Mixer
from Units.Reactor import Reactor
from Units.EquilibriumReactor import EquilibriumReactor
from Units.SteamReformer import SteamReformer
from Units.PreReformer import PreReformer
from Units.ShiftReactor import ShiftReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.PSA import PSA
from Units.Splitter import Splitter
from Units.ElementBalanceReactor import ElementBalanceReactor
from networkx_viewer import Viewer
    
if __name__=="__main__":
    Str1='FlowSheet.xls'
    F1=ReadFlowSheet(Str1)
    
    ToInternalUnits(F1.ListStrm)
    opt1=ipopt(F1.ListStrm,F1.ListUnit,5,5,1e-8,iter=50000)
    GLR1=GLR(opt1,0.01)
    #Write2File(ListStreams,'GED.csv')
    GLR1.MakeDetectedFlagUnmeasured(GLR1.Detected,GLR1.XmIndex)
    opt1=ipopt(F1.ListStrm,F1.ListUnit,5,5,1e-8,iter=100000)
    GLR1.RestoreDetectedFlag(GLR1.Detected,GLR1.XmIndex)
    ToExternalUnits(F1.ListStrm)
    Write2File(F1.ListStrm,"AfterDroppingGESensors.csv")
    G=GenerateGraph(F1.ListStrm,F1.ListUnit)
#     app = Viewer(G)
#     app.mainloop()
    
