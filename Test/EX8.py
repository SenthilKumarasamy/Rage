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
class Test8():
    def __init__(self,Ctol):   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
        CO2=Comp(2,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        C2H6=Comp(3,StdState=2)
        
        Therm=Refprop([H2,CO,CO2,H2O,CH4,C2H6])
        
        Rxn1=Reaction('Rxn1',[CO,H2O,CO2,H2],[-1,-1,1,1])
        Rxn2=Reaction('Rxn2',[CO,H2,CH4,H2O],[-1,-3,1,1])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(12.11)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=12.235595008942528
        T1=Sensor(25)
        T1.Sol=25
        P1=Sensor(100)
        P1.Sol=100
        CO_R=Sensor(0.32)
        CO_R.Flag=0
        CO_R.Sigma=0.01*CO_R.Meas
        CO_R.Sol=  0.229578624995014
        H2O_R=Sensor(0.35/(1.0-CO_R.Meas))
        H2O_R.Sigma=0.01*H2O_R.Meas
        H2O_R.Sol=0.379459609662103
        CO2_R=Sensor(0.09/(1.0-CO_R.Meas))
        CO2_R.Sigma=0.01*CO2_R.Meas
        CO2_R.Sol=0.096092065249691
        H2_R=Sensor(0.085/(1.0-CO_R.Meas))
        H2_R.Sigma=0.01*H2_R.Meas
        H2_R.Sol=  0.100521579278419
        CH4_R=Sensor(0.084/(1.0-CO_R.Meas))
        CH4_R.Sigma=0.01*CH4_R.Meas
        CH4_R.Sol=0.108718145526405
        C2H6_R=Sensor(0.087/(1.0-CO_R.Meas))
        C2H6_R.Sigma=0.01*C2H6_R.Meas
        C2H6_R.Sol=0.085629975288367
        CTag={CO:CO_R,H2O:H2O_R,CO2:CO2_R,H2:H2_R,CH4:CH4_R,C2H6:C2H6_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag,FreeBasis=[CO])
        ListStreams.append(S1)
        
        F2=Sensor(11.95)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=11.823438396858114
        T2=Sensor(25)
        P2=Sensor(100)
        CO_P=Sensor(0.07)
        CO_P.Sigma=0.01*CO_P.Meas
        CO_P.Sol=0.070297615202701
        H2O_P=Sensor(0.25)
        H2O_P.Sigma=0.01*H2O_P.Meas
        H2O_P.Sol=0.260262629154082
        CO2_P=Sensor(0.22)
        CO2_P.Sigma=0.01*CO2_P.Meas
        CO2_P.Sol=0.249296079900316
        H2_P=Sensor(0.22)
        H2_P.Sigma=0.01*H2_P.Meas
        H2_P.Sol= 0.201591075699967
        CH4_P=Sensor(0.17)
        CH4_P.Sigma=0.01*CH4_P.Meas
        CH4_P.Sol=0.129937625017341
        C2H6_P=Sensor(0.08)
        C2H6_P.Sigma=0.01*C2H6_P.Meas
        C2H6_P.Sol=0.088614975025593
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P,C2H6:C2H6_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',0)
        E.Q.Flag=2
        ListStreams.append(E)
        
        REX=Reactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:1.771793249311506,Rxn2:0.206078306042207}
        ListUnits.append(REX)
        
        self.OPT=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=5000)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
#===============================================================================
if __name__=="__main__":
#     T4=Test8(1e-2)
#     for i in T4.OPT.ListStreams:
#         if (not isinstance(i,Energy_Stream)):
#             print i.FTag.Est
#             for j in i.CTag.keys():
#                 print j.Name[:-4],i.CTag[j].Est
#     print T4.TestResult
    Ctol=1e-3
    T4=Test8(Ctol)
    for i in T4.OPT.ListStreams:
        if (not isinstance(i,Energy_Stream)):
            print i.FTag.Est, abs(i.FTag.Est-i.FTag.Sol)<Ctol
            for j in i.CTag.keys():
                print j.Name[:-4],i.CTag[j].Est,abs(i.CTag[j].Est-i.CTag[j].Sol)<Ctol
    i=T4.OPT.ListUints[0]
    print i.RxnExt[i.Rxn[0]],i.RxnExt[i.Rxn[1]],abs(i.RxnExtSol[i.Rxn[0]]-i.RxnExt[i.Rxn[0]])<Ctol,abs(i.RxnExtSol[i.Rxn[1]]-i.RxnExt[i.Rxn[1]])<Ctol
    print T4.TestResult  
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