''' Mixer Test example to check the unit conversion from KG/HR to Kmol/Hr and then back to KG/HR'''
import sys
import os
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ".."))
if filepath not in sys.path:
    sys.path.append(filepath)

from numpy import *
from Component.Comp import Comp
from Thermo.Refprop import Refprop
from Sensor.Sensor import Sensor
from Streams.FixedConcStream import FixedConcStream
from Units.Splitter import Splitter
from optim.ipopt import ipopt
from GrossErrorDetection.GLRTest import GLR
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits


class Test22():
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Mixer Test example to check the unit conversion from KG/HR to Kmol/Hr and then back to KG/HR'
        self.Type=1
        H2O=Comp(7,StdState=1)
        Therm=Refprop([H2O])
        
        ListStreams=[]
        ListUnits=[]
        
        '''Define stream1'''
        F1=Sensor(101.91)
        F1.Sol=100.22
        F1.Unit='KG/HR'
        T1=Sensor(25)
        T1.Unit='C'
        P1=Sensor(101)
        P1.Unit='KPA'
        CTag={H2O:1}
        S1=FixedConcStream('S1',F1,T1,P1,1,Therm,CTag,'xfrac')
        ListStreams.append(S1)
        
        '''Define stream2'''
        F2=Sensor(64.45)
        F2.Sol=64.50
        F2.Unit='KG/HR'
        T2=Sensor(25)
        T2.Unit='C'
        P2=Sensor(101)
        P2.Unit='KPA'
        CTag={H2O:1}
        S2=FixedConcStream('S2',F2,T2,P2,1,Therm,CTag,'xfrac')
        ListStreams.append(S2)
        
        '''Define stream3'''
        F3=Sensor(34.65)
        F3.Sol=35.72
        F3.Unit='KG/HR'
        T3=Sensor(25)
        T3.Unit='C'
        P3=Sensor(101)
        P3.Unit='KPA'
        CTag={H2O:1}
        S3=FixedConcStream('S3',F3,T3,P3,1,Therm,CTag,'xfrac')
        ListStreams.append(S3)
        
        '''Define Splitter1'''
        SPL=Splitter('SPL',S1,[S2,S3])
        ListUnits.append(SPL)
        # Solving without unit conversion of flow rate
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
        ObjSol=self.OPT.obj
        for i in ListStreams:
            i.FTag.Sol=i.FTag.Est
        
        # Solving with unit conversion from KG/HR to KMOL/Hr and then converting back to KG/HR after solving
        ToInternalUnits(ListStreams)
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
        self.OPT.ObjSol=ObjSol
        
        ToExternalUnits(ListStreams)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#=============================================================
if __name__ == "__main__":
    T1=Test22(1e-5)
    for i in T1.OPT.ListStreams:
        print i.FTag.Est
    print T1.TestResult