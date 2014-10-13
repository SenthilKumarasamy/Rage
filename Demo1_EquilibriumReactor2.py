from numpy import *
import pyipopt
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Streams.Energy_Stream import Energy_Stream 
from Streams.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Units.EquilibriumReactor import EquilibriumReactor
from Units.EquilibriumReactor2 import EquilibriumReactor2
from Thermo.Refprop import Refprop
from optim.ipopt import ipopt

CO=Comp(1,StdState=2)
H2O=Comp(7,StdState=1)
H2=Comp(4,StdState=2)
CO2=Comp(2,StdState=2)

Therm=Refprop([H2,CO,CO2,H2O])
ListStreams=[]
ListUnits=[]

RE1=Reaction('RE1',[CO,H2O,CO2,H2],[-1,-1,1,1])

F1=Sensor(2)
F1.Flag=2
T1=Sensor(827)
P1=Sensor(100)
C1={CO:0.5,H2O:0.5}
S1=FixedConcStream('S1',F1,T1,P1,2,Therm,C1,'xfrac')
ListStreams.append(S1)

F2=Sensor(2)
T2=Sensor(827)
P2=Sensor(100)
CH2=Sensor(0.15)
CH2O=Sensor(0.35)
CCO=Sensor(0.35)
CCO2=Sensor(0.15)
C={H2:CH2,H2O:CH2O,CO:CCO,CO2:CCO2}
S2=Material_Stream('S2',F2,T2,P2,2,Therm,C)
ListStreams.append(S2)

E2=Energy_Stream('E2',0)
E2.Q.Flag=2
ListStreams.append(E2)

R1=EquilibriumReactor2('R1',S1,S2,[E2],[RE1])
ListUnits.append(R1)

opt1=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=5000)

for i in ListStreams:
    if (not isinstance(i,Energy_Stream)):
        if (i.FTag.Flag==1):
            print i.FTag.Xindex,'\t',i.FTag.Tag,'\t', i.FTag.Meas,'\t', i.FTag.Est
        if (isinstance(i,Material_Stream)):
            for j in i.CTag.keys():
                if (i.CTag[j].Flag==1):
                    print i.CTag[j].Xindex,'\t',i.CTag[j].Tag,'\t', i.CTag[j].Meas,'\t', i.CTag[j].Est


