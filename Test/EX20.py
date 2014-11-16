'''Equilibrium reactor example '''
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
from Units.EquilibriumReactor import EquilibriumReactor
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test20(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Reactor (Equilibrium Reactor)'   
        self.Type=5
        H2=Comp(4,StdState=2)
        CO2=Comp(2,StdState=2)
        CO=Comp(1,StdState=2)
        H2O=Comp(7,StdState=1)
        
        Therm=Refprop([CO,H2O,CO2,H2])
        
        Rxn1=Reaction('Rxn1',[CO,H2O,CO2,H2],[-1,-1,1,1],EquTempAppFlag=1,EquTempApp=0.0)
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.1)
        F1.Sol=1.014950732329255e+01
        T1=Sensor(530)
        T1.Sol=5.299999498891710e+02
        P1=Sensor(105)
        P1.Sol=1.023777721614761e+02
        CO_R=Sensor(0.51)
        CO_R.Sol=4.991175688113909e-01
        H2O_R=Sensor(0.52)
        H2O_R.Sol=5.008824311886092e-01
        CTag={CO:CO_R,H2O:H2O_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(10.2)
        F2.Sol=1.014950732329255e+01
        T2=Sensor(825)
        T2.Sol=7.625035354996178e+02
        P2=Sensor(100)
        P2.Sol=1.023777721614761e+02
        CO_P=Sensor(0.25)
        CO_P.Sol=2.547948265188097e-01
        H2O_P=Sensor(0.25)
        H2O_P.Sol=2.565596888960282e-01
        CO2_P=Sensor(0.25)
        CO2_P.Sol=2.443227422925811e-01
        H2_P=Sensor(0.25)
        H2_P.Sol=2.443227422925811e-01
        
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',100)
        E.Q.Flag=0
        E.Q.Sol=3.370369036550214e+03
        ListStreams.append(E)
        
        REX=EquilibriumReactor('REX',S1,S2,[E],[Rxn1],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:2.479755462145470e+00}
        ListUnits.append(REX)
        self.SetSigma(ListStreams,0.01)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-6,iter=0)
        self.OPT.ObjSol=1.087081886709052e+02
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    Ctol=1e-5
    T1=Test20(1e-5,1)
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
#=================MatLab Code=============================== 
'''
function [Xopt,Fval,Flag]=EquilibriumReactor()
    FR=10.1;
    TR=530;
    PR=105;
    CO_R=0.51;
    H2O_R=0.52;
    FP=10.2;
    TP=825;
    PP=100;
    CO_P=0.25;
    H2O_P=0.25;
    CO2_P=0.25;
    H2_P=0.25;
    Q=100;
    Ext=2.6;
    Xmeas=[FR;TR;PR;CO_R;H2O_R;FP;TP;PP;CO_P;H2O_P;CO2_P;H2_P;Q;Ext];
    XFlag=ones(14,1);
    XFlag([13,14])=0;
    LB=zeros(14,1);
    UB=ones(14,1)*inf;
    %UB([1,2,3,6,7,8,13,14])=inf;
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [C,Ceq] = Cons(X,Xmeas,XFlag)
    % CO + H2O -----> CO2 + H2
    FR=X(1);
    TR=X(2);
    PR=X(3);
    CO_R=X(4);
    H2O_R=X(5);
    FP=X(6);
    TP=X(7);
    PP=X(8);
    CO_P=X(9);
    H2O_P=X(10);
    CO2_P=X(11);
    H2_P=X(12);
    Q=X(13);
    Ext=X(14);
    C1=FR*CO_R - Ext - FP*CO_P; % CO balance
    C2=FR*H2O_R - Ext - FP*H2O_P; % H2O Balance
    C3= -FP*CO2_P + Ext; % CO2 Balance
    C4= -FP*H2_P + Ext; % H2 Balance
    C5=CO_R+H2O_R-1.0; % Normalization
    C6=CO_P+H2O_P+CO2_P+H2_P-1.0; % Normalization
    HosR=OffSetR(CO_R,H2O_R);
    HR=refpropm('H<','T',TR+273,'P',PR,'CO','water','CO2','hydrogen',[CO_R,H2O_R,0,0])+HosR;
    HosP=OffSetP(CO_P,H2O_P,CO2_P,H2_P);
    HP=refpropm('H<','T',TP+273,'P',PP,'CO','water','CO2','hydrogen',[CO_P,H2O_P,CO2_P,H2_P])+HosP;
    C7=FR*HR-Q-FP*HP; % Energy balance
    C8=PR-PP;
    C9=EC(TP,PP,CO_P,H2O_P,CO2_P,H2_P);% Equilibrium Constraints
    Ceq=[C1;C2;C3;C4;C5;C6;C7;C8;C9];
    C=[];
end
function Hos=OffSetR(CO_R,H2O_R)
    Hos=CO_R*-122813.37690204574+H2O_R*-285995.1604551062;
end
function Hos=OffSetP(CO_P,H2O_P,CO2_P,H2_P)
    Hos=CO_P*-122813.37690204574+H2O_P*-285995.1604551062+CO2_P*-415568.8760894639+H2_P*-7963.037870345514;
end
function C=EC(TP,PP,CO_P,H2O_P,CO2_P,H2_P)
    R=8.314;
    CO_Hos=-122813.37690204574;
    H2O_Hos=-285995.1604551062;
    CO2_Hos=-415568.8760894639;
    H2_Hos=-7963.037870345514;
    
    CO_Sos=-21.53856518258297;
    H2O_Sos=-165.63852216324867;
    CO2_Sos=-116.76001784087575;
    H2_Sos=-109.68429686419977;
    
    CO_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[1,0,0,0])+CO_Hos;
    H2O_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,1,0,0])+H2O_Hos;
    CO2_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,0,1,0])+CO2_Hos;
    H2_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,0,0,1])+H2_Hos;
    
    CO_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[1,0,0,0])+CO_Sos;
    H2O_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,1,0,0])+H2O_Sos;
    CO2_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,0,1,0])+CO2_Sos;
    H2_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen',[0,0,0,1])+H2_Sos;
    
    CO_G=CO_H-(TP+273)*CO_S;
    H2O_G=H2O_H-(TP+273)*H2O_S;
    CO2_G=CO2_H-(TP+273)*CO2_S;
    H2_G=H2_H-(TP+273)*H2_S;

    dG=CO2_G+H2_G-(CO_G+H2O_G);
    T=TP+273;
    K=exp(-dG/(R*T));
    F=(refpropm('F<','T',TP+273,'P',PP,'CO','water','CO2','hydrogen',[CO_P,H2O_P,CO2_P,H2_P])/100.0);
    RHS=F(3)*F(4)/(F(1)*F(2));
    C=1-RHS/K;
end
'''
