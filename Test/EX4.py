'''Extent of Reaction Reactor solved  with Matlab'''
import sys
import os
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ".."))
if filepath not in sys.path:
    sys.path.append(filepath)

from numpy import *

from CommonFunctions.Readfile import Readfile
from Sensor.Sensor import Sensor
from Component.Comp import Comp
from Reaction.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Units.Reactor import Reactor
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
class Test4():
    def __init__(self,Ctol):   
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
        F1.Sigma=0.01*F1.Meas
        F1.Sol=12.376455141279800
        T1=Sensor(25)
        T1.Sol=25
        P1=Sensor(100)
        P1.Sol=100
        CO_R=Sensor(0.32)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=0.272610101885968
        H2O_R=Sensor(0.35)
        H2O_R.Sigma=0.01*H2O_R.Meas
        H2O_R.Sol=0.378763814758167
        CO2_R=Sensor(0.09)
        CO2_R.Sigma=0.01*CO2_R.Meas
        CO2_R.Sol=0.081898025761180
        H2_R=Sensor(0.085)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.090579554350688
        CH4_R=Sensor(0.084)
        CH4_R.Sigma=0.01*CH4_R.Meas
        CH4_R.Sol=0.095216085256523
        C2H6_R=Sensor(0.087)
        C2H6_R.Sigma=0.01*C2H6_R.Meas
        C2H6_R.Sol=0.080932417987475
        CTag={CO:CO_R,H2O:H2O_R,CO2:CO2_R,H2:H2_R,CH4:CH4_R,C2H6:C2H6_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(11.95)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=11.674949377742706
        T2=Sensor(25)
        P2=Sensor(100)
        CO_P=Sensor(0.07)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.072870844472924
        H2O_P=Sensor(0.25)
        H2O_P.Sigma=0.01*H2O_P.Meas
        H2O_P.Sol=0.245489359874907
        CO2_P=Sensor(0.22)
        CO2_P.Sigma=0.01*CO2_P.Meas
        CO2_P.Sol=0.272895199272964
        H2_P=Sensor(0.22)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.191968758772945
        CH4_P=Sensor(0.17)
        CH4_P.Sigma=0.01*CH4_P.Meas
        CH4_P.Sol=0.130980481387688
        C2H6_P=Sensor(0.08)
        C2H6_P.Sigma=0.01*C2H6_P.Meas
        C2H6_P.Sol=0.085795356218572
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P,C2H6:C2H6_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',0)
        E.Q.Flag=2
        ListStreams.append(E)
        
        REX=Reactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:2.172430394948006,Rxn2:0.350752881768548}
        ListUnits.append(REX)
        
        self.OPT=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
    T4=Test4(1e-5)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est
    print T4.TestResult 