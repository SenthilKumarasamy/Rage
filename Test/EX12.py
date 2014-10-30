'''Heat Exchanger example with energy balance. Solution obtained from Matlab'''
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
from Units.HeatExchanger import HeatExchanger
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
class Test12():
    def __init__(self,Ctol=1e-5,Ptol=0.5):
        self.Description='Heat Exchanger example with energy balance. Solution obtained from Matlab'
        self.Type=6   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(1.1)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=1.072748082705692
        T1=Sensor(100)
        T1.Sigma=0.01*T1.Meas
        T1.Sol=99.589703677287545
        P1=Sensor(100)
        P1.Sigma=0.01*P1.Meas
        P1.Flag=2
        CO_R=Sensor(0.52)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol= 0.503843983966100
        H2_R=Sensor(0.47)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.496156016033900
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(1.05)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=1.072748082705692
        T2=Sensor(50)
        T2.Sigma=0.01*T2.Meas
        T2.Sol=50.102150586564591
        P2=Sensor(100)
        P2.Sigma=0.01*P2.Meas
        P2.Flag=2
        CO_P=Sensor(0.49)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.503843983966100
        H2_P=Sensor(0.53)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.496156016033900
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        F3=Sensor(5.1)
        F3.Sigma=0.01*F3.Meas
        F3.Sol=4.945923242555951
        T3=Sensor(40)
        T3.Sigma=0.01*T3.Meas
        T3.Sol=39.699183844374431
        P3=Sensor(100)
        P3.Sigma=0.01*P3.Meas
        P3.Flag=2
        CO_R1=Sensor(0.42)
        CO_R1.Sigma=0.01*CO_R1.Meas
        CO_R1.Sol=0.405558768990082
        H2_R1=Sensor(0.62)
        H2_R1.Sigma=0.01*H2_R1.Meas
        H2_R1.Sol=0.594441231009918
        CTag={CO:CO_R1,H2:H2_R1}
        S3=Material_Stream('S3',F3,T3,P3,2,Therm,CTag)
        ListStreams.append(S3)
        
        F4=Sensor(4.8)
        F4.Sigma=0.01*F4.Meas
        F4.Sol=4.945923242555951
        T4=Sensor(50)
        T4.Sigma=T4.Meas
        T4.Sol=50.470631264775783
        P4=Sensor(100)
        P4.Sigma=P4.Meas
        P4.Flag=2
        CO_P1=Sensor(0.41)
        CO_P1.Sigma=0.01*CO_P1.Meas
        CO_P1.Sol=0.405558768990082
        H2_P1=Sensor(0.61)
        H2_P1.Sigma=0.01*H2_P1.Meas
        H2_P1.Sol= 0.594441231009918
        CTag={CO:CO_P1,H2:H2_P1}
        S4=Material_Stream('S4',F4,T4,P4,2,Therm,CTag)
        ListStreams.append(S4)
        
        HEX=HeatExchanger('HEX',S1,S2,S3,S4)
        ListUnits.append(HEX)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=500)
        self.OPT.ObjSol=156.7401
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    T4=Test12(1e-5,1)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print '============================'
            print 'Stream Name:',i.Name
            print 'Flow:', i.FTag.Est, i.FTag.Meas
            print 'Temp: ',i.TTag.Est, i.TTag.Meas
            print 'Press: ',i.PTag.Est,i.PTag.Meas
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est,i.CTag[j].Meas
    print '======================================='
    print T4.TestResult 
    print T4.TestResultPercentage
#====================Matlab Code======================================
'''
function [Xopt,Fval,Flag]=HeaterExample()
    Fin=1.1;
    FTin=100;
    COin=0.52;
    Hin=0.47;
    Fout=1.05;
    FTout=50;
    COout=0.49;
    Hout=0.53;
    Sin=5.1;
    STin=40;
    SCOin=0.42;
    SHin=0.62;
    Sout=4.8;
    STout=50;
    SCOout=0.41;
    SHout=0.61;
    Xmeas=[Fin;FTin;COin;Hin;Fout;FTout;COout;Hout;Sin;STin;SCOin;SHin;Sout;STout;SCOout;SHout];
    XFlag=ones(16,1);
    opt=optimset('algorithm','interior-point','display','iter','TolX',1e-12,'TolFun',1e-8);
    LB=zeros(16,1);
    UB=ones(16,1);
    UB([1,2,5,6,9,10,13,14])=inf;
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    Fin=X(1);
    FTin=X(2);
    COin=X(3);   
    Hin=X(4);
    Fout=X(5);
    FTout=X(6);
    COout=X(7);
    Hout=X(8);
    Sin=X(9);
    STin=X(10);
    SCOin=X(11);
    SHin=X(12);
    Sout=X(13);
    STout=X(14);
    SCOout=X(15);
    SHout=X(16);
    
    C1=Fin-Fout;
    C2=COin-COout;
    C3=Sin-Sout;
    C4=SCOin-SCOout;
    C5=COin+Hin-1;
    C6=COout+Hout-1;
    C7=SCOin+SHin-1;
    C8=SCOout+SHout-1;
    %=============Energy Balance========================%
    FinEnthal=refpropm('H>','T',FTin+273,'P',100,'CO','hydrogen',[COin,Hin]);
    FoutEnthal=refpropm('H>','T',FTout+273,'P',100,'CO','hydrogen',[COout,Hout]);
    SinEnthal=refpropm('H>','T',STin+273,'P',100,'CO','hydrogen',[SCOin,SHin]);
    SoutEnthal=refpropm('H>','T',STout+273,'P',100,'CO','hydrogen',[SCOout,SHout]);
    C9=(Fin*FinEnthal-Fout*FoutEnthal)-(Sout*SoutEnthal-Sin*SinEnthal);
    %============End of Energy Balance====================%
    ceq=[C1;C2;C3;C4;C5;C6;C7;C8;C9];
    CI1=STin-FTout;
    CI2=STout-FTin;
    c=[CI1;CI2];
end
function [rho,ierr]=TPRho(T,P,X,PhaseFlag,Ref)
    herr = 32*ones(255,1);
    [dummy dummy dummyx dummy dummy rho ierr errTxt] = calllib(Ref,'TPRHOdll', T, P, X, PhaseFlag, 0, 0, 0, herr, 255);
end
function h=Enthal(T,X,Rho,Ref)
    [dummy,dummy,dummy,h]=calllib(Ref,'ENTHALdll',T,Rho,X,0);
end
'''
