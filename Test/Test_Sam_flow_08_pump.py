#Reactor modelling: Pump
from fpdf import FPDF
from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
#from scipy.optimize import minimize
import pyipopt
#from optim.myslsqp import myslsqp
from numpy import float_
from numpy import exp
import sys
import os
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ".."))
if filepath not in sys.path:
    sys.path.append(filepath)


#import Constraints as Con
from CommonFunctions.Readfile import Readfile
from Sensor.Sensor import Sensor
from Component.Comp import Comp
from Thermo.IdealGas import IdealGas
from Reaction.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.HeaterVaporizer import HeaterVaporizer
from Units.Mixer import Mixer
from Units.Reactor import Reactor
from Units.Pump import Pump
from Units.EquilibriumReactor import EquilibriumReactor
from Units.EquilibriumReactor2 import EquilibriumReactor2
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Splitter import Splitter
from Units.ElementBalanceReactor import ElementBalanceReactor
from Units.HeatExchangerVaporizer import HeatExchangerVaporizer
from optim.ipopt import ipopt
from CommonFunctions.Report import Report
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from CommonFunctions.Write2File import Write2File
from Thermo.Refprop import Refprop
from GrossErrorDetection.GLRTest import GLR

if __name__=="__main__":
#     CO=Comp(Compid=1,StdState=1)
#     H2O=Comp(Compid=7,StdState=1)
#     CO2=Comp(Compid=2,StdState=1)
#     H2=Comp(Compid=4,StdState=1)    
#     Ref=Refprop([CO,H2O,CO2,H2])
#     
#     ListStreams=[]
#     ListUnits=[]
#     
#     F1=Sensor(0.555*3600) # kmol/hr
#     F1.Flag=1 # Measured
#     T1=Sensor(25)
#     P1=Sensor(101.325) # kPa
#     P1.Flag = 1 # Measured
#     CO_1=Sensor(0.0)
#     CO_1.Flag=2 # Constant
#     H2O_1=Sensor(1.0)
#     H2O_1.Flag=1 # Measured
#     CO2_1=Sensor(0.0)
#     CO2_1.Flag=2 # Constant
#     H2_1=Sensor(0.0)
#     H2_1.Flag=2 # Constant
#     #CTag={CO:CO_1, H2O:H2O_1, CO2:CO2_1, H2:H2_1}
#     CTag={H2O:1.0}
#     LiqLow=FixedConcStream('LiqLow',F1,T1,P1,1,Ref,CTag,'xfrac')
#     ListStreams.append(LiqLow)
#     
#     F2=Sensor(0.555*3600) # kmol/hr
#     F2.Flag=1 # Measured
#     T2=Sensor(25)
#     P2=Sensor(202.650) # kPa
#     P2.Flag = 1 # Measured
#     CO_2=Sensor(0.0)
#     CO_2.Flag=2 # Constant
#     H2O_2=Sensor(1.0)
#     H2O_2.Flag=1 # Measured
#     CO2_2=Sensor(0.0)
#     CO2_2.Flag=2 # Constant
#     H2_2=Sensor(0.0)
#     H2_2.Flag=2 # Constant
#     #CTag={CO:CO_2, H2O:H2O_2, CO2:CO2_2, H2:H2_2}
#     CTag={H2O:1.0}
#     LiqHigh=FixedConcStream('LiqHigh',F2,T2,P2,1,Ref,CTag,'xfrac')
#     ListStreams.append(LiqHigh)

    H2O=Comp(Compid=7,StdState=1)
    Ref=Refprop([H2O])
    
    ListStreams=[]
    ListUnits=[]
    
    F1=Sensor(1998.0) # kmol/hr # 0.555*3600
    F1.Flag=1 # Measured
    T1=Sensor(25)
    P1=Sensor(101.325) # kPa
    P1.Flag = 1 # Measured
    CTag={H2O:1}  
    LiqLow=FixedConcStream('LiqLow',F1,T1,P1,1,Ref,CTag,'xfrac')
    ListStreams.append(LiqLow)
    
    
    F2=Sensor(1998.0) # kmol/hr # 0.555*3600
    F2.Flag=1 # Measured
    T2=Sensor(25)
    P2=Sensor(202.65) # kPa
    P2.Flag = 1 # Measured
    CTag={H2O:1}  
    LiqHigh=FixedConcStream('LiqHigh',F2,T2,P2,1,Ref,CTag,'xfrac')
    ListStreams.append(LiqHigh)

    pump_power=3414.123 # 3600*1.26 * 0.75 kJ/hr
    QStream=Energy_Stream('QStream',pump_power)
    ListStreams.append(QStream)


    PUMP1=Pump('PUMP1', LiqLow, LiqHigh, QStream)
    ListUnits.append(PUMP1)
  
    opt1=ipopt(ListStreams,ListUnits,7,5,Xtol=1e-8,iter=100)

print 'Energy'
print QStream.Q.Meas, QStream.Q.Est, QStream.Q.Sigma
print '-----'

for X in ListStreams[:-1]:
    print X.Name
    print 'Flow:'
    print X.FTag.Meas, X.FTag.Est, X.FTag.Sigma
    print X.PTag.Meas, X.PTag.Est, X.PTag.Sigma
  
    print 'Concentrations:'
    for x in X.CTag.keys():
        print x.Name[:-4], X.CTag[x].Meas, X.CTag[x].Est, X.CTag[x].Sigma
    print
