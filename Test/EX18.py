'''Reactor and Heater'''
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
from Units.Reactor import Reactor
from Units.Heater import Heater
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test18(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Reactor (Extent of Reaction) and Heater'   
        self.Type=7
        O2=Comp(6,StdState=2)
        CO2=Comp(2,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
        
        Therm=Refprop([CO2,H2O,CH4,O2,H2,CO])
        
        Rxn1=Reaction('Rxn1',[CH4,O2,CO2,H2O],[-1,-2,1,2])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(0.0025)#0.0022
        F1.Sol=2.547519345203116e-03
        T1=Sensor(25)
        T1.Sol=2.499996956798440e+01
        P1=Sensor(105)
        P1.Sol=1.023781353760656e+02
        CH4_R=Sensor(0.339)
        CH4_R.Sol= 3.333333333333333e-01
        O2_R=Sensor(0.672)
        O2_R.Sol=6.666666666666666e-01
        CTag={CH4:CH4_R,O2:O2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(0.0026)#0.0022
        F2.Sol= 2.547519345203116e-03
        T2=Sensor(120)
        T2.Sol=1.200007866986675e+02
        P2=Sensor(100)
        P2.Sol=1.023781353760656e+02
        H2O_P=Sensor(0.673)
        H2O_P.Sol=6.666666666666666e-01
        CO2_P=Sensor(0.335)
        CO2_P.Sol=3.333333333333333e-01
        CTag={CO2:CO2_P,H2O:H2O_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',100)
        E.Q.Flag=0
        E.Q.Sol=6.701306907570768e+02
        ListStreams.append(E)
        
        REX=Reactor('REX',S1,S2,[E],[Rxn1],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:8.491731150677052e-04}
        ListUnits.append(REX)
        
        F11=Sensor(10.1)
        F11.Sol=1.029431168698602e+01
        T11=Sensor(25)
        T11.Sol=2.488765932997879e+01
        P11=Sensor(100)
        P11.Sol=9.897981452278087e+01
        CO_R1=Sensor(0.52)
        CO_R1.Sol=5.038450361426106e-01
        H2_R1=Sensor(0.47)
        H2_R1.Sol=4.961549638573895e-01
        CTag={CO:CO_R1,H2:H2_R1}
        S11=Material_Stream('S11',F11,T11,P11,2,Therm,CTag)
        ListStreams.append(S11)
        
        F21=Sensor(10.5)
        F21.Sol=1.029431168698602e+01
        T21=Sensor(27)
        T21.Sol=2.713107227423428e+01
        P21=Sensor(98)
        P21.Sol=9.897981452278087e+01
        CO_P1=Sensor(0.49)
        CO_P1.Sol=5.038450361426106e-01
        H2_P1=Sensor(0.53)
        H2_P1.Sol=4.961549638573894e-01
        CTag={CO:CO_P1,H2:H2_P1}
        S21=Material_Stream('S21',F21,T21,P21,2,Therm,CTag)
        ListStreams.append(S21)
        self.SetSigma(ListStreams,0.01)
        
        HET=Heater('HET',S11,S21,E)
        ListUnits.append(HET)

        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
        self.OPT.ObjSol=1.235341433464574e+02
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    Ctol=1e-5
    T1=Test18(1e-5,1)
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
#====================Matlab Code========================================
'''
function [Xopt,Fval,Flag]=ReactorHeater()
    FR=0.0025;
    TR=25;
    PR=105;
    CH4_R=0.339;
    O2_R=0.672;
    
    FP=0.0026;
    TP=120;
    PP=100;
    CO2_P=0.335;
    H2O_P=0.673;
    
    FHin=10.1;
    THin=25;
    PHin=100;
    CO_Hin=0.52;
    H2_Hin=0.47;
    
    FHout=10.5;
    THout=27;
    PHout=98;
    CO_Hout=0.49;
    H2_Hout=0.53;
    
    Q=100;
    
    Xmeas=[FR;TR;PR;CH4_R;O2_R;FP;TP;PP;CO2_P;H2O_P;FHin;THin;PHin;CO_Hin;H2_Hin;FHout;THout;PHout;CO_Hout;H2_Hout;Q;2.1];
    XFlag=ones(22,1);
    XFlag([21,22])=0;
    LB=zeros(22,1);
    UB=ones(22,1);
    UB([1,2,3,6,7,8,11,12,13,16,17,18,21,22])=inf;
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [C,Ceq] = Cons(X,Xmeas,XFlag)
    % CH4 + 2O2 -----> CO2 + 2H2O
    FR=X(1);
    TR=X(2);
    PR=X(3);
    CH4_R=X(4);
    O2_R=X(5);
    FP=X(6);
    TP=X(7);
    PP=X(8);
    CO2_P=X(9);
    H2O_P=X(10);
    
    FHin=X(11);
    THin=X(12);
    PHin=X(13);
    CO_Hin=X(14);
    H2_Hin=X(15);
    
    FHout=X(16);
    THout=X(17);
    PHout=X(18);
    CO_Hout=X(19);
    H2_Hout=X(20);
    
    Q=X(21);
    Ext=X(22);
    
    C1=FR*CH4_R - Ext; % CH4 balance
    C2=FR*O2_R - 2*Ext; % O2 Balance
    C3= -FP*CO2_P + Ext; % CO2 Balance
    C4= -FP*H2O_P + 2*Ext; % H20 Balance
    C5=CH4_R+O2_R-1.0;
    C6=CO2_P+H2O_P-1.0;
    HosR=OffSetR(CH4_R,O2_R);
    HR=refpropm('H<','T',TR+273,'P',PR,'methane','oxygen','CO2','water','CO','hydrogen',[CH4_R,O2_R,0,0,0,0])+HosR;
    HosP=OffSetP(CO2_P,H2O_P);
    HP=refpropm('H<','T',TP+273,'P',PP,'methane','oxygen','CO2','water','CO','hydrogen',[0,0,CO2_P,H2O_P,0,0])+HosP;
    C7=FR*HR-Q-FP*HP;
    C8=PR-PP;
    
    C9=FHin-FHout;
    C10=CO_Hin-CO_Hout;
    C11=CO_Hin+H2_Hin-1;
    C12=CO_Hout+H2_Hout-1;
    Hin=refpropm('H<','T',THin+273,'P',PHin,'methane','oxygen','CO2','water','CO','hydrogen',[0,0,0,0,CO_Hin,H2_Hin]);
    Hout=refpropm('H<','T',THout+273,'P',PHout,'methane','oxygen','CO2','water','CO','hydrogen',[0,0,0,0,CO_Hout,H2_Hout]);
    C13=FHin*Hin+Q-FHout*Hout;
    C14=PHin-PHout;
    Ceq=[C1;C2;C3;C4;C5;C6;C7;C8;C9;C10;C11;C12;C13;C14];
    C=[];
end
function Hos=OffSetR(CH4_R,O2_R)
    Hos=CH4_R*-89098.91450281386+O2_R*-8666.33550895689;
end
function Hos=OffSetP(CO2_P,H2O_P)
    Hos=CO2_P*-415568.87614272034+H2O_P*-285995.1604551062;
end
'''