from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
from numpy import float_
import numpy as np
import pyipopt
import collections as Con

from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Streams.FixedConcStream import FixedConcStream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.EquilibriumReactor import EquilibriumReactor
from Units.EquilibriumReactor2 import EquilibriumReactor2
from Units.ElementBalanceReactor import ElementBalanceReactor
from Units.AdiabaticElementBalanceReactor import AdiabaticElementBalanceReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Reactor import Reactor
from Units.Mixer import Mixer
from Units.Pump import Pump

class ipopt:
#     ListStreams=[]
#     ListUints=[]
#     Xmeas=[]
#     X=[]
#     XFlag=[]
#     Sigma=[]
#     Xlen=0
#     XLB=[]
#     XUB=[]
#     Glen=0
#     GLB=[]
#     GUB=[]
#     Normlen=0
#     JNorm=[]
#     NonZeroJacoRow=[]
#     NonZeroJacoCol=[]
#     nnzj=0
#     nnzh=0
#     CFlag=5

    def __init__(self,ListStreams,ListUnits,CFlag=5,PrintOpt=0,Xtol=1e-6,iter=100):
        self.XFlag=[]
        self.X=[]
        self.Sigma=[]
        self.CFlag=CFlag
        self.ListStreams=ListStreams
        self.ListUints=ListUnits
        self.ConstructXFlag()
        #self.ConstructX()
        self.Xmeas=self.X
        self.JacobianSize()
        if (self.CFlag==5 or self.CFlag==6 or self.CFlag==7):
            self.JacoNorm()
        self.NonZeroJacoRowCol()
        self.NonZeroHessRowCol()
        self.nnzh=len(self.NonZeroHessRow)
        self.nnzj=len(self.NonZeroJacoRow)
        self.ConstraintBounds()
        self.nlp = pyipopt.create(self.Xlen, self.XLB, self.XUB, self.Glen, self.GLB, self.GUB, self.nnzj, self.nnzh, self.Objective, self.obj_grad, self.Constraints, self.ConstructJaco, self.Hessian)
        self.nlp.int_option('print_level',PrintOpt)
        self.nlp.int_option('max_iter',iter)
        self.nlp.num_option('tol',Xtol)
#         self.nlp.num_option('dual_inf_tol',500000)
#         self.nlp.str_option('accept_every_trial_step','yes')
#         '''==============Derivative Check============================'''
#         self.nlp.str_option('derivative_test','only-second-order')
#         self.nlp.num_option('derivative_test_perturbation',1e-6)
#         self.nlp.num_option('derivative_test_tol',1e-5)
#         '''================================================================='''
        #self.nlp.str_option('hessian_approximation','limited-memory')
        #self.nlp.str_option('nlp_scaling_method','none')
        #self.nlp.num_option('nlp_scaling_min_value',0.01)
        #self.nlp.str_option('alpha_for_y','full')
        #self.nlp.num_option('constr_viol_tol',1e-4)
        #nlp.str_option('expect_infeasible_problem','yes')
        #nlp.str_option('start_with_resto','yes')
        self.X0 = asarray(self.Xmeas,dtype=float_)
        self.Validation()
        self.ExitFlag={}
        self.Xopt, self.zl, self.zu, self.constraint_multipliers, self.obj, self.status = self.nlp.solve(self.X0)
        self.ExitFlag[-1]=self.status
        for i in range(0):
            if (self.status !=0):
                self.Xopt, self.zl, self.zu, self.constraint_multipliers, self.obj, self.status = self.nlp.solve(self.Xopt)
                self.ExitFlag[i]=self.status
                if (self.status==0):
                    self.OptimIndex=i
                    print 'sucess ',i
                    break      
        self.nlp.close()
