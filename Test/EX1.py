from numpy import *
from Component.Comp import Comp
from Thermo.Refprop import Refprop
from Sensor.Sensor import Sensor
from Streams.FixedConcStream import FixedConcStream
from Units.Splitter import Splitter
from Units.Mixer import Mixer
from optim.ipopt import ipopt

class Test1():
    def __init__(self,Ctol):

        H2O=Comp(7,StdState=1)
        Therm=Refprop([H2O])
        
        ListStreams=[]
        ListUnits=[]
        
        '''Define stream1'''
        F1=Sensor(101.91)
        F1.Sol=100.22
        T1=Sensor(25)
        P1=Sensor(101)
        CTag={H2O:1}
        S1=FixedConcStream('S1',F1,T1,P1,1,Therm,CTag,'xfrac')
        ListStreams.append(S1)
        
        '''Define stream2'''
        F2=Sensor(64.45)
        F2.Sol=64.50
        T2=Sensor(25)
        P2=Sensor(101)
        CTag={H2O:1}
        S2=FixedConcStream('S2',F2,T2,P2,1,Therm,CTag,'xfrac')
        ListStreams.append(S2)
        
        '''Define stream3'''
        F3=Sensor(34.65)
        F3.Sol=35.72
        T3=Sensor(25)
        P3=Sensor(101)
        CTag={H2O:1}
        S3=FixedConcStream('S3',F3,T3,P3,1,Therm,CTag,'xfrac')
        ListStreams.append(S3)
        
        '''Define Splitter1'''
        SPL=Splitter('SPL',S1,[S2,S3])
        ListUnits.append(SPL)
        
        '''Define stream4'''
        F4=Sensor(64.20)
        F4.Sol=64.50
        T4=Sensor(25)
        P4=Sensor(101)
        CTag={H2O:1}
        S4=FixedConcStream('S4',F4,T4,P4,1,Therm,CTag,'xfrac')
        ListStreams.append(S4)
        
        '''Define Heater'''
        HEX=Splitter('HEX',S2,[S4])
        ListUnits.append(HEX)
        
        '''Define stream5'''
        F5=Sensor(36.44)
        F5.Sol=35.72
        T5=Sensor(25)
        P5=Sensor(101)
        CTag={H2O:1}
        S5=FixedConcStream('S5',F5,T5,P5,1,Therm,CTag,'xfrac')
        ListStreams.append(S5)
        
        '''Define Valve'''
        VAL=Splitter('VAL',S3,[S5])
        ListUnits.append(VAL)
        
        '''Define stream6'''
        F6=Sensor(98.88)
        F6.Sol=100.22
        T6=Sensor(25)
        P6=Sensor(101)
        CTag={H2O:1}
        S6=FixedConcStream('S6',F6,T6,P6,1,Therm,CTag,'xfrac')
        ListStreams.append(S6)
            
        '''Define Mixer'''
        MIX=Mixer('MIX',[S5,S4],S6)
        ListUnits.append(MIX)
        
        self.OPT=ipopt(ListStreams,ListUnits,2,5,1e-4,iter=5000)
        self.TestResult=self.OPT.CompareEstSol(Ctol)