'''Extent of reaction reactor example '''
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
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test17(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Reactor (Extent of Reaction)'   
        self.Type=7
        O2=Comp(6,StdState=2)
        CO2=Comp(2,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        
        Therm=Refprop([CO2,H2O,CH4,O2])
        
        Rxn1=Reaction('Rxn1',[CH4,O2,CO2,H2O],[-1,-2,1,2])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(0.0022)
        F1.Sol=0.0020844938769
        T1=Sensor(25)
        T1.Sol=24.9999990371548
        P1=Sensor(105)
        P1.Sol=102.3781145505173
        CH4_R=Sensor(0.339)
        CH4_R.Sol=0.3333333333333
        O2_R=Sensor(0.672)
        O2_R.Sol=0.6666666666667
        CTag={CH4:CH4_R,O2:O2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(0.00199)
        F2.Sol= 0.0020844938769
        T2=Sensor(120)
        T2.Sol=119.9999919285024
        P2=Sensor(100)
        P2.Sol=102.3781145505173
        H2O_P=Sensor(0.673)
        H2O_P.Sol=0.6666666666667
        CO2_P=Sensor(0.335)
        CO2_P.Sol=0.3333333333333
        CTag={CO2:CO2_P,H2O:H2O_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',100)
        E.Q.Flag=0
        E.Q.Sol=548.3308630808275
        ListStreams.append(E)
        
        REX=Reactor('REX',S1,S2,[E],[Rxn1],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:0.0006948312923}
        ListUnits.append(REX)
        self.SetSigma(ListStreams,0.01)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
        self.OPT.ObjSol=66.560857591475283
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    Ctol=1e-5
    T1=Test17(1e-5,1)
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
function [Xopt,Fval,Flag]=ExtentReactionReactor()
    FR=0.0022;
    TR=25;
    PR=105;
    CH4_R=0.339;
    O2_R=0.672;
    FP=0.00199;
    TP=120;
    PP=100;
    CO2_P=0.335;
    H2O_P=0.673;
    Q=100;
    Xmeas=[FR;TR;PR;CH4_R;O2_R;FP;TP;PP;CO2_P;H2O_P;Q;2.1];
    XFlag=ones(12,1);
    XFlag([11,12])=0;
    LB=zeros(12,1);
    UB=ones(12,1);
    UB([1,2,3,6,7,8,11,12])=inf;
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
    Q=X(11);
    Ext=X(12);
    C1=FR*CH4_R - Ext; % CH4 balance
    C2=FR*O2_R - 2*Ext; % O2 Balance
    C3= -FP*CO2_P + Ext; % CO2 Balance
    C4= -FP*H2O_P + 2*Ext; % H20 Balance
    C5=CH4_R+O2_R-1.0;
    C6=CO2_P+H2O_P-1.0;
    HosR=OffSetR(CH4_R,O2_R);
    HR=refpropm('H<','T',TR+273,'P',PR,'methane','oxygen','CO2','water',[CH4_R,O2_R,0,0])+HosR;
    HosP=OffSetP(CO2_P,H2O_P);
    HP=refpropm('H<','T',TP+273,'P',PP,'methane','oxygen','CO2','water',[0,0,CO2_P,H2O_P])+HosP;
    C7=FR*HR-Q-FP*HP;
    C8=PR-PP;
    
    Ceq=[C1;C2;C3;C4;C5;C6;C7;C8];
    C=[];
end
function Hos=OffSetR(CH4_R,O2_R)
    Hos=CH4_R*-89098.91450281386+O2_R*-8666.33550895689;
end
function Hos=OffSetP(CO2_P,H2O_P)
    Hos=CO2_P*-415568.87614272034+H2O_P*-285995.1604551062;
end
'''