#--------------------------Methods called once during initialisation of the object-------------    
    def ConstructXFlag(self):
        self.XFlag=[]
        self.FBFlag=[]
        if (self.CFlag in [1,2,5]):
            self.MakeTPconstant()
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2): # Flag==2 means constant
                    if (i.FTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    self.FBFlag.append(0)
                    i.FTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.FTag.Meas)
                    self.Sigma.append(i.FTag.Sigma)
                
                if (i.TTag.Flag !=2):    
                    if (i.TTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    self.FBFlag.append(0)
                    i.TTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.TTag.Meas)
                    self.Sigma.append(i.TTag.Sigma)
               
                if (i.PTag.Flag !=2):    
                    if (i.PTag.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    self.FBFlag.append(0)
                    i.PTag.Xindex=len(self.XFlag)-1
                    self.X.append(i.PTag.Meas)
                    self.Sigma.append(i.PTag.Sigma)
                
                for j,val in enumerate(i.CTag.keys()):
                    if (i.CTag[val].Flag!=2):
                        if (i.CTag[val].Flag!=0):
                            self.XFlag.append(1)
                            if (i.FreeBasis!=[]):
                                self.FBFlag.append(i.CTag[i.FreeBasis[0]])
                            else:
                                self.FBFlag.append(0)
                        else:
                            self.XFlag.append(0)
                            self.FBFlag.append(0)
                        i.CTag[val].Xindex=len(self.XFlag)-1
                        self.X.append(i.CTag[val].Meas)
                        if (i.CTag[val].Sigma==0.0):
                            print 'The Sigma value of the Tag ',val.Name, ' present in Stream ',i.Name, ' is zero'
                            exit()
                        self.Sigma.append(i.CTag[val].Sigma)                                
            elif (isinstance(i,Energy_Stream)):
                #self.XFlag.append(0)
                #i.Xindex=len(self.XFlag)-1
                if (i.Q.Flag !=2):    
                    if (i.Q.Flag!=0):
                        self.XFlag.append(1)
                    else:
                        self.XFlag.append(0)
                    FBFlag.append(0)
                    i.Q.Xindex=len(self.XFlag)-1
                    self.X.append(i.Q.Meas)
                    self.Sigma.append(i.Q.Sigma) # Q is always unmeasured and sigma doesnot affect the objective as flag is zero
            else:
                print "Stream in the list is not defined"
                quit()
    #-------------------------------------------------------------    
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
#                 self.XFlag.append(0)
#                 i.UXindex=len(self.XFlag)-1
#                 self.X.append(i.U)
#                 self.Sigma.append(1)
                s=0
            
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,EquilibriumReactor2)):
                for j in (i.RxnExt.keys()):
                    self.XFlag.append(0)
                    i.RxnExtXindex[j]=len(self.XFlag)-1
                    self.X.append(i.RxnExt[j])
                    self.Sigma.append(1)
                    self.FBFlag.append(0)
                s=0
                
            elif (isinstance(i,Reactor)     or isinstance(i,EquilibriumReactor)):
                  for j in (i.RxnExt.keys()):
                    self.XFlag.append(0)
                    i.RxnExtXindex[j]=len(self.XFlag)-1
                    self.X.append(i.RxnExt[j])
                    self.Sigma.append(1)
                    self.FBFlag.append(0)

            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater) or isinstance(i,Pump))):
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
                        self.XLB[i.CTag[val].Xindex]=1e-12
    #---------------------------------------------------------------------

    def JacobianSize(self):
        self.Glen=0
        self.Normlen=0
        for i in self.ListUints:
            if (self.CFlag==1): # Only Material balance
                self.Glen=self.Glen+i.LenMatRes#1
            elif (self.CFlag==2 or self.CFlag==5): # Material and Comp balance
                self.Glen=self.Glen + i.LenCompRes + i.LenMatRes #+ i.LenPreRes#1
            elif (self.CFlag==3 or self.CFlag==6): # Mat comp Eng bal
                self.Glen=self.Glen + i.LenCompRes + i.LenMatRes + i.LenEneRes
            elif (self.CFlag==4 or self.CFlag==7):
                self.Glen=self.Glen+i.LenCompRes + i.LenMatRes + i.LenEneRes + i.LenPreRes
        for i in self.ListStreams:
            if ((isinstance(i,Material_Stream)) and (self.CFlag==5 or self.CFlag==6 or self.CFlag==7)):
                self.Glen=self.Glen+1
                self.Normlen=self.Normlen+1

    def ConstraintBounds(self):
        Glen=0
        Normlen=0
        self.GLB=zeros((self.Glen))
        self.GUB=zeros((self.Glen))
        for i in self.ListStreams:
            if ((isinstance(i,Material_Stream)) and (self.CFlag==5 or self.CFlag==6 or self.CFlag==7)):
                Glen=Glen+1
                Normlen=Normlen+1
        for i in self.ListUints:
            if (self.CFlag==1): # Only Material balance
                LB,UB=i.MaterialBalBound()
                self.GLB[Glen:Glen+i.LenMatRes]=LB
                self.GUB[Glen:Glen+i.LenMatRes]=UB
                Glen=Glen+i.LenMatRes#1
            elif (self.CFlag==2 or self.CFlag==5): # Material and Comp balance
                LB,UB=i.MaterialBalBound()
                self.GLB[Glen:Glen+i.LenMatRes]=LB
                self.GUB[Glen:Glen+i.LenMatRes]=UB
                Glen=Glen + i.LenMatRes#1
                
                LB,UB=i.ComponentBalBound()
                self.GLB[Glen:Glen+i.LenCompRes]=LB
                self.GUB[Glen:Glen+i.LenCompRes]=UB
                Glen=Glen + i.LenCompRes
                
