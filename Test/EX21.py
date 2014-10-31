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
from Units.Reactor import Reactor
from optim.ipopt import ipopt
from Thermo.Refprop import Refprop
from EX15 import Test15
class Test21(Test15):
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Reactor (Equilibrium Reactor with two Reactions)'   
        self.Type=7
        H2=Comp(4,StdState=2)
        CO2=Comp(2,StdState=2)
        CO=Comp(1,StdState=2)
        H2O=Comp(7,StdState=1)
        CH4=Comp(5,StdState=2)
        
        Therm=Refprop([CO,H2O,CO2,H2,CH4])
        
        Rxn1=Reaction('Rxn1',[CO,H2O,CO2,H2],[-1,-1,1,1])
        Rxn2=Reaction('Rxn2',[CO,H2,CH4,H2O],[-1,-3,1,1])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(11.2)
        F1.Sol=1.120230432949998e+01
        T1=Sensor(530)
        T1.Sol=5.300000161154702e+02
        P1=Sensor(106)
        P1.Sol=1.062850908282309e+02
        CO_R=Sensor(0.41)
        CO_R.Sol=4.082164934803849e-01
        H2O_R=Sensor(0.25)
        H2O_R.Sol=2.458901992917100e-01
        H2_R=Sensor(0.35)
        H2_R.Sol=3.458933072279052e-01
        CTag={CO:CO_R,H2O:H2O_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(8.8)
        F2.Sol= 8.798189083164068e+00
        T2=Sensor(564)
        T2.Sol=5.654782593720630e+02
        P2=Sensor(106)
        P2.Sol=1.062850908282309e+02
        CO_P=Sensor(0.14)
        CO_P.Sol=1.354941078542647e-01
        H2O_P=Sensor(0.21)
        H2O_P.Sol=2.020631134323766e-01
        CO2_P=Sensor(0.25)
        CO2_P.Sol=2.476424373208237e-01
        H2_P=Sensor(0.28)
        H2_P.Sol=2.781747685836742e-01
        CH4_P=Sensor(0.14)
        CH4_P.Sol=1.366255728088608e-01
        
        CTag={CO:CO_P,H2O:H2O_P,CO2:CO2_P,H2:H2_P,CH4:CH4_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        E=Energy_Stream('E',337000)
        E.Q.Flag=0
        E.Q.Sol=3.359022642710555e+05
        ListStreams.append(E)
        
        REX=EquilibriumReactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        #REX=Reactor('REX',S1,S2,[E],[Rxn1,Rxn2],ExoEndoFlag=-1)
        REX.RxnExtSol={Rxn1:2.178804988564214e+00,Rxn2:1.202057623167956e+00}
        ListUnits.append(REX)
        self.SetSigma(ListStreams,0.01)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-6,iter=5000)
        self.OPT.ObjSol=3.624954316957449e+01
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
#===============================================================================
if __name__=="__main__":
    Ctol=1e-5
    T1=Test21(1e-5,1)
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
    for i in T1.OPT.ListUints:
        print '========================='
        print 'Unit Name: ',i.Name
        print '========================='
        for j in i.Rxn:
            print 'Extent of Reaction ',j.Name,': ',i.RxnExt[j]
    print T1.TestResult 
    if (not T1.TestResult):
            print T1.TestResultPercentage 
#=================MatLab Code=============================== 
'''
function [Xopt,Fval,Flag]=EquilibriumReactorWithTwoReactions()
    FR=11.2;
    TR=530;
    PR=106;
    CO_R=0.41;
    H2O_R=0.25;
    H2_R=0.35;
    
    FP=8.8;
    TP=564;
    PP=106;
    CO_P=0.14;
    H2O_P=0.21;
    CO2_P=0.25;
    H2_P=0.28;
    CH4_P=0.14;
    
    Q=337000;
    Ext1=2.18;
    Ext2=1.2;
    Xmeas=[FR;TR;PR;CO_R;H2O_R;H2_R;FP;TP;PP;CO_P;H2O_P;CO2_P;H2_P;CH4_P;Q;Ext1;Ext2];
    XFlag=ones(17,1);
    XFlag([15,16,17])=0;
    LB=zeros(17,1);
    UB=ones(17,1)*inf;
    UB([4,5,6,10,11,12,13,14])=1;
    opt=optimset('algorithm','interior-point','display','iter');
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [C,Ceq] = Cons(X,Xmeas,XFlag)
    % CO + H2O -----> CO2 + H2
    % CO + H2 ------> CH4 + H2O
    FR=X(1);
    TR=X(2);
    PR=X(3);
    CO_R=X(4);
    H2O_R=X(5);
    H2_R=X(6);
    
    FP=X(7);
    TP=X(8);
    PP=X(9);
    CO_P=X(10);
    H2O_P=X(11);
    CO2_P=X(12);
    H2_P=X(13);
    CH4_P=X(14);
    
    Q=X(15);
    Ext1=X(16);
    Ext2=X(17);
    C1=FR*CO_R - Ext1 - Ext2 - FP*CO_P; % CO balance
    C2=FR*H2O_R - Ext1 + Ext2 - FP*H2O_P; % H2O Balance
    C3= -FP*CO2_P + Ext1; % CO2 Balance
    C4=FR*H2_R + Ext1 - 3*Ext2 - FP*H2_P; % H2 Balance
    C5= -FP*CH4_P + Ext2;
    C6=CO_R + H2O_R + H2_R -1.0; % Normalization
    C7=CO_P + H2O_P + CO2_P + H2_P  +CH4_P - 1.0; % Normalization
    HosR=OffSetR(CO_R,H2O_R,H2_R);
    HR=refpropm('H<','T',TR+273,'P',PR,'CO','water','CO2','hydrogen','methane',[CO_R,H2O_R,0,H2_R,0])+HosR;
    HosP=OffSetP(CO_P,H2O_P,CO2_P,H2_P,CH4_P);
    HP=refpropm('H<','T',TP+273,'P',PP,'CO','water','CO2','hydrogen','methane',[CO_P,H2O_P,CO2_P,H2_P,CH4_P])+HosP;
    C8=FR*HR-Q-FP*HP; % Energy balance
    C9=PR-PP;
    C=EC(TP,PP,CO_P,H2O_P,CO2_P,H2_P,CH4_P);% Equilibrium Constraints
    C10=C(1);
    C11=C(2);
    Ceq=[C1;C2;C3;C4;C5;C6;C7;C8;C9;C10;C11];
    C=[];
end
function Hos=OffSetR(CO_R,H2O_R,H2_R)
    Hos=CO_R*-122813.37690204574+H2O_R*-285995.1604551062+H2_R*-7963.037870345514;
end
function Hos=OffSetP(CO_P,H2O_P,CO2_P,H2_P,CH4_P)
    Hos=CO_P*-122813.37690204574+H2O_P*-285995.1604551062+CO2_P*-415568.8760894639+H2_P*-7963.037870345514+CH4_P*-89098.91450281504;
end
function C=EC(TP,PP,CO_P,H2O_P,CO2_P,H2_P,CH4_P)
    R=8.314;
    CO_Hos=-122813.37690204574;
    H2O_Hos=-285995.1604551062;
    CO2_Hos=-415568.8760894639;
    H2_Hos=-7963.037870345514;
    CH4_Hos=-89098.91450281504;
    
    CO_Sos=-21.53856518258297;
    H2O_Sos=-165.63852216324867;
    CO2_Sos=-116.76001784087575;
    H2_Sos=-109.68429686419977;
    CH4_Sos=-187.77311250193037;
    
    CO_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[1,0,0,0,0])+CO_Hos;
    H2O_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,1,0,0,0])+H2O_Hos;
    CO2_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,1,0,0])+CO2_Hos;
    H2_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,0,1,0])+H2_Hos;
    CH4_H=refpropm('H<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,0,0,1])+CH4_Hos;
    
    CO_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[1,0,0,0,0])+CO_Sos;
    H2O_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,1,0,0,0])+H2O_Sos;
    CO2_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,1,0,0])+CO2_Sos;
    H2_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,0,1,0])+H2_Sos;
    CH4_S=refpropm('S<','T',TP+273,'P',100,'CO','water','CO2','hydrogen','methane',[0,0,0,0,1])+CH4_Sos;
    
    CO_G=CO_H-(TP+273)*CO_S;
    H2O_G=H2O_H-(TP+273)*H2O_S;
    CO2_G=CO2_H-(TP+273)*CO2_S;
    H2_G=H2_H-(TP+273)*H2_S;
    CH4_G=CH4_H-(TP+273)*CH4_S;

    dG1=CO2_G+H2_G-(CO_G+H2O_G);
    dG2=CH4_G+H2O_G-(CO_G+3*H2_G);
    
    T=TP+273;
    K1=exp(-dG1/(R*T));
    K2=exp(-dG2/(R*T));
    F=(refpropm('F<','T',TP+273,'P',PP,'CO','water','CO2','hydrogen','methane',[CO_P,H2O_P,CO2_P,H2_P,CH4_P])/100.0);
    CO_F=F(1);
    H2O_F=F(2);
    CO2_F=F(3);
    H2_F=F(4);
    CH4_F=F(5);
    
    RHS1=CO2_F*H2_F/(CO_F*H2O_F);
    C1=1-RHS1/K1;
    RHS2=CH4_F*H2O_F/(CO_F*H2_F^3);
    C2=1-RHS2/K2;
    C=[C1;C2];
end
'''
