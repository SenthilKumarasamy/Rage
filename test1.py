from Streams.Readfile import Readfile
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Streams.Therm import Therm
from Streams.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.EquilibriumReactor import EquilibriumReactor
from Units.HeatExchanger import HeatExchanger

str="D:\\Gyandata\\Python\\RAGE2/Meas.dat"
R1=Readfile(str)
S1F=Sensor('FT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S1T=Sensor('TT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S1P=Sensor('PT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S1C1=Sensor('CT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S1C2=Sensor('CT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)

S2T=Sensor('TT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S3T=Sensor('TT102',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
S4T=Sensor('TT103',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
C1=Comp(110)
C2=Comp(10)
Rxn1=Reaction([C1,C2],[-1,1],23,23)
T1=Therm([C1,C2],0,0,298,101.325)
S1=Material_Stream(S1F,S1T,S1P,1,T1,[C1,C2],[S1C1,S1C2])
S2=Material_Stream(S1F,S2T,S1P,1,T1,[C1,C2],[S1C1,S1C2])
S3=Material_Stream(S1F,S3T,S1P,1,T1,[C1,C2],[S1C1,S1C2])
S4=Material_Stream(S1F,S4T,S1P,1,T1,[C1,C2],[S1C1,S1C2])

Q1=Energy_Stream(100)


Rx=EquilibriumReactor(S1,S1,[Q1],[Rxn1])
Rx.Residual()
print Rx.Resid

Het=Heater(S1,S1,Q1)
Het.Residual()
print Het.Resid

Hex=HeatExchanger(S1,S2,S3,S4,200,100,1)
print Hex.hotin.TTag.Meas,Hex.hotout.TTag.Meas,Hex.coldin.TTag.Meas,Hex.coldout.TTag.Meas
Hex.Residual()
print Hex.Resid

SPL=Splitter(S1,[S2,S3])
SPL.Residual()
print SPL.Resid
