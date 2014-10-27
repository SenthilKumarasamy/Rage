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
class Test9():
    def __init__(self,Ctol):
        self.Description='Heater example. Solution obtained from Matlab'
        self.Type=5   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        

        
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.1)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=10.292235866436428
        T1=Sensor(25)
        T1.Sol=25
        P1=Sensor(100)
        P1.Sol=100
        CO_R=Sensor(0.52)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=0.503844726098164
        H2_R=Sensor(0.47)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.496155273901836
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(10.5)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=10.292235866436428
        T2=Sensor(25)
        P2=Sensor(100)
        CO_P=Sensor(0.49)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.503844726098164
        H2_P=Sensor(0.53)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.496155273901836
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',0)
        E.Q.Flag=2
        ListStreams.append(E)
        
        HET=Heater('HET',S1,S2,E)
        ListUnits.append(HET)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-12,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
    T4=Test9(1e-5)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est
    print T4.TestResult 
#===========MatLab Code==========================================================
'''
function [Xopt,Fval,Flag]=HeaterExample()
    Fin=10.1;
    COin=0.52;
    Hin=0.47;
    Fout=10.5;
    COout=0.49;
    Hout=0.53;
    Xmeas=[Fin;COin;Hin;Fout;COout;Hout];
    XFlag=ones(6,1);
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
    C1=Fin-Fout;
    C2=Fin*COin-Fout*COout;
    C3=COin+Hin-1;
    C4=COout+Hout-1;
    ceq=[C1;C2;C3;C4];
    c=[];
end
'''
