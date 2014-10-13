from numpy import zeros
from numpy import inf
from numpy import asarray
from numpy.linalg import pinv
from scipy.optimize import fsolve
from numpy import dot
from math import log
from Units.Reactor import Reactor
class EquilibriumReactor2(Reactor):
    def __init__(self,Name,Rstrm,Pstrm,Qstrm,Rxn,ExoEndoFlag=1,dp=0):
#===================Validation Starts======================================
        self.Name=Name        
        if ((ExoEndoFlag != -1) and (ExoEndoFlag != 1)):
            print 'Error: ExoEndoFlag of a Reactor is not valid option. The valid option is 1 for Endo and -1 for Exo thermic reactions'
            exit()
        if (Rstrm==Pstrm):
            print 'Reactant and Product streams are the same. They have to be different'
            exit()
#         elif (len(Rstrm)>1):
#             print 'More than one reactant stream is defined. But only one reactant stream is allowed'
#             exit()
#         elif (len(Pstrm)>1):
#             print 'More than one product stream is defined. But only one product stream is allowed'
#             exit()
        # Check the uniqueness of Qstrm
        C=[]
        for i in Qstrm:
            if (i not in C):
                C.append(i)
        if (len(C)!=len(Qstrm)):
            print 'Heat strams are not unique'
            exit()
        # Checking for uniqueness of Rxn
        C=[]
        for i in Rxn:
            if (i not in C):
                C.append(i)
        if (len(C)!=len(Rxn)):
            print 'Reactions of a reactor are not uniques'
            exit()
        R=[]
        P=[]    
        for i in Rxn:
            for j in i.Coef.keys():
                if ((i.Coef[j]>0) and (j not in P)):
                    P.append(j)
                elif ((i.Coef[j]<0) and (j not in C)):
                    R.append(j)
        for i in R:
            if (i not in Rstrm.CTag.keys()):
                print 'One of the reactants of a reaction is not present in the reactant stream of a reactor'
                exit()
        
        for i in P:
            if (i not in Pstrm.CTag.keys()):
                print 'One of the products of a reaction is not present in the product stream of a reactor'
                exit()
#====================================Validation ends=================================        
        self.Rstrm=Rstrm
        self.Pstrm=Pstrm
        self.Qstrm=Qstrm
        self.Dp=dp
        self.perturb=1e-2
        self.EFlag=ExoEndoFlag
        self.Rxn=Rxn
        self.RxnExt={}
        self.RxnExtXindex={}
        for i in Rxn:
            self.RxnExt[i]=0
            self.RxnExtXindex[i]=0
            
        self.ListComp=[]
        for i in self.Pstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        for i in self.Rstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        self.SMat=self.StoichioMatrix()
        self.LenMatRes=0
        self.LenCompRes=len(self.ListComp)+len(self.Rxn)
        self.LenEneRes=1
        self.LenPreRes=1
        self.RxnExt=self.InitialGuessRxnExt()
#         self.MB_SF=abs(asarray(self.MaterialBalRes()))
#         self.CB_SF=abs(asarray(self.ComponentBalRes()))
#         self.EB_SF=abs(asarray(self.EnergyBalRes()))
#         self.PB_SF=abs(asarray(self.PressureBalRes()))
#         self.CheckForZero()
    
    def CheckForZero(self):
        Min_SF=1.0
        for ind,i in enumerate(self.MB_SF):
            if (i<Min_SF):
                self.MB_SF[ind]=Min_SF
        for ind,i in enumerate(self.CB_SF):
            if (i<Min_SF):
                self.CB_SF[ind]=Min_SF
        for ind,i in enumerate(self.EB_SF):
            if (i<Min_SF):
                self.EB_SF[ind]=Min_SF
        for ind,i in enumerate(self.PB_SF):
            if (i<Min_SF):
                self.PB_SF[ind]=Min_SF

    
    def ComponentBalRes(self):
        Resid=[]
