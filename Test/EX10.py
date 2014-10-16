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
class Test10():
    def __init__(self,Ctol):   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.1)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=10.292235857373242
        T1=Sensor(100)
        P1=Sensor(100)
        CO_R=Sensor(0.52)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=0.503844725753330
        H2_R=Sensor(0.47)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.496155274246670
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(10.5)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=10.292235857373242
        T2=Sensor(50)
        P2=Sensor(100)
        CO_P=Sensor(0.49)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.503844725753330
        H2_P=Sensor(0.53)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.496155274246670
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        F3=Sensor(5.1)
        F3.Sigma=0.01*F3.Meas
        F3.Sol=4.940917395432558
        T3=Sensor(40)
        P3=Sensor(100)
        CO_R1=Sensor(0.42)
        CO_R1.Sigma=0.01*CO_R1.Meas
        CO_R1.Sol=0.405557767827707
        H2_R1=Sensor(0.62)
        H2_R1.Sigma=0.01*H2_R1.Meas
        H2_R1.Sol= 0.594442232172293
        CTag={CO:CO_R1,H2:H2_R1}
        S3=Material_Stream('S3',F3,T3,P3,2,Therm,CTag)
        ListStreams.append(S3)
        
        F4=Sensor(4.8)
        F4.Sigma=0.01*F4.Meas
        F4.Sol=4.940917395432558
        T4=Sensor(50)
        P4=Sensor(100)
        CO_P1=Sensor(0.41)
        CO_P1.Sigma=0.01*CO_P1.Meas
        CO_P1.Sol=0.405557767827707
        H2_P1=Sensor(0.61)
        H2_P1.Sigma=0.01*H2_P1.Meas
        H2_P1.Sol= 0.594442232172293
        CTag={CO:CO_P1,H2:H2_P1}
        S4=Material_Stream('S4',F4,T4,P4,2,Therm,CTag)
        ListStreams.append(S4)
        
        HEX=HeatExchanger('HEX',S1,S2,S3,S4)
        ListUnits.append(HEX)
        
        self.OPT=ipopt(ListStreams,ListUnits,5,5,1e-12,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
    T4=Test10(1e-5)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est, i.FTag.Flag, i.FTag.Sigma
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est,i.CTag[j].Flag
    print T4.TestResult 
#====================Matlab Code======================================
'''
function [Xopt,Fval,Flag]=HeaterExample()
    Fin=10.1;
    COin=0.52;
    Hin=0.47;
    Fout=10.5;
    COout=0.49;
    Hout=0.53;
    Sin=5.1;
    SCOin=0.42;
    SHin=0.62;
    Sout=4.8;
    SCOout=0.41;
    SHout=0.61;
    Xmeas=[Fin;COin;Hin;Fout;COout;Hout;Sin;SCOin;SHin;Sout;SCOout;SHout];
    XFlag=ones(12,1);
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],zeros(6,0),[],@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    Fin=X(1);
    COin=X(2);   
    Hin=X(3);
    Fout=X(4);
    COout=X(5);
    Hout=X(6);
    Sin=X(7);
    SCOin=X(8);
    SHin=X(9);
    Sout=X(10);
    SCOout=X(11);
    SHout=X(12);
    
    C1=Fin-Fout;
    C2=COin-COout;
    C3=Sin-Sout;
    C4=SCOin-SCOout;
    C5=COin+Hin-1;
    C6=COout+Hout-1;
    C7=SCOin+SHin-1;
    C8=SCOout+SHout-1;
    ceq=[C1;C2;C3;C4;C5;C6;C7;C8];
    c=[];
end
'''
