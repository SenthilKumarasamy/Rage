'''Separator example. Solution obtained by solving in Matlab'''
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
from Units.Seperator import Seperator
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
class Test11():
    def __init__(self,Ctol):
        self.Description='Separator example. Solution obtained by solving in Matlab'
        self.Type=5   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.9547)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=10.027126782740753
        T1=Sensor(100)
        P1=Sensor(100)
        CO_R=Sensor(0.4822)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=0.481092728766512
        H2_R=Sensor(0.5170)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.518907271233487
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(4.7840)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=4.973631415577737
        T2=Sensor(50)
        P2=Sensor(100)
        CO_P=Sensor(0.9410)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.949889621425092
        H2_P=Sensor(0.0501)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.050110378574908
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        F3=Sensor(4.8823)
        F3.Sigma=0.01*F3.Meas
        F3.Sol=5.053495367163017
        T3=Sensor(40)
        P3=Sensor(100)
        CO_R1=Sensor(0.0197)
        CO_R1.Sigma=0.01*CO_R1.Meas
        CO_R1.Sol=0.019704564051347
        H2_R1=Sensor(0.9748)
        H2_R1.Sigma=0.01*H2_R1.Meas
        H2_R1.Sol= 0.980295435948653
        CTag={CO:CO_R1,H2:H2_R1}
        S3=Material_Stream('S3',F3,T3,P3,2,Therm,CTag)
        ListStreams.append(S3)
        

        SEP=Seperator('SEP',S1,[S2,S3])
        ListUnits.append(SEP)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
    T4=Test11(1e-5)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est, i.FTag.Flag, i.FTag.Sigma
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est,i.CTag[j].Flag
    print T4.TestResult 
#===================Matlab code=====================================
'''
function [Xopt,Fval,Flag]=SeparatorExample()
    F=10.9547;
    COF=0.4822;
    HF=0.5170;
    D=4.7840;
    COD=0.9410;
    HD=0.0501;
    B=4.8823;
    COB=0.0197;
    HB=0.9748;
    Xmeas=[F;COF;HF;D;COD;HD;B;COB;HB];
    XFlag=ones(9,1);
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],zeros(6,0),[],@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    F=X(1);
    COF=X(2);
    HF=X(3);
    D=X(4);
    COD=X(5);
    HD=X(6);
    B=X(7);
    COB=X(8);
    HB=X(9);
    C1=F-B-D;
    C2=F*COF-D*COD-B*COB;
    C3=COF+HF-1;
    C4=COD+HD-1;
    C5=COB+HB-1;
    ceq=[C1;C2;C3;C4;C5];
    c=[];
end
'''