#         Ext=[]
#         for i in self.Rxn:
#             Ext.append(self.RxnExt[i])
#         EquilibriumRxnExt=fsolve(self.SolveForReactionExtent,Ext)
#         print 'EquilibriumRxnExt ',EquilibriumRxnExt
#         for ind,i in enumerate(self.Rxn):
#             self.RxnExt[i]=EquilibriumRxnExt[ind]
        for i in self.ListComp:
            sumC=0.0
            for j in self.Rxn:
                if (i in j.Coef.keys()):
                    sumC=sumC+j.Coef[i]*self.RxnExt[j]
            if (i in self.Rstrm.CTag.keys()):
                inletcomp=self.Rstrm.FTag.Est*self.Rstrm.CTag[i].Est
            else:
                inletcomp=0.0
            if (i in self.Pstrm.CTag.keys()):
                outletcomp=self.Pstrm.FTag.Est*self.Pstrm.CTag[i].Est
            else:
                outletcomp=0.0
            Resid.append(inletcomp-outletcomp+sumC)
        
#         '''Constraint to make RxnExt = Equilibrium RxnExt'''
#         Ext=[]
#         for i in self.Rxn:
#             Ext.append(self.RxnExt[i])
#         self.EquilibriumRxnExt=fsolve(self.SolveForReactionExtent,Ext)
        for ind,i in enumerate(self.Rxn):
            Resid.append(self.RxnExt[i]-self.EquilibriumRxnExt[ind])
        return Resid
    
    def ComponentBalJaco(self,len1):
        J = zeros((self.LenCompRes,len1))
        for ind,i in enumerate(self.ListComp):
            for j in self.RxnExt.keys():
                if (i in j.Coef.keys()):
                    J[ind,self.RxnExtXindex[j]] = j.Coef[i]            
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.CTag[i].Flag != 2):
                    J[ind,self.Rstrm.CTag[i].Xindex] = self.Rstrm.FTag.Est
                if (self.Rstrm.FTag.Flag !=2):
                    J[ind,self.Rstrm.FTag.Xindex] = self.Rstrm.CTag[i].Est
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.CTag[i].Flag !=2):
                    J[ind,self.Pstrm.CTag[i].Xindex] = -self.Pstrm.FTag.Est
                if (self.Pstrm.FTag.Flag != 2):
                    J[ind,self.Pstrm.FTag.Xindex] = -self.Pstrm.CTag[i].Est
        ind=len(self.ListComp)
        for ind1,i in enumerate(self.Rxn):
            J[ind+ind1,self.RxnExtXindex[i]]=1
        return J
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        for ind,i in enumerate(self.ListComp):
            for j in self.RxnExt.keys():
                if (i in j.Coef.keys()):
                    row.append(ind)
                    col.append(self.RxnExtXindex[j])           
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.CTag[i].Flag != 2):
                    row.append(ind)
                    col.append(self.Rstrm.CTag[i].Xindex)
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.CTag[i].Flag !=2):
                    row.append(ind)
                    col.append(self.Pstrm.CTag[i].Xindex)                    
            if (self.Rstrm.FTag.Flag !=2):
                row.append(ind)
                col.append(self.Rstrm.FTag.Xindex)            
            if (self.Pstrm.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Pstrm.FTag.Xindex)
        ind=len(self.ListComp)
        for ind1,i in enumerate(self.Rxn):
            row.append(ind+ind1)
            col.append(self.RxnExtXindex[i])
        return row,col
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        for ind1,i in enumerate(self.ListComp):
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[i].Flag !=2):
                    List[ind1].append((self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex))
                    List[ind1].append((self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex))
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[i].Flag !=2):
                    List[ind1].append((self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex))
                    List[ind1].append((self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex))
        return List
     
    def ComponentBalHess(self):
        List=[]
        for ind1,i in enumerate(self.ListComp):
            Dic={}
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[i].Flag !=2):
                    Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex)]=1.0
                    Dic[(self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex)]=1.0
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[i].Flag !=2):
                    Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex)]=-1.0
                    Dic[(self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex)]=-1.0
            List.append(Dic)
        for i in enumerate(self.Rxn):
            List.append({})
        return List
    
    def SolveForReactionExtent(self,X):
        yi=[0]*len(self.ListComp)
        f=[0]*len(self.Rxn)
        for ind1,i in enumerate(self.ListComp):
            SumN=0.0
            SumD=0.0
            for ind2,j in enumerate(self.Rxn):
                SumD=SumD+sum(j.Coef.values())*X[ind2]
                if (i in j.Coef.keys()):
                    SumN=SumN+j.Coef[i]*X[ind2]
            n0=self.Rstrm.FTag.Est
            if (i in self.Rstrm.CTag.keys()):
                ni=self.Rstrm.FTag.Est*self.Rstrm.CTag[i].Est
            else:
                ni=0.0
            yi[ind1]=(ni+SumN)/(n0+SumD)
        
        Composition={}
        for ind,i in enumerate(self.ListComp):
            Composition[i]=yi[ind]
            
        FugCof=self.Pstrm.Therm.FugacityCoefficient(self.Pstrm.TTag.Est,self.Pstrm.PTag.Est,self.Pstrm.State,Composition)     
        for ind2,j in enumerate(self.Rxn):
            K=self.Pstrm.Therm.EquilibriumConstant(j,self.Pstrm.TTag.Est,self.Pstrm.State)
            Prod=1.0
            for ind1,i in enumerate(self.ListComp):
                if (i in j.Coef.keys()):
                    Prod=Prod*(yi[ind1]*FugCof[i])**j.Coef[i]
            #f[ind2]=log(Prod/K)+log(self.Pstrm.PTag.Est/100.0)*(sum(j.Coef.values()))
            #f[ind2]=log(Prod*(self.Pstrm.PTag.Est/100.0)**sum(j.Coef.values()))
            #f[ind2]=Prod*(self.Pstrm.PTag.Est/100.0)**(sum(j.Coef.values()))-K
            f[ind2]=Prod-(self.Pstrm.PTag.Est/100.0)**(-sum(j.Coef.values()))*K
        return f
    
    def StoichioMatrix(self):
        NRxn=len(self.Rxn)
        NComp=len(self.ListComp)
        SMat=zeros((NComp,NRxn))
        for ind1,i in enumerate(self.ListComp):
            for ind2,j in enumerate(self.Rxn):
                if (i in j.Coef.keys()):
                    SMat[ind1,ind2]=j.Coef[i]
        return SMat
    
    def Const(self):
        NComp=len(self.ListComp)
        b=zeros((NComp,1))
        for ind,i in enumerate(self.ListComp):
            if (i in self.Pstrm.CTag.keys()):
                Temp1=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas
            else:
                Temp1=0
            if (i in self.Rstrm.CTag.keys()):
                Temp2=self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas
            else:
                Temp2=0
            #b[ind,0]=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas - self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas
            b[ind,0]=Temp1-Temp2
        return b
    
    def InitialGuessRxnExt(self):
        A=self.StoichioMatrix()
        RxnExt={}
        b=self.Const()
        B=pinv(dot(A.T,A))
        C=dot(B,A.T)
        Ext=dot(C,b)
        for ind,i in enumerate(self.Rxn):
            RxnExt[i]=Ext[ind,0]
        self.EquilibriumRxnExt=fsolve(self.SolveForReactionExtent,Ext)
        return RxnExt
    
    def EquRxnExtDer(self,Tag):
        GDic={}
        Ext=[]
        x=Tag.Est
        dx=Tag.Est*0.1#self.perturb
        if (dx==0.0):
            dx=0.01
        Tag.Est=x+dx
        for i in self.Rxn:
            Ext.append(self.RxnExt[i])
        f1=fsolve(self.SolveForReactionExtent,Ext)
        Tag.Est=x-dx
        f_1=fsolve(self.SolveForReactionExtent,Ext)
        Tag.Est=x
        dfdt=(f1-f_1)/(2*dx)
        return dfdt
    
    def ComponentBalBound(self):
        LB=zeros((self.LenCompRes))
        UB=zeros((self.LenCompRes))
        for i in range(len(self.ListComp),self.LenCompRes,1):
            LB[i]=-inf
        return LB,UB
