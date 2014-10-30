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
class Test15():
    def __init__(self,Ctol=1e-5,Ptol=2):
        self.Description='Separator example. Solution obtained by solving in Matlab'
        self.Type=7   
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
                
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        F1=Sensor(10.9547)
        F1.Sol=10.027127629273942
        T1=Sensor(50)
        T1.Sol=42.402885721169845
        P1=Sensor(100)
        P1.Sol=99.997097302836366
        CO_R=Sensor(0.4822)
        CO_R.Sol=0.481089103331390
        H2_R=Sensor(0.5170)
        H2_R.Sol=0.518910896668609
        CTag={CO:CO_R,H2:H2_R}
        S1=Material_Stream('S1',F1,T1,P1,2,Therm,CTag)
        ListStreams.append(S1)
        
        F2=Sensor(4.7840)
        F2.Sol=4.973594641466226
        T2=Sensor(40)
        T2.Sol=42.422166520952864
        P2=Sensor(100)
        P2.Sol=99.997097302836366
        CO_P=Sensor(0.9410)
        CO_P.Sol=0.949889188600976
        H2_P=Sensor(0.0501)
        H2_P.Sol=0.050110811399024
        CTag={CO:CO_P,H2:H2_P}
        S2=Material_Stream('S2',F2,T2,P2,2,Therm,CTag)
        ListStreams.append(S2)
        
        F3=Sensor(4.8823)
        F3.Sol=5.053532987807715
        T3=Sensor(40)
        T3.Sol=42.440879165103077
        P3=Sensor(100)
        P3.Sol=99.997097302836366
        CO_R1=Sensor(0.0197)
        CO_R1.Sol=0.019704642669701
        H2_R1=Sensor(0.9748)
        H2_R1.Sol=0.980295357330299
        CTag={CO:CO_R1,H2:H2_R1}
        S3=Material_Stream('S3',F3,T3,P3,2,Therm,CTag)
        ListStreams.append(S3)
        self.SetSigma(ListStreams,0.01)
        

        SEP=Seperator('SEP',S1,[S2,S3])
        ListUnits.append(SEP)
        
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=500)
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
    
    def SetSigma(self,ListStreams,Percentage):
        for i in ListStreams:
            if (not (isinstance(i,Energy_Stream))):
                if (not (Percentage==0.0)):
                    if (not(i.FTag.Meas==0.0)):
                        i.FTag.Sigma=i.FTag.Meas*Percentage
                    else:
                        i.FTag.Sigma=1.0
                    if (not (i.TTag.Meas==0.0)):
                        i.TTag.Sigma=i.TTag.Meas*Percentage
                    else:
                        i.TTag.Sigma=1.0
                    if (not(i.PTag.Meas==0)):
                        i.PTag.Sigma=i.PTag.Meas*Percentage
                    else:
                        i.PTag.Sigma=1.0
                    for j in i.CTag.keys():
                        if (not (i.CTag[j].Meas==0.0)):
                            i.CTag[j].Sigma=i.CTag[j].Meas*Percentage
                        else:
                            i.CTag[j].Sigma=1.0
                else:
                    i.FTag.Sigma=1.0
                    i.TTag.Sigma=1.0
                    i.PTag.Sigma=1.0
                    for j in i.CTag.keys():
                        i.CTag[j].Sigma=1.0
            else:
                i.Q.Sigma=1.0
                    
                
#===============================================================================
if __name__ == "__main__":
    T1=Test15(1e-4,1)
    for i in T1.OPT.ListStreams:
        print '========================='
        print 'Stream Name: ',i.Name
        print '========================='
        print 'Flow :',i.FTag.Meas,i.FTag.Est,i.FTag.Sigma
        print 'Temp :',i.TTag.Meas, i.TTag.Est,i.TTag.Sigma
        print 'Press:',i.PTag.Meas,i.PTag.Est,i.PTag.Sigma
        for j in i.CTag.keys():
            print j.Name,' : ',i.CTag[j].Meas,i.CTag[j].Est,i.CTag[j].Sigma
    print T1.TestResult 
    if (not T1.TestResult):
            print T1.TestResultPercentage
#===================Matlab code=====================================
'''
function [Xopt,Fval,Flag]=SeparatorExample()
    F=10.9547;
    TF=50;
    PF=100;
    COF=0.4822;
    HF=0.5170;
    D=4.7840;
    TD=40;
    PD=100;
    COD=0.9410;
    HD=0.0501;
    B=4.8823;
    TB=40;
    PB=100;
    COB=0.0197;
    HB=0.9748;
    Xmeas=[F;TF;PF;COF;HF;D;TD;PD;COD;HD;B;TB;PB;COB;HB];
    XFlag=ones(15,1);
    opt=optimset('algorithm','interior-point','display','iter');
    LB=zeros(15,1);
    UB=ones(15,1);
    UB([1,2,3,6,7,8,11,12,13])=inf;
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
    
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    F=X(1);
    TF=X(2);
    PF=X(3);
    COF=X(4);
    HF=X(5);
    D=X(6);
    TD=X(7);
    PD=X(8);
    COD=X(9);
    HD=X(10);
    B=X(11);
    TB=X(12);
    PB=X(13);
    COB=X(14);
    HB=X(15);
    C1=F-B-D;
    C2=F*COF-D*COD-B*COB;
    C3=COF+HF-1;
    C4=COD+HD-1;
    C5=COB+HB-1;
    H1=refpropm('H>','T',TF+273,'P',PF,'CO','hydrogen',[COF,HF]);
    H2=refpropm('H>','T',TD+273,'P',PD,'CO','hydrogen',[COD,HD]);
    H3=refpropm('H>','T',TB+273,'P',PB,'CO','hydrogen',[COB,HB]);
    C6=F*H1-(D*H2+B*H3);
    C7=PF-PD;
    C8=PF-PB;
    ceq=[C1;C2;C3;C4;C5;C6;C7;C8];
    c=[];
end

'''
