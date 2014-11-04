from numpy import zeros
from numpy import asarray
from math import log
from Units.Reactor import Reactor
class EquilibriumReactor(Reactor):
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
        self.LenCompRes=len(self.ListComp) + len(self.RxnExt.keys())
        #self.LenCompRes= len(self.RxnExt.keys())
        self.LenEneRes=1
        self.LenPreRes=1
        self.InitialExt=self.InitialGuessRxnExt()
#         self.MB_SF=abs(asarray(self.MaterialBalRes()))
#         self.CB_SF=abs(asarray(self.ComponentBalRes()))
#         self.EB_SF=abs(asarray(self.EnergyBalRes()))
#         self.PB_SF=abs(asarray(self.PressureBalRes()))
#         self.CheckForZero()
#     
#     def CheckForZero(self):
#         Min_SF=1.0
#         for ind,i in enumerate(self.MB_SF):
#             if (i<Min_SF):
#                 self.MB_SF[ind]=Min_SF
#         for ind,i in enumerate(self.CB_SF):
#             if (i<Min_SF):
#                 self.CB_SF[ind]=Min_SF
#         for ind,i in enumerate(self.EB_SF):
#             if (i<Min_SF):
#                 self.EB_SF[ind]=Min_SF
#         for ind,i in enumerate(self.PB_SF):
#             if (i<Min_SF):
#                 self.PB_SF[ind]=Min_SF

    
    def ComponentBalRes(self):
        Resid=[]
        for i in self.ListComp:
            sumC=0.0
            for j in self.RxnExt.keys():
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
        #Rxn=self.RxnExt.keys()
        for i in self.Rxn:
            Resid.append(self.EquilibriumConstraint(i))      
        return Resid
    
#     def EquilibriumConstraint(self,Rxn):
#         Prod=1.0
#         R=8.314
#         fu=self.Pstrm.Therm.Fugacity(self.Pstrm)           
#         for j in Rxn.Coef.keys():
#             if (fu[j]>1e-6):
#                 Prod = Prod * (fu[j]/100.00)**(Rxn.Coef[j])
#             else:
#                 Prod=0
#                 break
#         K=(self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)) # log is removed
#         Resid=(K - Prod)
#         #DG=self.Pstrm.Therm.DGRxn(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)
#         #Resid=(DG+R*self.Pstrm.TTag.Est*Prod)
#         return Resid

    def EquilibriumConstraint(self,Rxn):
        Prod=1.0
        fu=self.Pstrm.Therm.Fugacity(self.Pstrm)           
        for j in Rxn.Coef.keys():
            if (fu[j]!=0.0):
                Prod = Prod * (fu[j]/100.00)**(Rxn.Coef[j])
        #K=self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.PTag.Est,self.Pstrm.State)
        K=self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)
        #Resid=(K - Prod)
        Resid=(1 - Prod/K)
        return Resid
    
