''' Mixer Example'''
import sys
import os
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ".."))
if filepath not in sys.path:
    sys.path.append(filepath)

from numpy import *
from Component.Comp import Comp
from Thermo.Refprop import Refprop
from Sensor.Sensor import Sensor
from Streams.Material_Stream import Material_Stream
from Units.Splitter import Splitter
from Units.Mixer import Mixer
from optim.ipopt import ipopt
from GrossErrorDetection.GLRTest import GLR


class Test14():
    def __init__(self,Ctol=1e-5,Ptol=1):
        self.Description='Mixer Example'
        self.Type=7
        H2=Comp(4,StdState=2)
        CO=Comp(1,StdState=2)
        Therm=Refprop([H2,CO])
        
        ListStreams=[]
        ListUnits=[]
        
        '''Define stream1'''
        F1=Sensor(102.0)
        F1.Sigma=0.01*F1.Meas
        F1.Sol=103.9639897368061
        T1=Sensor(25)
        T1.Sigma=0.01*T1.Meas
        T1.Sol=25.0638451629384
        P1=Sensor(105)
        P1.Sigma=0.01*P1.Meas
        P1.Sol=100.4878883377671
        H2_S1=Sensor(0.55)
        H2_S1.Sigma=0.01*H2_S1.Meas
        H2_S1.Sol=0.5118066340514
        CO_S1=Sensor(0.49)
        CO_S1.Sigma=0.01*CO_S1.Meas
        CO_S1.Sol=0.4881933659486
        CTag={H2:H2_S1,CO:CO_S1}
        S1=Material_Stream('S1',F1,T1,P1,1,Therm,CTag)
        ListStreams.append(S1)
        
        '''Define stream2'''
        F2=Sensor(50)
        F2.Sigma=0.01*F2.Meas
        F2.Sol=49.4569784634372
        T2=Sensor(23)
        T2.Sigma=0.01*T2.Meas
        T2.Sol=22.9742906118456
        P2=Sensor(102)
        P2.Sigma=0.01*P2.Meas
        P2.Sol=104.1290022192904
        H2_S2=Sensor(0.50)
        H2_S2.Sigma=0.01*H2_S2.Meas
        H2_S2.Sol=0.4851066065855
        CO_S2=Sensor(0.55)
        CO_S2.Sigma=0.01*CO_S2.Meas
        CO_S2.Sol=0.5148933934145
        CTag={H2:H2_S2,CO:CO_S2}
        S2=Material_Stream('S2',F2,T2,P2,1,Therm,CTag)
        ListStreams.append(S2)
        
        '''Define stream3'''
        F3=Sensor(55)
        F3.Sigma=0.01*F3.Meas
        F3.Sol=54.5070112733689
        T3=Sensor(27)
        T3.Sigma=0.01*T3.Meas
        T3.Sol=26.9609589817538
        P3=Sensor(95)
        P3.Sigma=0.01*P3.Meas
        P3.Sol= 96.8467744562437
        H2_S3=Sensor(0.55)
        H2_S3.Sigma=0.01*H2_S3.Meas
        H2_S3.Sol=0.5360329244405
        CO_S3=Sensor(0.49)
        CO_S3.Sigma=0.01*CO_S3.Meas
        CO_S3.Sol=0.4639670755595
        CTag={H2:H2_S3,CO:CO_S3}
        S3=Material_Stream('S3',F3,T3,P3,1,Therm,CTag)
        ListStreams.append(S3)
        
        '''Define Splitter1'''
        MIX=Mixer('MIX',[S2,S3],S1)
        ListUnits.append(MIX)
        self.OPT=ipopt(ListStreams,ListUnits,self.Type,5,1e-8,iter=5000)
        self.OPT.ObjSol=416.3467
        self.TestResult=self.OPT.CompareEstSol(Ctol)
        if (not self.TestResult):
            self.TestResultPercentage=self.OPT.CompareEstSolPercent(Ptol)
        #self.GLR1=GLR(self.OPT)
#=============================================================
if __name__ == "__main__":
    T1=Test14(1e-5,1)
    for i in T1.OPT.ListStreams:
        print '========================='
        print 'Stream Name: ',i.Name
        print '========================='
        print 'Flow :',i.FTag.Meas,i.FTag.Est
        print 'Temp :',i.TTag.Meas, i.TTag.Est
        print 'Press:',i.PTag.Meas,i.PTag.Est
        for j in i.CTag.keys():
            print j.Name,' : ',i.CTag[j].Meas,i.CTag[j].Est
    print T1.TestResult 
    if (not T1.TestResult):
            print T1.TestResultPercentage
#==============Matlab==============================
'''
function [Xopt,Fval,Flag]=MixerExample()
    FS1=102;
    TS1=25;
    PS1=105;
    COS1=0.49;
    HS1=0.55;
    FS2=50;
    TS2=23;
    PS2=102;
    COS2=0.55;
    HS2=0.50;
    FS3=55;
    TS3=27;
    PS3=95;
    COS3=0.49;
    HS3=0.55;
    Xmeas=[FS1;TS1;PS1;COS1;HS1;FS2;TS2;PS2;COS2;HS2;FS3;TS3;PS3;COS3;HS3];
    XFlag=ones(15,1);
    opt=optimset('algorithm','interior-point','display','iter','TolX',1e-12,'TolFun',1e-8);
    LB=zeros(15,1);
    UB=ones(16,1);
    UB([1,2,3,6,7,8,11,12,13])=inf;
    [Xopt,Fval,Flag]=fmincon(@obj,Xmeas,[],[],[],[],LB,UB,@Cons,opt,Xmeas,XFlag);
end
function f=obj(X,Xmeas,XFlag)
    Sigma=0.01*Xmeas;
    f=sum((((X-Xmeas)./Sigma).^2).*XFlag);
end
function [c,ceq]=Cons(X,Xmeas,XFlag)
    FS1=X(1);
    TS1=X(2);
    PS1=X(3);
    COS1=X(4);
    HS1=X(5);
    FS2=X(6);
    TS2=X(7);
    PS2=X(8);
    COS2=X(9);
    HS2=X(10);
    FS3=X(11);
    TS3=X(12);
    PS3=X(13);
    COS3=X(14);
    HS3=X(15);
    C1=FS1-FS2-FS3;
    C2=FS1*COS1-FS2*COS2-FS3*COS3;
    C3=COS1+HS1-1;
    C4=COS2+HS2-1;
    C5=COS3+HS3-1;
    C6=PS1-(PS2+PS3)/2;
    H1=refpropm('H>','T',TS1+273,'P',PS1,'CO','hydrogen',[COS1,HS1]);
    H2=refpropm('H>','T',TS2+273,'P',PS2,'CO','hydrogen',[COS2,HS2]);
    H3=refpropm('H>','T',TS3+273,'P',PS3,'CO','hydrogen',[COS3,HS3]);
    C7=FS1*H1-(FS2*H2+FS3*H3);
    ceq=[C1;C2;C3;C4;C5;C6;C7];
    c=[];
end
'''