#                 LB,UB=i.PressureBalBound()
#                 self.GLB[Glen:Glen+i.LenPreRes]=LB
#                 self.GUB[Glen:Glen+i.LenPreRes]=UB
#                 Glen=Glen + i.LenPreRes
            elif (self.CFlag==3 or self.CFlag==6): # Mat comp Eng bal
                LB,UB=i.MaterialBalBound()
                self.GLB[Glen:Glen+i.LenMatRes]=LB
                self.GUB[Glen:Glen+i.LenMatRes]=UB
                Glen=Glen + i.LenMatRes#1
                
                LB,UB=i.ComponentBalBound()
                self.GLB[Glen:Glen+i.LenCompRes]=LB
                self.GUB[Glen:Glen+i.LenCompRes]=UB
                Glen=Glen + i.LenCompRes
                
                LB,UB=i.EnergyBalBound()
                self.GLB[Glen:Glen+i.LenEneRes]=LB
                self.GUB[Glen:Glen+i.LenEneRes]=UB
                Glen=Glen + i.LenEneRes
                
            elif (self.CFlag==4 or self.CFlag==7):
                LB,UB=i.MaterialBalBound()
                self.GLB[Glen:Glen+i.LenMatRes]=LB
                self.GUB[Glen:Glen+i.LenMatRes]=UB
                Glen=Glen + i.LenMatRes#1
                
                LB,UB=i.ComponentBalBound()
                self.GLB[Glen:Glen+i.LenCompRes]=LB
                self.GUB[Glen:Glen+i.LenCompRes]=UB
                Glen=Glen + i.LenCompRes
                
                LB,UB=i.EnergyBalBound()
                self.GLB[Glen:Glen+i.LenEneRes]=LB
                self.GUB[Glen:Glen+i.LenEneRes]=UB
                Glen=Glen + i.LenEneRes

                LB,UB=i.PressureBalBound()
                self.GLB[Glen:Glen+i.LenPreRes]=LB
                self.GUB[Glen:Glen+i.LenPreRes]=UB
                Glen=Glen + i.LenPreRes
    #------------------------------------------------------------------------
    def NonPosJacoNorm(self):
        row=[]
        col=[]
        Nrow=-1
        for ind,i in enumerate(self.ListStreams): 
            if (isinstance(i,Material_Stream)):
                Nrow=Nrow+1
                for ind in i.CTag.keys():
                    row.append(Nrow)
                    col.append(i.CTag[ind].Xindex)
        return row,col,Nrow+1
    
    def JacoNorm(self):
        self.JNorm=zeros((self.Normlen,self.Xlen))
        k=-1
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream)):
                k=k+1
                for ind in i.CTag.keys():
                    self.JNorm[k,i.CTag[ind].Xindex]=1
    def NonZeroJacoRowCol(self):
        row=[]
        col=[]
        StartRow=0
        if (self.CFlag==5 or self.CFlag==6 or self.CFlag==7):
            row1,col1,Nrow=self.NonPosJacoNorm()
            row.extend(row1)
            col.extend(col1)
            StartRow=Nrow
        for i in self.ListUints:
            if (self.CFlag==1):
                row1,col1=i.MaterialBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenMatRes#1
            elif (self.CFlag==2 or self.CFlag==5):
                row1,col1=i.MaterialBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenMatRes#1
                
                row1,col1=i.ComponentBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenCompRes
                
#                 row1,col1=i.PressureBalJacoNZP()
#                 row.extend(asarray(row1)+StartRow)
#                 col.extend(col1)
#                 StartRow=StartRow + i.LenPreRes
            
            elif (self.CFlag==3 or self.CFlag==6):
                row1,col1=i.MaterialBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenMatRes
                
                row1,col1=i.ComponentBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenCompRes
                
                row1,col1=i.EnergyBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenEneRes#1
            elif (self.CFlag==4 or self.CFlag==7):
                row1,col1=i.MaterialBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenMatRes#1
                
                row1,col1=i.ComponentBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenCompRes
                
                row1,col1=i.EnergyBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenEneRes#1
                
                row1,col1=i.PressureBalJacoNZP()
                row.extend(asarray(row1)+StartRow)
                col.extend(col1)
                StartRow=StartRow + i.LenPreRes
        
        self.NonZeroJacoRow=asarray(row)
        self.NonZeroJacoCol=asarray(col)

    def NonZeroHessObjRowCol(self):
#         NZP=[]
#         for i in range(self.Xlen):
#             NZP.append((i,i))
#         return NZP
        Dic=self.ObjHess()
        NZP=Dic.keys()
        return NZP
    
    def ObjHess(self):
