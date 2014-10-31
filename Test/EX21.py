'''Equilibrium reactor example '''
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
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Reaction.Reaction import Reaction
from Units.EquilibriumReactor import EquilibriumReactor
from Units.Reactor import Reactor
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test21(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Reactor (Equilibrium Reactor with two Reactions)'   
        self.Type=7
        H2=Comp(4,StdState=2)
        CO2=Comp(2,StdState=2)
        CO=Comp(1,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        
        Therm=Refprop([CO,H2O,CO2,H2,CH4])
        
        Rxn1=Reaction('Rxn1',[CO,H2O,CO2,H2],[-1,-1,1,1])
        Rxn2=Reaction('Rxn2',[CO,H2,CH4,H2O],[-1,-3,1,1])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(11.2)
        F1.Sol=1.120230432949998e+01
        T1=Sensor(530)
        T1.Sol=5.300000161154702e+02
        P1=Sensor(106)
        P1.Sol=1.062850908282309e+02
        CO_R=Sensor(0.41)
        CO_R.Sol=4.082164934803849e-01
        H2O_R=Sensor(0.25)
        H2O_R.Sol=2.458901992917100e-01
        H2_R=Sensor(0.35)
        H2_R.Sol=3.458933072279052e-01
        CTag={CO:CO_R,H2O:H2O_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(8.8)
        F2.Sol= 8.798189083164068e+00
        T2=Sensor(564)
        T2.Sol=5.654782593720630e+02
        P2=Sensor(106)
        P2.Sol=1.062850908282309e+02
        CO_P=Sensor(0.14)
        CO_P.Sol=1.354941078542647e-01
        H2O_P=Sensor(0.21)
        H2O_P.Sol=2.020631134323766e-01
        CO2_P=Sensor(0.25)
        CO2_P.Sol=2.476424373208237e-01
        H2_P=Sensor(0.28)
        H2_P.Sol=2.781747685836742e-01
        CH4_P=Sensor(0.14)
        CH4_P.Sol=1.366255728088608e-01
        
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',337000)
        E.Q.Flag=0
        E.Q.Sol=3.359022642710555e+05
        ListStreams.append(E)
        
        REX=EquilibriumReactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        #REX=Reactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:2.178804988564214e+00,Rxn2:1.202057623167956e+00}
        ListUnits.append(REX)
        self.SetSigma(ListStreams,0.01)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-6,iter=5000)
        self.OPT.ObjSol=3.624954316957449e+01
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    Ctol=1e-5
    T1=Test21(1e-5,1)
    for i in T1.OPT.ListStreams:
        print '========================='
        print 'Stream Name: ',i.Name
        print '========================='
        if (not (isinstance(i,Energy_Stream))):
            print 'Flow :',i.FTag.Meas,i.FTag.Est,i.FTag.Sol,i.FTag.Sigma
            print 'Temp :',i.TTag.Meas, i.TTag.Est,i.TTag.Sol,i.TTag.Sigma
            print 'Press:',i.PTag.Meas,i.PTag.Est,i.PTag.Sol,i.PTag.Sigma
            for j in i.CTag.keys():
                print j.Name,' : ',i.CTag[j].Meas,i.CTag[j].Est,i.CTag[j].Sol,i.CTag[j].Sigma
        else:
            print i.Q.Meas,i.Q.Est,i.Q.Sol,i.Q.Sigma
    for i in T1.OPT.ListUints:
        print '========================='
        print 'Unit Name: ',i.Name
        print '========================='
        for j in i.Rxn:
            print 'Extent of Reaction ',j.Name,': ',i.RxnExt[j]
    print T1.TestResult 
    if (not T1.TestResult):
            print T1.TestResultPercentage 
#=================MatLab Code=============================== 
