'''ElementbalanceReactor example. Solution obtained from Matlab'''
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
from Units.ElementBalanceReactor import ElementBalanceReactor
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
class Test5():
    def __init__(self,Ctol):   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
        CO2=Comp(2,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        C2H6=Comp(3,StdState=2)
        
        Therm=Refprop([H2,CO,CO2,H2O,CH4,C2H6])
        

        
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(12.11)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=12.236459565900454
        T1=Sensor(25)
        T1.Sol=25
        P1=Sensor(100)
        P1.Sol=100
        CO_R=Sensor(0.32)
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=0.260215627342918
        H2O_R=Sensor(0.35)
        H2O_R.Sigma=0.01*H2O_R.Meas
        H2O_R.Sol=0.385259333626918
        CO2_R=Sensor(0.09)
        CO2_R.Sigma=0.01*CO2_R.Meas
        CO2_R.Sol=0.082953706960279
        H2_R=Sensor(0.085)
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=0.089146503187727
        CH4_R=Sensor(0.084)
        CH4_R.Sigma=0.01*CH4_R.Meas
        CH4_R.Sol=0.089013261905107
        C2H6_R=Sensor(0.087)
        C2H6_R.Sigma=0.01*C2H6_R.Meas
        C2H6_R.Sol=0.093411566977051
        CTag={CO:CO_R,H2O:H2O_R,CO2:CO2_R,H2:H2_R,CH4:CH4_R,C2H6:C2H6_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(11.95)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=11.822548349475738
        T2=Sensor(25)
        P2=Sensor(100)
        CO_P=Sensor(0.07)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.073153343540962
        H2O_P=Sensor(0.25)
        H2O_P.Sigma=0.01*H2O_P.Meas
        H2O_P.Sol=0.237585191470347
        CO2_P=Sensor(0.22)
        CO2_P.Sigma=0.01*CO2_P.Meas
        CO2_P.Sol=0.264525298764840
        H2_P=Sensor(0.22)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol=0.197008062653091
        CH4_P=Sensor(0.17)
        CH4_P.Sigma=0.01*CH4_P.Meas
        CH4_P.Sol=0.152457529778887
        C2H6_P=Sensor(0.08)
        C2H6_P.Sigma=0.01*C2H6_P.Meas
        C2H6_P.Sol=0.075270573791873
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P,C2H6:C2H6_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',0)
        E.Q.Flag=2
        ListStreams.append(E)
        
        REX=ElementBalanceReactor('REX',S1,S2,[E],ExoEndoFlag=-1)
        ListUnits.append(REX)
        
        self.OPT=ipopt(ListStreams,ListUnits,5,5,1e-12,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
    T4=Test5(1e-5)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est
    print T4.TestResult 
#===========MatLab Code==========================================================
'''
function [Xopt,Fval,Flag]=ElementBalanceReactor()
    FlowR=12.11;
    COR=0.32;
    H2OR=0.35;
    CO2R=0.09;
    H2R=0.085;
    CH4R=0.084;
    C2H6R=0.087;
    FlowP=11.95;
    COP=0.07;
    H2OP=0.25;
    CO2P=0.22;
    H2P=0.22;
    CH4P=0.17;
    C2H6P=0.08;
    Xmeas=[FlowR;COR;H2OR;CO2R;H2R;CH4R;C2H6R;FlowP;COP;H2OP;CO2P;H2P;CH4P;C2H6P];%;2.1;1.2];
    XFlag=ones(14,1);
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj1,Xmeas,[],[],[],[],zeros(11,0),[],@Cons1,opt,Xmeas,XFlag);
end
function f=obj1(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum(XFlag.*((X-Xmeas)./Sigma).^2);
end
function [C,Ceq] = Cons1(X,Xmeas,XFlag)
    % CO + H2O ------> CO2  +  H2
    % CO + 3H2 ------> CH4  +  H2O
    FlowR=X(1);
    COR=X(2);
    H2OR=X(3);
    CO2R=X(4);
    H2R=X(5);
    CH4R=X(6);
    C2H6R=X(7);
    FlowP=X(8);
    COP=X(9);
    H2OP=X(10);
    CO2P=X(11);
    H2P=X(12);
    CH4P=X(13);
    C2H6P=X(14);

    C1=FlowR * (COR + CO2R + CH4R + C2H6R*2)-FlowP * (COP + CO2P + CH4P + C2H6P*2);
    C2=FlowR * (COR + H2OR + CO2R*2) - FlowP * (COP + H2OP + CO2P*2);
    C3=FlowR * (H2OR*2 + H2R*2 + CH4R*4 + C2H6R*6) - FlowP * (H2OP*2 + H2P*2 + CH4P*4 + C2H6P*6);
    C4=COR+H2OR+CO2R+H2R+CH4R+C2H6R-1.0;
    C5=COP+H2OP+CO2P+H2P+CH4P+C2H6P-1.0;

    Ceq=[C1;C2;C3;C4;C5];
    C=[];
end
'''