#         Dic={}
#         for i in range(self.Xlen):
#             Dic[(i,i)]=2.0*self.XFlag[i]/self.Sigma[i]**2
        Dic={}
        for i in self.ListStreams:
            if (isinstance(i,FixedConcStream) or isinstance(i,Material_Stream)):
                if (i.FTag.Flag !=2):
                    Dic[(i.FTag.Xindex,i.FTag.Xindex)]=i.FTag.Flag*2.0/i.FTag.Sigma**2
                if (i.TTag.Flag !=2):
                    Dic[(i.TTag.Xindex,i.TTag.Xindex)]=i.TTag.Flag*2.0/i.TTag.Sigma**2
                if (i.PTag.Flag !=2):
                    Dic[(i.PTag.Xindex,i.PTag.Xindex)]=i.PTag.Flag*2.0/i.PTag.Sigma**2
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag !=2):
                        if (i.FreeBasis!=[]):
                            if (i.FreeBasis[0]!=j):
                                Dic[(i.CTag[j].Xindex,i.CTag[j].Xindex)]=i.CTag[j].Flag*2.0/((i.CTag[j].Sigma**2)*(1.0-i.CTag[i.FreeBasis[0]].Est)**2) 
                            else:
                                S=0.0
                                for k in i.CTag.keys():
                                    T1=(2.0*i.CTag[k].Flag*i.CTag[k].Est)/((i.CTag[k].Sigma**2)*(1.0-i.CTag[i.FreeBasis[0]].Est)**3)
                                    T2=(3.0*i.CTag[k].Est/(1.0-i.CTag[i.FreeBasis[0]].Est))-2.0*i.CTag[k].Meas
                                    S=S+T1*T2
                                Dic[(i.CTag[j].Xindex,i.CTag[j].Xindex)]=S
                            for k in i.CTag.keys():
                                if (k!=i.FreeBasis[0]):
                                    T1=(2.0*i.CTag[k].Flag)/((i.CTag[k].Sigma**2)*(1.0-i.CTag[i.FreeBasis[0]].Est)**2)
                                    T2=(2.0*i.CTag[k].Est/(1.0-i.CTag[i.FreeBasis[0]].Est))-i.CTag[k].Meas
                                    Dic[(i.CTag[k].Xindex,i.CTag[i.FreeBasis[0]].Xindex)]=T1*T2
                                    Dic[(i.CTag[i.FreeBasis[0]].Xindex,i.CTag[k].Xindex)]=T1*T2
                        else:
                            Dic[(i.CTag[j].Xindex,i.CTag[j].Xindex)]=i.CTag[j].Flag*2.0/i.CTag[j].Sigma**2
            elif (isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    Dic[(i.Q.Xindex,i.Q.Xindex)]=i.Q.Flag*2.0/i.Q.Sigma**2
        return Dic
        
    def NonZeroHessRowCol(self):
        NZP=[]
        '''Non zero entries of hessian of the objective function'''
        NZP.extend(self.NonZeroHessObjRowCol())
        '''Non zero entries of hessian of the Constraints'''
        for i in self.ListUints:
            if (self.CFlag==2 or self.CFlag==5):
                List1=i.ComponentBalHessNZP()
                for j in range(i.LenCompRes):
                    NZP.extend(List1[j])
            elif (self.CFlag==3 or self.CFlag==6 or self.CFlag==4 or self.CFlag==7):
                List1=i.ComponentBalHessNZP()
                diag=[]
                offdiag=[]
                for j in range(i.LenCompRes):
                    NZP.extend(List1[j])
                List1=i.EnergyBalHessNZP()
                for j in range(i.LenEneRes):
                    NZP.extend(List1[j])
        UniqueNZP=set(NZP)
        UniqueSymNZP=[]
        for i in UniqueNZP:
            if (i[0]>=i[1]):
                UniqueSymNZP.append(i)
        List=map(list,zip(* UniqueSymNZP))
        self.NonZeroHessRow=asarray(List[0])
        self.NonZeroHessCol=asarray(List[1])
        

    def Dic2Mat(self,Dic):
        Mat=zeros((self.Xlen,self.Xlen),dtype=float_)
        for i in Dic.keys():
            Mat[i[0],i[1]]=Dic[i]
        return Mat
    
    def Hessian(self,X, lamda, obj_factor, flag, user_data = None):
        if flag:
            return (array(self.NonZeroHessRow), array(self.NonZeroHessCol))
        else:
            self.DeconstructX(X)
            if (self.CFlag not in [1,2,5]):
                for i in self.ListStreams:
                    if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                        i.h=i.Therm.EnthalpyStream(i)
                        i.GradDic=i.EnthalpyGradient()
                        i.HessDic=i.EnthalpyHessian()
            Mat=self.Dic2Mat(self.ObjHess())*obj_factor
            He=[]
            Nlamda=self.Normlen
            for i in self.ListUints:
                if (self.CFlag==1):
                    Nlamda=Nlamda+i.LenMatRes
                elif (self.CFlag==2 or self.CFlag==5):
                    Nlamda=Nlamda+i.LenMatRes                    
                    List=i.ComponentBalHess()
                    for j in List:
                        Mat=Mat+self.Dic2Mat(j)*lamda[Nlamda]
                        Nlamda=Nlamda+1
                    #Nlamda=Nlamda+i.LenPreRes               
                elif (self.CFlag==3 or self.CFlag==6):
                    Nlamda=Nlamda+i.LenMatRes                    
                    List=i.ComponentBalHess()
                    for j in List:
                        Mat=Mat+self.Dic2Mat(j)*lamda[Nlamda]
                        Nlamda=Nlamda+1
                    List=i.EnergyBalHess()
                    for j in List:
                        Mat=Mat+self.Dic2Mat(j)*lamda[Nlamda]
                        Nlamda=Nlamda+1
                elif (self.CFlag==4 or self.CFlag==7):
                    Nlamda=Nlamda+i.LenMatRes                    
                    List=i.ComponentBalHess()
                    for ind,j in enumerate(List):
                        Mat=Mat+self.Dic2Mat(j)*lamda[Nlamda]#/i.CB_SF[ind]
                        Nlamda=Nlamda+1
                    List=i.EnergyBalHess()
                    for ind,j in enumerate(List):
                        Mat=Mat+self.Dic2Mat(j)*lamda[Nlamda]#/i.EB_SF[ind]
                        Nlamda=Nlamda+1
                    Nlamda=Nlamda+i.LenPreRes
            for i in range(len(self.NonZeroHessRow)):
                He.append(Mat[self.NonZeroHessRow[i]][self.NonZeroHessCol[i]])
            return asarray(He,dtype=float_)
        
    def Validation(self):
        print'-------------Printing the problem-----------------------------'
        print 'Length of X :',self.Xlen
        print 'Length of LB of X :', len(self.XLB)
        print 'Length of UB of X :', len(self.XUB)
        print 'No.Of Constraints :', len(self.Constraints(self.X0))
        print 'Length of LB on Constraints :',len(self.GLB)
        print 'Length of UB on Constraints :',len(self.GUB)
        print 'No. of Rows of Jacobian :', max(self.NonZeroJacoRow)+1
        print '---------------------------------------------------'
        if (len(self.X0)!=len(self.Xmeas)): 
            print 'Length of the initial guess and Measurement vector are not matching'
            print 'Length of X0 :',len(self.X0)
            print 'Length of Xmeas :',len(self.Xmeas)
            exit()
        if (len(self.X0)!=len(self.XLB)):
            print 'Length of the initial guess and lower bound on X are not matching'
            print 'Length of X0 :',len(self.X0)
            print 'Length of XLB :',len(self.XLB)
            exit()
        if (len(self.X0)!=len(self.XUB)):
            print 'Length of the initial guess and upper bound on X are not matching'
            print 'Length of X0 :',len(self.X0)
            print 'Length of XUB :',len(self.XUB)
            exit()
        if (self.Glen!=len(self.GLB)):
            print 'Length of the constraint residuals and lower bound on constraints are not matching'
            print 'Length of  constraints:',self.Glen
            print 'Length of GLB :',len(self.GLB)
            exit()
        if (self.Glen!=len(self.GUB)):
            print 'Length of the constraint residuals and upper bound on constraints are not matching'
            print 'Length of  constraints:',self.Glen
            print 'Length of GUB :',len(self.GUB)
            exit()
        if (len(self.obj_grad(self.X0))!=len(self.X0)):
            print 'Length of the initial guess and gradient of the objective function are not matching'
            print 'Length of  initial guess:',len(self.X0)
            print 'Length of Gradient :',len(self.obj_grad(self.X0))
            exit()
        
        Conlen=len(self.Constraints(self.X0))
        if (Conlen!=self.Glen):
            print 'No. of rows in Jacobian not equal to no of Constraints'
            exit()
        NJaco=self.Xlen*self.Glen
        if ((len(self.NonZeroJacoRow)>NJaco) or (len(self.NonZeroJacoCol)>NJaco)):
            print 'Incorrect Jacobian dimensions.'
            print 'Total no. of elements in Jacobian :', NJaco
            exit()
        elif (max(self.NonZeroJacoRow)!=(self.Glen-1)):
            print 'Some of the  of rows of Jacobian is fully zero'
            print 'No. of Constraints is :',self.Glen
            print 'Largest row number of the Jacobian having atleast one nonzero is :',max(self.NonZeroJacoRow)+1
            exit()
            
        elif (max(self.NonZeroJacoCol)>(self.Xlen-1)):
            print 'Incorrect No. of columns of Jacobian'
            print 'Max column no of the Jacobian in the vector', max(self.NonZeroJacoCol)
            exit()
        
        for i in range(Conlen):
            if (i not in self.NonZeroJacoRow):
                print 'Error : No non zero entries in ',i,'th', 'row of the Jacobian Matrix'
                exit()
                
        '''Check for the Uniqueness of Units'''
        if (len(self.ListUints)!=len(set(self.ListUints))):
            print ('Units are not unique or the same Units are being added multiple times to the Unit list. Printing Non Unique Units')
            Dic=Con.Counter(self.ListUints)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i.Name,'repeated', Dic[i], ' times'
            exit()
        
        '''Check for the Uniqueness of Streams'''
        if (len(self.ListStreams)!=len(set(self.ListStreams))):
            print ('Streams are not unique or the same stream being added multiple times. Printing Non Unique Streams')
            Dic=Con.Counter(self.ListStreams)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i.Name,'repeated', Dic[i], ' times'
            exit()
        
        ''' Check for Uniqueness of Sensors'''
        C=[]
        for i in self.ListStreams:
            if (not isinstance(i,Energy_Stream)):
                C.extend([i.FTag,i.TTag,i.PTag])
                C.extend(i.CTag.values())
        UniqueC=set(C)
        if (len(C)>len(UniqueC)):
            for i in UniqueC:
                Count=0.0
                for j in C:
                    if (i==j):
                        Count=Count+1
                if (Count>1):
                    print 'Error : Same Sensor being used in multiple streams'
                    print 'Check the Tag : ', i.Tag
                    exit()
                    
        '''Check the connectivity information'''
        InletStream=[]
        OutletStream=[]
        EnergyStream=[]
        EnergyFlag=[]
        ListStream1=[]
        for i in self.ListUints:
            if (isinstance(i,Reactor)):
                InletStream.append(i.Rstrm)
                OutletStream.append(i.Pstrm)
                for j in i.Qstrm:
                    EnergyStream.append(j)
                    EnergyFlag.append(i.EFlag)
            elif (isinstance(i,Mixer)):
                InletStream.extend(i.output)
                OutletStream.extend(i.input)
            elif (isinstance(i,Pump)):
                InletStream.append(i.Inlet)
                OutletStream.append(i.Outlet)
                EnergyStream.append(i.Qstrm)
            elif (isinstance(i,Seperator)):
                InletStream.extend(i.input)
                OutletStream.extend(i.output)
            elif (isinstance(i,Heater)):
                InletStream.append(i.input)
                OutletStream.append(i.output)
                EnergyStream.append(i.Qstrm)
                EnergyFlag.append(i.HCFlag)
            elif (isinstance(i,HeatExchanger)):
                InletStream.append(i.Shellin)
                InletStream.append(i.Tubein)
                OutletStream.append(i.Shellout)
                OutletStream.append(i.Tubeout)
            ListStream1.extend(InletStream)
            ListStream1.extend(OutletStream)
            ListStream1.extend(EnergyStream)
        if (len(set(self.ListStreams))!=len(set(ListStream1))):
            print 'The length of the List of streams given by the user not matching the list of streams generated from the list of units'
            print 'Length of the list of streams generated from the list of units is ',len(set(ListStream1))
            print 'Length of the list of streams given by the user is ',len(set(self.ListStreams))
            if (len(set(self.ListStreams))>len(set(ListStream1))):
                print 'The user defined list of streams is the super set'
                print 'Check the list of units prepared by the user. Some of the units may be missing in the list.'
                c= (set(self.ListStreams)-set(ListStream1))
            else:
                print 'List of streams obtained from the list of units is the super set'
                print 'Check the list of streams prepared by the user. Some of the streams may be missing in the list.'
                c= (set(ListStream1)-set(self.ListStreams))
            print 'The following streams are not present in both the list.'
            for i in c:
                print i.Name
            exit()
        
        '''Checking the Uniqueness of InletStreams '''
        if (len(InletStream)!=len(set(InletStream))):
            print ('The following Streams are input to more than one unit')
            Dic=Con.Counter(InletStream)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i.Name,' stream is input to ', Dic[i], ' units'
            exit()
            
        '''Checking the Uniqueness of OutletStreams '''
        if (len(OutletStream)!=len(set(OutletStream))):
            print ('The following Streams are output to more than one unit')
            Dic=Con.Counter(OutletStream)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i.Name,' stream is output to ', Dic[i], ' units'
            exit()
            
        ''' Checking the Energy Streams'''
#         Dic=Con.Counter(EnergyStream)
#  
#         for i in Dic.keys():
#             if (Dic[i]==1):
#                 if (i.Q.Flag!=2):
#                     print 'Either Source or Sink of the Energy Stream ',i.Name,' is not defined'
#                     print i.Q.Meas,i.Q.Flag
#                     exit()
#             elif (Dic[i]==2):
#                 EEFlag=[0]*2
#                 cont=0
#                 for ind,j in enumerate(EnergyStream):
#                     if (i==j):
#                         EEFlag[cont]=EnergyFlag[ind]
#                         cont=cont+1
#                 if (EEFlag[0]==1 and EEFlag[1]==1):
#                     print 'Energy Stream ', i.Name, ' is connecting to two sinks'
#                     exit()
#                 elif (EEFlag[0]==-1 and EEFlag[1]==-1):
#                     print 'Energy Stream ', i.Name, ' is connecting to two sources'
#                     exit()
#             else:
#                 print 'Energy Stream ',i.Name,' is associated with more than two units'
#                 exit()
#                 
# #-----------------------------Methods called several times by the optimiser-----------
    
    def Objective(self,X,user_data=None):
        assert len(X)==self.Xlen
#         Obj=0
#         for i in range(self.Xlen):
#             Obj=Obj+self.XFlag[i]*((X[i]-self.Xmeas[i])/self.Sigma[i])**2
        Obj=0.0
        self.DeconstructX(X)
        for i in self.ListStreams:
            if (isinstance(i,FixedConcStream) or isinstance(i,Material_Stream)):
                if (i.FTag.Flag !=2):
                    Obj=Obj+i.FTag.Flag*((i.FTag.Est-i.FTag.Meas)/i.FTag.Sigma)**2
                if (i.TTag.Flag !=2):
                    Obj=Obj+i.TTag.Flag*((i.TTag.Est-i.TTag.Meas)/i.TTag.Sigma)**2
                if (i.PTag.Flag !=2):
                    Obj=Obj+i.PTag.Flag*((i.PTag.Est-i.PTag.Meas)/i.PTag.Sigma)**2
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag !=2):
                        if (i.FreeBasis!=[]):
                            if (i.FreeBasis[0]!=i.CTag[j]):
                                Obj=Obj+i.CTag[j].Flag*((i.CTag[j].Est/(1.0-i.CTag[i.FreeBasis[0]].Est)-i.CTag[j].Meas)/i.CTag[j].Sigma)**2
                            else:
                                Obj=Obj+i.CTag[j].Flag*((i.CTag[j].Est-i.CTag[j].Meas)/i.CTag[j].Sigma)**2
                        else:
                            Obj=Obj+i.CTag[j].Flag*((i.CTag[j].Est-i.CTag[j].Meas)/i.CTag[j].Sigma)**2
            elif (isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    Obj=Obj+i.Q.Flag*((i.Q.Est-i.Q.Meas)/i.Q.Sigma)**2
        return Obj

    def obj_grad(self,X,user_data=None):
        assert len(X)==self.Xlen
#         SumG=zeros((self.Xlen),dtype=float_)
#         for i in range(self.Xlen):
#             SumG[i]=2*self.XFlag[i]*(X[i]-self.Xmeas[i])/self.Sigma[i]**2
        SumG=zeros((self.Xlen),dtype=float_)
        self.DeconstructX(X)
        for i in self.ListStreams:
            if (isinstance(i,FixedConcStream) or isinstance(i,Material_Stream)):
                if (i.FTag.Flag !=2):
                    SumG[i.FTag.Xindex]=2.0*i.FTag.Flag*(i.FTag.Est-i.FTag.Meas)/(i.FTag.Sigma**2)
                if (i.TTag.Flag !=2):
                    SumG[i.TTag.Xindex]=2.0*i.TTag.Flag*(i.TTag.Est-i.TTag.Meas)/(i.TTag.Sigma**2)
                if (i.PTag.Flag !=2):
                    SumG[i.PTag.Xindex]=2.0*i.PTag.Flag*(i.PTag.Est-i.PTag.Meas)/(i.PTag.Sigma**2)
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag !=2):
                        if (i.FreeBasis!=[]):
                            if (i.FreeBasis[0]!=j):
                                SumG[i.CTag[j].Xindex]=2.0*i.CTag[j].Flag*(i.CTag[j].Est/(1.0-i.CTag[i.FreeBasis[0]].Est)-i.CTag[j].Meas)/((i.CTag[j].Sigma**2)*(1.0-i.CTag[i.FreeBasis[0]].Est)) 
                            else:
                                S=0.0
                                for k in i.CTag.keys():
                                    T1=(2.0*i.CTag[k].Flag*i.CTag[k].Est)/((i.CTag[k].Sigma**2)*(1.0-i.CTag[i.FreeBasis[0]].Est)**2)
                                    T2=(i.CTag[k].Est/(1.0-i.CTag[i.FreeBasis[0]].Est))-i.CTag[k].Meas
                                    S=S+T1*T2
                                SumG[i.CTag[j].Xindex]=S+2.0*i.CTag[i.FreeBasis[0]].Flag*(i.CTag[i.FreeBasis[0]].Est-i.CTag[i.FreeBasis[0]].Meas)/(i.CTag[i.FreeBasis[0]].Sigma**2)
                        else:
                            SumG[i.CTag[j].Xindex]=2.0*i.CTag[j].Flag*(i.CTag[j].Est-i.CTag[j].Meas)/(i.CTag[j].Sigma**2)
            elif (isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    SumG[i.Q.Xindex]=2.0*i.Q.Flag*(i.Q.Est-i.Q.Meas)/(i.Q.Sigma**2)
        return asarray(SumG,dtype=float_)

    def Constraints(self,X,user_data=None):
        assert len(X)==self.Xlen
        Resid=[]
        self.DeconstructX(X)
        if (self.CFlag not in [1,2,5]):
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
                #Resid.extend(i.PressureBalRes())
            elif (self.CFlag==3 or self.CFlag==6):
                Resid.extend(i.MaterialBalRes())
                Resid.extend(i.ComponentBalRes())
                Resid.extend(i.EnergyBalRes())
            elif (self.CFlag==4 or self.CFlag==7):
                Resid.extend(i.MaterialBalRes())
                Resid.extend(i.ComponentBalRes())
                Resid.extend(i.EnergyBalRes())
                Resid.extend(i.PressureBalRes())
#                 Resid.extend(asarray(i.MaterialBalRes())/i.MB_SF)
#                 Resid.extend(asarray(i.ComponentBalRes())/i.CB_SF)
#                 Resid.extend(asarray(i.EnergyBalRes())/i.EB_SF)
#                 Resid.extend(asarray(i.PressureBalRes())/i.PB_SF) 
        return asarray(Resid,dtype=float_)
    
    def ConstructJaco(self,X,flag,user_data=None):
        if (flag):
            return (self.NonZeroJacoRow,self.NonZeroJacoCol)
        else:
            self.DeconstructX(X)
            if (self.CFlag not in [1,2,5]):
                for i in self.ListStreams:
                    if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                        i.h=i.Therm.EnthalpyStream(i)
                        i.GradDic=i.EnthalpyGradient()
            Ja=[]
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
#                     Jaco[start:start+i.LenPreRes][:]=i.PressureBalJaco(self.Xlen)
#                     start=start+i.LenPreRes
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
                    #print 'Jacobian length',i.LenCompRes
                    start=start+i.LenCompRes
                    Jaco[start:start+i.LenEneRes][:]=i.EnergyBalJaco(self.Xlen)
                    start=start+i.LenEneRes
                    Jaco[start:start+i.LenPreRes][:]=i.PressureBalJaco(self.Xlen)
                    start=start+i.LenPreRes
#                      a=i.MaterialBalJaco(self.Xlen)
#                      for m in range(i.LenMatRes):
#                          Jaco[start:start+1][:]=a[m,:]/i.MB_SF[m]
#                          start=start+1
#                      #start=start+i.LenMatRes#1
#                      a=i.ComponentBalJaco(self.Xlen)
#                      for m in range(i.LenCompRes):
#                          Jaco[start:start+1][:]=a[m,:]/i.CB_SF[m]
#                          start=start+1
#                      a=i.EnergyBalJaco(self.Xlen)
#                      for m in range(i.LenEneRes):
#                          Jaco[start:start+1][:]=a[m,:]/i.EB_SF[m]
#                          start=start+1
#                      #start=start+ i.LenEneRes
#                      a=i.PressureBalJaco(self.Xlen)
#                      for m in range(i.LenPreRes):
#                          Jaco[start:start+1][:]=a[m,:]/i.PB_SF[m]
#                          start=start+1
#                     #print i.PressureBalJaco(self.Xlen)
#                      start=start+ i.LenPreRes
            for i in range(len(self.NonZeroJacoRow)):
                Ja.append(Jaco[self.NonZeroJacoRow[i]][self.NonZeroJacoCol[i]])
            return asarray(Ja) 
    
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
                #i.Q.Est=X[i.Xindex]
                if (i.Q.Flag !=2):
                    i.Q.Est=X[i.Q.Xindex]
            
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
#                 i.U=X[i.UXindex]
                s=0
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,EquilibriumReactor2)):
                for k in i.RxnExt.keys():
                    i.RxnExt[k]=X[i.RxnExtXindex[k]]
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                for k in i.RxnExt.keys():
                    i.RxnExt[k]=X[i.RxnExtXindex[k]]
            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater) or isinstance(i,Pump))):
                print 'here'
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
    
    def CopyEst2Meas(self):
        X=self.Xopt
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2):
                    i.FTag.Meas=X[i.FTag.Xindex]
                if (i.TTag.Flag!=2):
                    i.TTag.Meas=X[i.TTag.Xindex]
                if (i.PTag.Flag!=2):
                    i.PTag.Meas=X[i.PTag.Xindex]
                for k in i.CTag.keys():
                    if (i.CTag[k].Flag!=2):
                        i.CTag[k].Meas=X[i.CTag[k].Xindex]
            elif(isinstance(i,Energy_Stream)):
                #i.Q.Est=X[i.Xindex]
                if (i.Q.Flag !=2):
                    i.Q.Meas=X[i.Q.Xindex]
            
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
#                 i.U=X[i.UXindex]
                s=0
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                for k in i.RxnExt.keys():
                    i.RxnExt[k]=X[i.RxnExtXindex[k]]
            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater) or isinstance(i,Pump))):
                print "Object in the list is not defined"
                quit()   
    
    def CompareEstSol(self,Ctol):
        X=self.Xopt
        BList=[]
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2):
                    BList.append(abs(i.FTag.Est-i.FTag.Sol)<Ctol)
                if (i.TTag.Flag!=2):
                    BList.append(abs(i.TTag.Est-i.TTag.Sol)<Ctol)
                if (i.PTag.Flag!=2):
                    BList.append(abs(i.PTag.Est-i.PTag.Sol)<Ctol)
                    
                for k in i.CTag.keys():
                    if (i.CTag[k].Flag!=2):
                        BList.append(abs(i.CTag[k].Est-i.CTag[k].Sol)<Ctol)
                        
            elif(isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    BList.append(abs(i.Q.Est-i.Q.Sol)<Ctol)
            
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
#                 i.U=X[i.UXindex]
                s=0
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                s=0
                for k in i.RxnExt.keys():
                    BList.append(abs(i.RxnExt[k]-i.RxnExtSol[k]))
            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater) or isinstance(i,Pump))):
                print "Object in the list is not defined"
                quit()   
        self.Pass=all(BList)
        return self.Pass
        
    def CompareEstSolPercent(self,Ctol):
        X=self.Xopt
        BList=[]
        for i in self.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag!=2):
                    BList.append(abs((i.FTag.Est-i.FTag.Sol)*100.0/i.FTag.Sol)<Ctol)
                if (i.TTag.Flag!=2):
                    BList.append(abs((i.TTag.Est-i.TTag.Sol)*100.0/i.TTag.Est)<Ctol)
                if (i.PTag.Flag!=2):
                    BList.append(abs((i.PTag.Est-i.PTag.Sol)*100.0/i.PTag.Est)<Ctol)
                    
                for k in i.CTag.keys():
                    if (i.CTag[k].Flag!=2):
                        BList.append(abs((i.CTag[k].Est-i.CTag[k].Sol)*100.0/i.CTag[k].Sol)<Ctol)
                        
            elif(isinstance(i,Energy_Stream)):
                if (i.Q.Flag !=2):
                    BList.append(abs((i.Q.Est-i.Q.Sol)*100.0/i.Q.Sol)<Ctol)
            
        for i in self.ListUints:
            if (isinstance(i,HeatExchanger)):
