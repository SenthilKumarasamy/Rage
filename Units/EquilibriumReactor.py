from numpy import zeros
from numpy import asarray
from math import log
from Units.Reactor import Reactor
class EquilibriumReactor(Reactor):
    def __init__(self,Name,Rstrm,Pstrm,Qstrm,Rxn,ExoEndoFlag=1,dp=0):#EquEff=[],
#===================Validation Starts======================================
        self.Name=Name        
        if ((ExoEndoFlag != -1) and (ExoEndoFlag != 1)):
            print 'Error: ExoEndoFlag of a Reactor is not valid option. The valid option is 1 for Endo and -1 for Exo thermic reactions'
            exit()
        if (Rstrm==Pstrm):
            print 'Reactant and Product streams are the same. They have to be different'
            exit()

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
        self.perturb=1e-6
        self.EFlag=ExoEndoFlag
        self.Rxn=Rxn
            
        self.ListComp=[]
        for i in self.Pstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        for i in self.Rstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        self.SMat=self.StoichioMatrix()
        self.LenMatRes=0
        self.LenCompRes=len(self.ListComp) + len(self.Rxn) #modified
        #self.LenCompRes= len(self.RxnExt.keys())
        self.LenEneRes=1
        self.LenPreRes=1
        self.InitialGuessRxnExt() #modified
    
    def ComponentBalRes(self):
        Resid=[]
        for i in self.ListComp:
            sumC=0.0
            for j in self.Rxn: #modified
                if (i in j.Coef.keys()):
                    sumC=sumC+j.Coef[i]*j.RxnExt # modified
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
    

    def EquilibriumConstraint(self,Rxn):
        Prod=1.0
        fu=self.Pstrm.Therm.Fugacity(self.Pstrm)           
        for j in Rxn.Coef.keys():
            if (fu[j]!=0.0):
                Prod = Prod * (fu[j]/100.00)**(Rxn.Coef[j])
        K=self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State,Rxn.EquTempApp)
        #K=self.EquEff[Rxn]*self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)
        #Resid=(K - Prod)
        Resid=(1 - Prod/K)
        return Resid
    
    
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
            
            x=j.EquTempApp
            dx=self.perturb if (x==0) else x*self.perturb
            j.EquTempApp=x+dx
            f1=self.EquilibriumConstraint(j)
            j.EquTempApp=x-dx
            f_1=self.EquilibriumConstraint(j)
            j.EquTempApp=x
            dhdt=(f1-f_1)/(2*dx)
            GDic[j]=dhdt
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
                    elif (ind1==ind2):
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
                x=i.Est
                y=k.EquTempApp
                dx=i.Est*self.perturb
                dy=self.perturb if (y==0) else k.EquTempApp*self.perturb
                i.Est=x+dx
                k.EquTempApp=y+dy
                f11=self.EquilibriumConstraint(k)
                k.EquTempApp=y-dy
                f1_1=self.EquilibriumConstraint(k)
                i.Est=x-dx
                f_1_1=self.EquilibriumConstraint(k)
                k.EquTempApp=y+dy
                f_11=self.EquilibriumConstraint(k)
                i.Est=x
                k.EquTempApp=y
                dhdt=(f11-f1_1-f_11+f_1_1)/(4*dx*dy)
                HDic[(i,k)]=dhdt
                HDic[(k,i)]=dhdt
                
            y=k.EquTempApp
            f0=self.EquilibriumConstraint(k)
            dy=self.perturb if (y==0)else k.EquTempApp*self.perturb
            k.EquTempApp=y+dy
            f1=self.EquilibriumConstraint(k)
            k.EquTempApp=y-dy
            f_1=self.EquilibriumConstraint(k)
            k.EquTempApp=y
            dhdt=(f1-2*f0+f_1)/(dx**2)
            HDic[(k,k)]=dhdt
            
            ECHessDic[k]=HDic
        return ECHessDic
    
    def ComponentBalJaco(self,len1):
        J = zeros((self.LenCompRes,len1))
        for ind,i in enumerate(self.ListComp):
            for j in self.Rxn: #modified
                if (i in j.Coef.keys()):
                    J[ind,j.RxnExtXindex] = j.Coef[i]  #modified          
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
            if (i.EquTempAppFlag !=2):
                J[ind+indRxn,i.EquTempAppXindex]=ECGradDic[i][i]
        return J
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        for ind,i in enumerate(self.ListComp):
            for j in self.Rxn: #modified
                if (i in j.Coef.keys()):
                    row.append(ind)
                    col.append(j.RxnExtXindex) #modified           
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
            if (i.EquTempAppFlag != 2):
                row.append(ind+indRxn)
                col.append(i.EquTempAppXindex)
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
            if (i.TTag.Flag != 2 and m.EquTempAppFlag != 2):
                List[ind1+ind2].append((i.TTag.Xindex,m.EquTempAppXindex))
                List[ind1+ind2].append((m.EquTempAppXindex,i.TTag.Xindex))
                 
            if (i.PTag.Flag !=2):
                List[ind1+ind2].append((i.PTag.Xindex,i.PTag.Xindex))
            for j in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[ind1+ind2].append((i.PTag.Xindex,i.CTag[j].Xindex))
                    List[ind1+ind2].append((i.CTag[j].Xindex,i.PTag.Xindex))
            if (i.PTag.Flag != 2 and m.EquTempAppFlag != 2):
                List[ind1+ind2].append((i.PTag.Xindex,m.EquTempAppXindex))
                List[ind1+ind2].append((m.EquTempAppXindex,i.PTag.Xindex))
                 
            for i1,k in enumerate(i.CTag.keys()):
                for i2,j in enumerate(i.CTag.keys()):
                    if (i2>=i1):
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            List[ind1+ind2].append((i.CTag[k].Xindex,i.CTag[j].Xindex))
                            if (i1!=i2):
                                List[ind1+ind2].append((i.CTag[j].Xindex,i.CTag[k].Xindex))
                if (i.CTag[k].Flag != 2 and m.EquTempAppFlag != 2):
                    List[ind1+ind2].append((i.CTag[k].Xindex,m.EquTempAppXindex))
                    List[ind1+ind2].append((m.EquTempAppXindex,i.CTag[k].Xindex))
            if (m.EquTempAppFlag != 2):
                List[ind1+ind2].append((m.EquTempAppXindex,m.EquTempAppXindex))
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
            if (i.TTag.Flag != 2 and j.EquTempAppFlag != 2):
                Dic[(i.TTag.Xindex,j.EquTempAppXindex)]=ECHessDic[j][(i.TTag,j)]
                Dic[(j.EquTempAppXindex,i.TTag.Xindex)]=ECHessDic[j][(i.TTag,j)]
                 
            if (i.PTag.Flag !=2):
                Dic[(i.PTag.Xindex,i.PTag.Xindex)]=ECHessDic[j][(i.PTag,i.PTag)]
            for k in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[k].Flag !=2):
                    Dic[(i.PTag.Xindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.PTag,i.CTag[k])]
                    Dic[(i.CTag[k].Xindex,i.PTag.Xindex)]=ECHessDic[j][(i.PTag,i.CTag[k])]
            if (i.PTag.Flag != 2 and j.EquTempAppFlag != 2):
                Dic[(i.PTag.Xindex,j.EquTempAppXindex)]=ECHessDic[j][(i.PTag,j)]
                Dic[(j.EquTempAppXindex,i.PTag.Xindex)]=ECHessDic[j][(i.PTag,j)]
                 
            for ind1,k in enumerate(i.CTag.keys()):
                for ind2,m in enumerate(i.CTag.keys()):
                    if (ind2>=ind1):
                        if (i.CTag[k].Flag !=2 and i.CTag[m].Flag !=2):
                            Dic[(i.CTag[k].Xindex,i.CTag[m].Xindex)]=ECHessDic[j][(i.CTag[k],i.CTag[m])]
                            if (ind1!=ind2):
                                Dic[(i.CTag[m].Xindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.CTag[k],i.CTag[m])]
                if (i.CTag[k].Flag != 2 and j.EquTempAppFlag != 2):
                    Dic[(i.CTag[k].Xindex,j.EquTempAppXindex)]=ECHessDic[j][(i.CTag[k],j)]
                    Dic[(j.EquTempAppXindex,i.CTag[k].Xindex)]=ECHessDic[j][(i.CTag[k],j)]
            if (j.EquTempAppFlag != 2):
                Dic[(j.EquTempAppXindex,j.EquTempAppXindex)]=ECHessDic[j][(j,j)]
            List.append(Dic)
        return List