from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
from numpy import float_
import pyipopt
import collections as Con
from scipy.optimize import minimize
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Streams.FixedConcStream import FixedConcStream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.EquilibriumReactor import EquilibriumReactor
from Units.ElementBalanceReactor import ElementBalanceReactor
from Units.AdiabaticElementBalanceReactor import AdiabaticElementBalanceReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Reactor import Reactor
from Units.Mixer import Mixer

class myslsqp:
    ListStreams=[]
    ListUints=[]
    Xmeas=[]
    X=[]
    XFlag=[]
    Sigma=[]
    Xlen=0
    XLB=[]
    XUB=[]
    Normlen=0
    nnzj=0
    nnzh=0
    CFlag=5

    def __init__(self,ListStreams,ListUnits,CFlag=1):
        self.CFlag=CFlag
        self.ListStreams=ListStreams
        self.ListUints=ListUnits
        self.ConstructXFlag()
        self.Xmeas=self.X
        Bound=tuple(zip(self.XLB,self.XUB))
        self.JacobianSize()
        if (self.CFlag==5 or self.CFlag==6 or self.CFlag==7):
            self.JacoNorm()
        Con_eq=({"type":"eq","fun":self.Constraints,"jac":self.ConstructJaco})
        result=minimize(self.Objective,self.Xmeas,method='SLSQP',bounds=Bound,constraints=Con_eq,options={'maxiter':10000,'disp':'True'})
#--------------------------Methods called once during initialisation of the object-------------    
    def ConstructXFlag(self):   
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2): # Flag==2 means constant
                    if (i.FTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    i.FTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.FTag.Meas)
                    self.Sigma.append(i.FTag.Sigma)
                
                if (i.TTag.Flag !=2):    
                    if (i.TTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    i.TTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.TTag.Meas)
                    self.Sigma.append(i.TTag.Sigma)
               
                if (i.PTag.Flag !=2):    
                    if (i.PTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    i.PTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.PTag.Meas)
                    self.Sigma.append(i.PTag.Sigma)
                
                for j,val in enumerate(i.CTag.keys()):
                    if (i.CTag[val].Flag!=2):
                        if (i.CTag[val].Flag!=0):
                            self.XFlag.append(1)
                        else:
                            self.XFlag.append(0)
                        i.CTag[val].Xindex=len(self.XFlag)-1
                        self.X.append(i.CTag[val].Meas)
                        self.Sigma.append(i.CTag[val].Sigma)                                
            elif (isinstance(i,Energy_Stream)):
                #self.XFlag.append(0)
                #i.Xindex=len(self.XFlag)-1
                if (i.Q.Flag !=2):    
                    if (i.Q.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    i.Q.Xindex=len(self.XFlag)-1
                    self.X.append(i.Q.Meas)
                    self.Sigma.append(i.Q.Sigma) # Q is always unmeasured and sigma doesnot affect the objective as flag is zero
            else:
                print "Stream in the list is not defined"
                quit()
    #-------------------------------------------------------------    
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
                self.XFlag.append(0)
                i.UXindex=len(self.XFlag)-1
                self.X.append(i.U)
                self.Sigma.append(1)
            
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                for j in (i.RxnExt.keys()):
                    self.XFlag.append(0)
                    i.RxnExtXindex[j]=len(self.XFlag)-1
                    self.X.append(i.RxnExt[j])
                    self.Sigma.append(1)

            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater))):
                print "Object in the list is not defined"
                quit()
    #-------------------------------------------------------------------
        self.Xlen=len(self.XFlag)
        #self.XLB=asarray(self.X)*0.9#
        self.XLB=zeros((self.Xlen))
        #self.XUB=asarray(self.X)*1.1#
        self.XUB=ones((self.Xlen))*inf
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                for j,val in enumerate(i.CTag.keys()):
                    if (i.CTag[val].Flag!=2):
                        self.XUB[i.CTag[val].Xindex]=1.00001
    #---------------------------------------------------------------------
                
