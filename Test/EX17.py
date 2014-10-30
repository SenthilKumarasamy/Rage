'''Extent of reaction reactor example where the concentration of the reactant stream is 
measured in CO free basis. Solution obtained from Matlab'''
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
        self.Description='Extent of reaction reactor example where the concentration of the reactant stream is measured in CO free basis. Solution obtained from Matlab'   
        self.Type=7
        O2=Comp(6,StdState=2)
        CO2=Comp(2,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        
        Therm=Refprop([CO2,H2O,CH4,O2])
        
        Rxn1=Reaction('Rxn1',[CH4,O2,CO2,H2O],[-1,-2,1,2])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10)
        F1.Sol=12.235595008942528
        T1=Sensor(25)
        T1.Sol=25
        P1=Sensor(105)
        P1.Sol=100
        CH4_R=Sensor(0.339)
        CH4_R.Sol=0.33
        O2_R=Sensor(0.672)
        O2_R.Sol=0.67
        CTag={CH4:CH4_R,O2:O2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(10)
        F2.Sol=11.823438396858114
        T2=Sensor(120)
        T2.Sol=50
        P2=Sensor(100)
        P2.Sol=100
        H2O_P=Sensor(0.673)
        H2O_P.Sol=0.67
        CO2_P=Sensor(0.335)
        CO2_P.Sol=0.33
        CTag={CO2:CO2_P,H2O:H2O_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',100)
        E.Q.Flag=0
        E.Q.Sol=100
        ListStreams.append(E)
        
        REX=Reactor('REX',S1,S2,[E],[Rxn1],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:1.771793249311506}
        ListUnits.append(REX)
        self.SetSigma(ListStreams,0.01)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
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
function [Xopt,Fval,Flag]=ExtentReactionReactorDryBasis()
    FlowR=12.11;
    COR=0.32;
    H2OR=0.35/(1-COR);
    CO2R=0.09/(1-COR);
    H2R=0.085/(1-COR);
    CH4R=0.084/(1-COR);
    C2H6R=0.087/(1-COR);
    FlowP=11.95;
    COP=0.07;
    H2OP=0.25;
    CO2P=0.22;
    H2P=0.22;
    CH4P=0.17;
    C2H6P=0.08;
    Xmeas=[FlowR;COR;H2OR;CO2R;H2R;CH4R;C2H6R;FlowP;COP;H2OP;CO2P;H2P;CH4P;C2H6P;2.1;1.2];
    XFlag=ones(16,1);
    XFlag([2,15,16])=0;
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],zeros(11,0),[],@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    COR=X(2);
    f=XFlag(1)*((X(1)-Xmeas(1))/Sigma(1))^2;
    for i=3:7
        f=f+XFlag(i)*((X(i)/(1-COR)-Xmeas(i))/Sigma(i))^2;
    end
    for i=8:14
        f=f+XFlag(i)*((X(i)-Xmeas(i))/Sigma(i))^2;
    end
end
function [C,Ceq] = Cons(X,Xmeas,XFlag)
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
    Ext1=X(15);
    Ext2=X(16);

    C1=FlowR * COR - FlowP * COP - Ext1 - Ext2; % CO balance
    C2=FlowR*H2OR - FlowP*H2OP - Ext1 + Ext2; % H2O Balance
    C3=FlowR*CO2R - FlowP*CO2P + Ext1; % CO2 Balance
    C4=FlowR*H2R - FlowP*H2P + Ext1 -3*Ext2; % H2 Balance
    C5=FlowR*CH4R - FlowP*CH4P +Ext2; % CH4 Balance
    C6=FlowR*C2H6R - FlowP*C2H6P; % C2H6 Balance
    C7=COR+H2OR+CO2R+H2R+CH4R+C2H6R-1.0;
    C8=COP+H2OP+CO2P+H2P+CH4P+C2H6P-1.0;

    Ceq=[C1;C2;C3;C4;C5;C6;C7;C8];
    C=[];
end
'''