#                 i.U=X[i.UXindex]
                s=0
            elif (isinstance(i,ElementBalanceReactor)):
                s=0
            elif (isinstance(i,AdiabaticElementBalanceReactor)):
                s=0
            elif (isinstance(i,Reactor) or isinstance(i,EquilibriumReactor)):
                s=0
                for k in i.RxnExt.keys():
                    BList.append(abs((i.RxnExt[k]-i.RxnExtSol[k])*100.0/i.RxnExtSol[k])<Ctol)
            elif(not (isinstance(i,Mixer) or isinstance(i,Seperator) or isinstance(i,Heater) or isinstance(i,Pump))):
                print "Object in the list is not defined"
                quit()   
        self.Pass=all(BList)
        return self.Pass

    
    def MakeTPconstant(self):
        for i in self.ListStreams:
            if (not isinstance(i,Energy_Stream)):
                i.TTag.Flag=2
                i.PTag.Flag=2
            else:
                i.Q.Flag=2
                
    def NumGrad(self,X):
        SumG=zeros((self.Xlen),dtype=float_)
        self.DeconstructX(X)
        for i in range(len(X)):
            dx=X[i]*0.01
            f1=self.Objective(X)
            Temp=X[i]
            X[i]=X[i]+dx
            self.DeconstructX(X)
            f2=self.Objective(X)
            SumG[i]=(f2-f1)/dx
            X[i]=Temp
            self.DeconstructX(X)
        return SumG