#-----------------------------Methods called several times by the optimiser-----------
    
    def Objective(self,X):
        assert len(X)==self.Xlen
        Obj=0
        for i in range(self.Xlen):
            Obj=Obj+self.XFlag[i]*((X[i]-self.Xmeas[i])/self.Sigma[i])**2
        return Obj


    def Constraints(self,X):
        assert len(X)==self.Xlen
        Resid=[]
        self.DeconstructX(X)
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                i.h=i.Therm.EnthalpyStream(i)
        if (self.CFlag==5 or self.CFlag==6 or self.CFlag==7):
            Resid.extend(self.addNormCons())
        for i in self.ListUints:
            if (self.CFlag==1):
                Resid.extend(i.MaterialBalRes())
            elif (self.CFlag==2 or self.CFlag==5):
                Resid.extend(i.MaterialBalRes())
                Resid.extend(i.ComponentBalRes())
            elif (self.CFlag==3 or self.CFlag==6):
                Resid.extend(i.MaterialBalRes())
                Resid.extend(i.ComponentBalRes())
                Resid.extend(i.EnergyBalRes())
            elif (self.CFlag==4 or self.CFlag==7):
                Resid.extend(i.MaterialBalRes())
                Resid.extend(i.ComponentBalRes())
                Resid.extend(i.EnergyBalRes())
                Resid.extend(i.PressureBalRes()) 
        return asarray(Resid,dtype=float_)
    
    #-------Methods called by the functions which are called by optimiser---------------------------

    def DeconstructX(self,X):
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2):
                    i.FTag.Est=X[i.FTag.Xindex]
                if (i.TTag.Flag!=2):
                    i.TTag.Est=X[i.TTag.Xindex]
                if (i.PTag.Flag!=2):
                    i.PTag.Est=X[i.PTag.Xindex]
                for k in i.CTag.keys():
                    if (i.CTag[k].Flag!=2):
                        i.CTag[k].Est=X[i.CTag[k].Xindex]
            elif(isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    i.Q.Est=X[i.Q.Xindex]            
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
                i.U=X[i.UXindex]
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                for k in i.RxnExt.keys():
                    i.RxnExt[k]=X[i.RxnExtXindex[k]]
            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater))):
                print "Object in the list is not defined"
                quit()   
    
    def addNormCons(self):
        NormCons=[]
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream)):
                sumC=0
                for ind in i.CTag.keys():
                    sumC=sumC+i.CTag[ind].Est
                NormCons.append(sumC-1)
        return NormCons
    
    def ConstructJaco(self,X):
        self.DeconstructX(X)
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                i.h=i.Therm.EnthalpyStream(i)
                i.GradDic=i.EnthalpyGradient()
        Jaco=zeros((self.Glen,self.Xlen))
        start=0
        if (self.CFlag==5 or self.CFlag==6 or self.CFlag==7):
            Jaco[start:self.Normlen][:]=self.JNorm
            start=start+self.Normlen
        for i in self.ListUints:
            if (self.CFlag==1):
                Jaco[start:start+i.LenMatRes][:]=i.MaterialBalJaco(self.Xlen)
                start=start+i.LenMatRes#1
            elif (self.CFlag==2 or self.CFlag==5):
                Jaco[start:start+ i.LenMatRes][:]=i.MaterialBalJaco(self.Xlen)
                start=start+ i.LenMatRes#1
                Jaco[start:start+i.LenCompRes][:]=i.ComponentBalJaco(self.Xlen)
                start=start+i.LenCompRes
            elif (self.CFlag==3 or self.CFlag==6):
                Jaco[start:start+i.LenMatRes][:]=i.MaterialBalJaco(self.Xlen)
                start=start+i.LenMatRes#1
                Jaco[start:start+i.LenCompRes][:]=i.ComponentBalJaco(self.Xlen)
                start=start+i.LenCompRes
                Jaco[start:start+i.LenEneRes][:]=i.EnergyBalJaco(self.Xlen)
                start=start+ i.LenEneRes#1
            elif (self.CFlag==4 or self.CFlag==7):
                Jaco[start:start+i.LenMatRes][:]=i.MaterialBalJaco(self.Xlen)
                start=start+i.LenMatRes#1
                Jaco[start:start+i.LenCompRes][:]=i.ComponentBalJaco(self.Xlen)
                start=start+i.LenCompRes
                Jaco[start:start+i.LenEneRes][:]=i.EnergyBalJaco(self.Xlen)
                start=start+ i.LenEneRes
                Jaco[start:start+i.LenPreRes][:]=i.PressureBalJaco(self.Xlen)
                start=start+ i.LenPreRes
        return Jaco
        
    def JacoNorm(self):
        self.JNorm=zeros((self.Normlen,self.Xlen))
        k=-1
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream)):
                k=k+1
                for ind in i.CTag.keys():
                    self.JNorm[k,i.CTag[ind].Xindex]=1
    
    def JacobianSize(self):
        self.Glen=0
        self.Normlen=0
        for i in self.ListUints:
            if (self.CFlag==1): # Only Material balance
                self.Glen=self.Glen+i.LenMatRes#1
            elif (self.CFlag==2 or self.CFlag==5): # Material and Comp balance
                self.Glen=self.Glen + i.LenCompRes + i.LenMatRes#1
            elif (self.CFlag==3 or self.CFlag==6): # Mat comp Eng bal
                self.Glen=self.Glen + i.LenCompRes + i.LenMatRes + i.LenEneRes
            elif (self.CFlag==4 or self.CFlag==7):
                self.Glen=self.Glen+i.LenCompRes + i.LenMatRes + i.LenEneRes + i.LenPreRes
        for i in self.ListStreams:
            if ((isinstance(i,Material_Stream)) and (self.CFlag==5 or self.CFlag==6 or self.CFlag==7)):
                self.Glen=self.Glen+1
                self.Normlen=self.Normlen+1