#     def EquilibriumConstraint1(self,Rxn):
#         Prod=1.0
#         mu=sum(Rxn.Coef.values())
#         for i in Rxn.Coef.keys():
#             Prod=Prod*(self.Pstrm.CTag[i].Est)**(Rxn.Coef[i])
#         K=self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)*(self.Pstrm.PTag.Est/100.0)**(-mu)
#         Resid=(1 - Prod/K)
#         return Resid
    
    def EquilibriumGradient(self):
        XID=[self.Pstrm.TTag,self.Pstrm.PTag]
        for i in self.ListComp:
            XID.append(self.Pstrm.CTag[i])
        ECGradDic={}
        for j in self.Rxn:
            GDic={}
            for i in XID:
                x=i.Est
                dx=i.Est*self.perturb
                i.Est=x+dx
                f1=self.EquilibriumConstraint(j)
                i.Est=x-dx
                f_1=self.EquilibriumConstraint(j)
                i.Est=x
                dhdt=(f1-f_1)/(2*dx)
                GDic[i]=dhdt
            ECGradDic[j]=GDic
        return ECGradDic
    
    def EquilibriumHessian(self):
        XID=[self.Pstrm.TTag,self.Pstrm.PTag]
        for i in self.ListComp:
            XID.append(self.Pstrm.CTag[i])
        ECHessDic={}
        for k in self.Rxn:
            HDic={}
            for ind1,i in enumerate(XID):
                for ind2,j in enumerate(XID):
                    if (ind1>ind2):
                        x=i.Est
                        y=j.Est
                        dx=i.Est*self.perturb
                        dy=i.Est*self.perturb
                        i.Est=x+dx
                        j.Est=y+dy
                        f11=self.EquilibriumConstraint(k)
                        j.Est=y-dy
                        f1_1=self.EquilibriumConstraint(k)
                        i.Est=x-dx
                        f_1_1=self.EquilibriumConstraint(k)
                        j.Est=y+dy
                        f_11=self.EquilibriumConstraint(k)
                        i.Est=x
                        j.Est=y
                        dhdt=(f11-f1_1-f_11+f_1_1)/(4*dx*dy)
                        HDic[(i,j)]=dhdt
                        HDic[(j,i)]=dhdt
                    elif (ind1==ind1):
                        x=i.Est
                        f0=self.EquilibriumConstraint(k)
                        dx=i.Est*self.perturb
                        i.Est=x+dx
                        f1=self.EquilibriumConstraint(k)
                        i.Est=x-dx
                        f_1=self.EquilibriumConstraint(k)
                        i.Est=x
                        dhdt=(f1-2*f0+f_1)/(dx**2)
                        HDic[(i,i)]=dhdt
            ECHessDic[k]=HDic
        return ECHessDic
    
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
                
        # Equilibrium Constraints now being added        
        ind=len(self.ListComp)
        ECGradDic=self.EquilibriumGradient()
        for indRxn,i in enumerate(self.Rxn):
            j=self.Pstrm
            if (j.TTag.Flag!=2):
                J[ind+indRxn,j.TTag.Xindex]=ECGradDic[i][j.TTag]
            if (j.PTag.Flag!=2):
                J[ind+indRxn,j.PTag.Xindex]=ECGradDic[i][j.PTag]
            for k in j.CTag.keys():
                if (j.CTag[k].Flag!=2):
                    J[ind+indRxn,j.CTag[k].Xindex]=ECGradDic[i][j.CTag[k]]
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
        for indRxn,i in enumerate(self.Rxn):
            j=self.Pstrm
            if (j.TTag.Flag!=2):
                row.append(ind+indRxn)
                col.append(j.TTag.Xindex)
            if (j.PTag.Flag!=2):
                row.append(ind+indRxn)
                col.append(j.PTag.Xindex)
            for k in j.CTag.keys():
                if (j.CTag[k].Flag!=2):
                    row.append(ind+indRxn)
                    col.append(j.CTag[k].Xindex)
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
        
        ind1=len(self.ListComp)
        i=self.Pstrm
        for ind2,m in enumerate(self.Rxn):
            if (i.TTag.Flag !=2):
                List[ind1+ind2].append((i.TTag.Xindex,i.TTag.Xindex))
            if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
                List[ind1+ind2].append((i.TTag.Xindex,i.PTag.Xindex))
                List[ind1+ind2].append((i.PTag.Xindex,i.TTag.Xindex))
            for j in i.CTag.keys():
                if (i.TTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[ind1+ind2].append((i.TTag.Xindex,i.CTag[j].Xindex))
                    List[ind1+ind2].append((i.CTag[j].Xindex,i.TTag.Xindex))
                 
            if (i.PTag.Flag !=2):
                List[ind1+ind2].append((i.PTag.Xindex,i.PTag.Xindex))
            for j in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[ind1+ind2].append((i.PTag.Xindex,i.CTag[j].Xindex))
                    List[ind1+ind2].append((i.CTag[j].Xindex,i.PTag.Xindex))
                 
            for i1,k in enumerate(i.CTag.keys()):
                for i2,j in enumerate(i.CTag.keys()):
                    if (i2>=i1):
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            List[ind1+ind2].append((i.CTag[k].Xindex,i.CTag[j].Xindex))
                            if (i1!=i2):
                                List[ind1+ind2].append((i.CTag[j].Xindex,i.CTag[k].Xindex))
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
        
        ind1=len(self.ListComp)
        ECHessDic=self.EquilibriumHessian()
        i=self.Pstrm
        for ind2,j in enumerate(self.Rxn):
            Dic={}
            if (i.TTag.Flag !=2):
                Dic[(i.TTag.Xindex, i.TTag.Xindex)]=ECHessDic[j][(i.TTag,i.TTag)]
            if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
                Dic[(i.TTag.Xindex,i.PTag.Xindex)]=ECHessDic[j][(i.TTag,i.PTag)]
                Dic[(i.PTag.Xindex,i.TTag.Xindex)]=ECHessDic[j][(i.TTag,i.PTag)]
            for k in i.CTag.keys():
                if (i.TTag.Flag !=2 and i.CTag[k].Flag !=2):
                    Dic[(i.TTag.Xindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.TTag,i.CTag[k])]
                    Dic[(i.CTag[k].Xindex,i.TTag.Xindex)]=ECHessDic[j][(i.TTag,i.CTag[k])]
                 
            if (i.PTag.Flag !=2):
                Dic[(i.PTag.Xindex,i.PTag.Xindex)]=ECHessDic[j][(i.PTag,i.PTag)]
            for k in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[k].Flag !=2):
                    Dic[(i.PTag.Xindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.PTag,i.CTag[k])]
                    Dic[(i.CTag[k].Xindex,i.PTag.Xindex)]=ECHessDic[j][(i.PTag,i.CTag[k])]
                 
            for ind1,k in enumerate(i.CTag.keys()):
                for ind2,m in enumerate(i.CTag.keys()):
                    if (ind2>=ind1):
                        if (i.CTag[k].Flag !=2 and i.CTag[m].Flag !=2):
                            Dic[(i.CTag[k].Xindex,i.CTag[m].Xindex)]=ECHessDic[j][(i.CTag[k],i.CTag[m])]
                            if (ind1!=ind2):
                                Dic[(i.CTag[m].Xindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.CTag[k],i.CTag[m])]
            List.append(Dic)
        return List