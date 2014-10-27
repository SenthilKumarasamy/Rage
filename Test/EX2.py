'''Example 1 in Data reconciliation and gross error detection book by Prof. Shankar where
streams 3 and 4 are unmeasured.'''
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
from Units.Mixer import Mixer
from optim.ipopt import ipopt
from GrossErrorDetection.GLRTest import GLR

class Test2():
    def __init__(self,Ctol):
        self.Description='Example 1 in Data reconciliation and gross error detection book by Prof. Shankar where streams 3 and 4 are unmeasured.'
        self.Type=1
        H2O=Comp(7,StdState=1)
        Therm=Refprop([H2O])
        
        ListStreams=[]
        ListUnits=[]
        
        '''Define stream1'''
        F1=Sensor(101.91)
        F1.Sol=100.494
        T1=Sensor(25)
        P1=Sensor(101)
        CTag={H2O:1}
        S1=FixedConcStream('S1',F1,T1,P1,1,Therm,CTag,'xfrac')
        ListStreams.append(S1)
        
        '''Define stream2'''
        F2=Sensor(64.45)
        F2.Sol=64.252
        T2=Sensor(25)
        P2=Sensor(101)
        CTag={H2O:1}
        S2=FixedConcStream('S2',F2,T2,P2,1,Therm,CTag,'xfrac')
        ListStreams.append(S2)
        
        '''Define stream3'''
        F3=Sensor(34.65)
        F3.Flag=0
        F3.Sol=36.242
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
        F4.Flag=0
        F4.Sol=64.252
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
        F5.Sol=36.242
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
        F6.Sol=100.494
        T6=Sensor(25)
        P6=Sensor(101)
        CTag={H2O:1}
        S6=FixedConcStream('S6',F6,T6,P6,1,Therm,CTag,'xfrac')
        ListStreams.append(S6)
            
        '''Define Mixer'''
        MIX=Mixer('MIX',[S5,S4],S6)
        ListUnits.append(MIX)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-12,iter=5000)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        self.GLR1=GLR(self.OPT)

#===========================================================================        
if __name__ == "__main__":
    T2=Test2(1e-5)
    for i in T2.OPT.ListStreams:
        print i.FTag.Est
    print T2.TestResult
#========================Matlab Code==========================
'''
function [Xopt,Fval,Flag]=FlowExample()
    F1=101.91;
    F2=64.45;
    F3=34.65;
    F4=64.20;
    F5=36.44;
    F6=98.88;
    Xmeas=[F1;F2;F3;F4;F5;F6];
    XFlag=ones(6,1);
    XFlag([3,4])=0;
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],zeros(6,0),[],@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    f=sum(((X-Xmeas).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    F1=X(1);F2=X(2);F3=X(3);F4=X(4);F5=X(5);F6=X(6);
    C1=F1-F2-F3;
    C2=F2-F4;
    C3=F3-F5;
    C4=F6-F5-F4;
    ceq=[C1;C2;C3;C4];
    c=[];
end
''' 