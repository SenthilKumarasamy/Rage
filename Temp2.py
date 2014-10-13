from fpdf import FPDF
from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
from scipy.optimize import minimize
import pyipopt
from optim.myslsqp import myslsqp
from numpy import float_
from numpy import exp

import Constraints as Con
from Streams.Readfile import Readfile
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Thermo.IdealGas import IdealGas
from Streams.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.HeaterVaporizer import HeaterVaporizer
from Units.Mixer import Mixer
from Units.Reactor import Reactor
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
    
    H2=Comp(4,StdState=2)
    CO=Comp(1,StdState=2)
    CO2=Comp(2,StdState=2)
    H2O=Comp(7,StdState=1)
    CH4=Comp(5,StdState=2)
    C2H6=Comp(3,StdState=2)
    
    Therm=Refprop([H2,CO,CO2,H2O,CH4,C2H6])
    
    Rxn1=Reaction('Rxn1',[CO,H2O,CO2,H2],[-1,-1,1,1])
    Rxn2=Reaction('Rxn2',[CO,H2,CH4,H2O],[-1,-3,1,1])
    
    
    ListStreams=[]
    ListUnits=[]
    
    F1=Sensor(12.11)
    T1=Sensor(25)
    P1=Sensor(100)
    CO_R=Sensor(0.32)
    H2O_R=Sensor(0.35)
    CO2_R=Sensor(0.09)
    H2_R=Sensor(0.085)
    CH4_R=Sensor(0.084)
    C2H6_R=Sensor(0.087)
    CTag={CO:CO_R,H2O:H2O_R,CO2:CO2_R,H2:H2_R,CH4:CH4_R,C2H6:C2H6_R}
    S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
    ListStreams.append(S1)
    
    F2=Sensor(11.95)
    T2=Sensor(25)
    P2=Sensor(100)
    CO_P=Sensor(0.07)
    H2O_P=Sensor(0.25)
    CO2_P=Sensor(0.22)
    H2_P=Sensor(0.22)
    CH4_P=Sensor(0.17)
    C2H6_P=Sensor(0.08)
    CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P,C2H6:C2H6_P}
    S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
    ListStreams.append(S2)
    
    E=Energy_Stream('E',0)
    E.Q.Flag=2
    ListStreams.append(E)
    
    #REX=ElementBalanceReactor('REX',S1,S2,[E],ExoEndoFlag=-1)
    REX=Reactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
    #REX=EquilibriumReactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
    ListUnits.append(REX)
    
    opt1=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=500)
    
    for i in ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est
    