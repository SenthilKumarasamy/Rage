'''Heater example. Solution obtained from Matlab'''
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
from Units.Heater import Heater
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test16(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Heater example. Solution obtained from Matlab'
        self.Type=7
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.1)
        F1.Sol=10.2922359527333
        T1=Sensor(25)
        T1.Sol=24.9999997737530
        P1=Sensor(100)
        P1.Sol=98.9797993800635
        CO_R=Sensor(0.52)
        CO_R.Sol=0.5038447254990
        H2_R=Sensor(0.47)
        H2_R.Sol=0.4961552745010
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(10.5)
        F2.Sol=10.2922359527333
        T2=Sensor(27)
        T2.Sol=26.9999998351630
        P2=Sensor(98)
        P2.Sol=98.9797993800635
        CO_P=Sensor(0.49)
        CO_P.Sol=0.5038447254990
        H2_P=Sensor(0.53)
        H2_P.Sol=0.4961552745010
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',100)
        E.Q.Flag=0
        E.Q.Sol=597.2995859207216
        ListStreams.append(E)
        self.SetSigma(ListStreams,0.01)
        
        HET=Heater('HET',S1,S2,E)
        ListUnits.append(HET)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=500)
        self.OPT.ObjSol=98.960718220812140   
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    T1=Test16(1e-5,1)
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
    print T1.TestResult 
    if (not T1.TestResult):
            print T1.TestResultPercentage
#===========MatLab Code==========================================================
'''
function [Xopt,Fval,Flag]=HeaterEnergyBalance()
    Fin=10.1;
    TFin=25;
    PFin=100;
    COin=0.52;
    Hin=0.47;
    Fout=10.5;
    TFout=27;
    PFout=98;
    COout=0.49;
    Hout=0.53;
    Q=100;
    Xmeas=[Fin;TFin;PFin;COin;Hin;Fout;TFout;PFout;COout;Hout;Q];
    XFlag=ones(11,1);
    XFlag(11)=0;
    opt=optimset('algorithm','interior-point','display','iter');
    LB=zeros(11,1);
    UB=ones(11,1);
    UB([1,2,3,6,7,8,11])=inf;
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    Fin=X(1);
    TFin=X(2);
    PFin=X(3);
    COin=X(4);
    Hin=X(5);
    Fout=X(6);
    TFout=X(7);
    PFout=X(8);
    COout=X(9);
    Hout=X(10);
    Q=X(11);
    HFin=refpropm('H>','T',TFin+273,'P',PFin,'CO','hydrogen',[COin,Hin]);
    HFout=refpropm('H>','T',TFout+273,'P',PFout,'CO','hydrogen',[COout,Hout]);
    C1=Fin-Fout;
    C2=Fin*COin-Fout*COout;
    C3=COin+Hin-1;
    C4=COout+Hout-1;
    C5=Fin*HFin+Q-Fout*HFout;
    C6=PFin-PFout;
    ceq=[C1;C2;C3;C4;C5;C6];
    c=[];
end
'''
