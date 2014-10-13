'''
Created on 16-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from numpy.linalg import pinv
from numpy import dot
class Reactor:
    def __init__(self,Name,Rstrm,Pstrm,Qstrm,Rxn,ExoEndoFlag=1,dp=0):
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
        self.EFlag=ExoEndoFlag
        self.LenMatRes=0
        self.LenCompRes=len(self.ListComp)
        self.LenEneRes=1
        self.LenPreRes=1
        self.RxnExt=self.InitialGuessRxnExt()
        self.MB_SF=abs(asarray(self.MaterialBalRes()))
        self.CB_SF=abs(asarray(self.ComponentBalRes()))
        self.EB_SF=abs(asarray(self.EnergyBalRes()))
        self.PB_SF=abs(asarray(self.PressureBalRes()))
        self.CheckForZero()
    
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

    def StoichioMatrix(self):
        NRxn=len(self.Rxn)
        NComp=len(self.ListComp)
        SMat=zeros((NComp,NRxn))
        for ind1,i in enumerate(self.ListComp):
            for ind2,j in enumerate(self.RxnExt.keys()):
                if (i in j.Coef.keys()):
                    SMat[ind1,ind2]=j.Coef[i]
        return SMat
    
    def Const(self):
        NComp=len(self.ListComp)
        b=zeros((NComp,1))
        for ind,i in enumerate(self.ListComp):
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.FreeBasis==[]):
                    Temp1=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas
                else:
                    if (self.Pstrm.FreeBasis[0]==i):
                        Temp1=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas
                    else:
                        Temp1=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas * (1.0-self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Meas)
            else:
                Temp1=0
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FreeBasis==[]):
                    Temp2=self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas
                else:
                    if (self.Rstrm.FreeBasis[0]==i):
                        Temp2=self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas
                    else:    
                        Temp2=self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas * (1.0-self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Meas)
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
        for ind,i in enumerate(self.RxnExt.keys()):
            RxnExt[i]=Ext[ind,0]
        return RxnExt
                
                
    
    def MaterialBalRes(self):
        Resid=[]
        return Resid
    
    def ComponentBalRes(self):
        Resid=[]
        for i in self.ListComp:
            sumC=0.0
            for j in self.RxnExt.keys():
                if (i in j.Coef.keys()):
                    sumC=sumC+j.Coef[i]*self.RxnExt[j]
            
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FreeBasis==[]):
                    inletcomp=self.Rstrm.FTag.Est*self.Rstrm.CTag[i].Est
                else:
                    if (self.Rstrm.FreeBasis[0]==i):
                        inletcomp=self.Rstrm.FTag.Est*self.Rstrm.CTag[i].Est
                    else:
                        inletcomp=self.Rstrm.FTag.Est * self.Rstrm.CTag[i].Est * (1.0-self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Est)
            else:
                inletcomp=0.0
            
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.FreeBasis==[]):
                    outletcomp=self.Pstrm.FTag.Est*self.Pstrm.CTag[i].Est
                else:
                    if (self.Pstrm.FreeBasis[0]==i):
                        outletcomp=self.Pstrm.FTag.Est*self.Pstrm.CTag[i].Est
                    else:
                        outletcomp=self.Pstrm.FTag.Est * self.Pstrm.CTag[i].Est * (1.0-self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Est)
            else:
                outletcomp=0.0
            Resid.append(inletcomp-outletcomp+sumC)
        return Resid
    
    def EnergyBalRes(self):
        Resid=[]
        sumH=0.0
        for i in self.Qstrm:
            sumH=sumH+i.Q.Est*self.EFlag
        Resid.append(self.Rstrm.h * self.Rstrm.FTag.Est + sumH - self.Pstrm.h * self.Pstrm.FTag.Est)
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(self.Rstrm.PTag.Est - self.Pstrm.PTag.Est - self.Dp)
        return Resid
    
    def MaterialBalJaco(self,len1):
        J = zeros((self.LenMatRes,len1))
        return J
    def ComponentBalJaco(self,len1):
        J = zeros((self.LenCompRes,len1))
        for ind,i in enumerate(self.ListComp):
            for j in self.RxnExt.keys():
                if (i in j.Coef.keys()):
                    J[ind,self.RxnExtXindex[j]] = j.Coef[i]
            
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.CTag[i].Flag != 2):
                    if (self.Rstrm.FreeBasis==[]):
                        J[ind,self.Rstrm.CTag[i].Xindex] = self.Rstrm.FTag.Est
                    else:
                        if (self.Rstrm.FreeBasis[0]==i):
                            J[ind,self.Rstrm.CTag[i].Xindex] = self.Rstrm.FTag.Est
                        else:
                            J[ind,self.Rstrm.CTag[i].Xindex] = self.Rstrm.FTag.Est*(1.0-self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Est)
                            j[ind,self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex]=-self.Rstrm.FTag.Est * self.Rstrm.CTag[i].Est
                
                if (self.Rstrm.FTag.Flag !=2):
                    if (self.Rstrm.FreeBasis==[]):
                        J[ind,self.Rstrm.FTag.Xindex] = self.Rstrm.CTag[i].Est
                    else:
                        if (self.Rstrm.FreeBasis[0]==i):
                            J[ind,self.Rstrm.FTag.Xindex] = self.Rstrm.CTag[i].Est
                        else:
                            J[ind,self.Rstrm.FTag.Xindex] = self.Rstrm.CTag[i].Est*(1.0-self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Est)
            
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.CTag[i].Flag !=2):
                    if (self.Pstrm.FreeBasis==[]):
                        J[ind,self.Pstrm.CTag[i].Xindex] = -self.Pstrm.FTag.Est
                    else:
                        if (self.Pstrm.FreeBasis[0]==i):
                            J[ind,self.Pstrm.CTag[i].Xindex] = -self.Pstrm.FTag.Est
                        else:
                            J[ind,self.Pstrm.CTag[i].Xindex] = -self.Pstrm.FTag.Est*(1.0-self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Est)
                            j[ind,self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex] = self.Pstrm.FTag.Est * self.Pstrm.CTag[i].Est
                                
                if (self.Pstrm.FTag.Flag != 2):
                    if (self.Pstrm.FreeBasis==[]):
                        J[ind,self.Pstrm.FTag.Xindex] = -self.Pstrm.CTag[i].Est
                    else:
                        if (self.Pstrm.FreeBasis[0]==i):
                            J[ind,self.Pstrm.FTag.Xindex] = -self.Pstrm.CTag[i].Est
                        else:
                            J[ind,self.Pstrm.FTag.Xindex] = -self.Pstrm.CTag[i].Est*(1.0-self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Est)
        return J
    
    def EnergyBalJaco(self,len1):
        J = zeros((self.LenEneRes,len1))
        for i in self.Qstrm:
            if (i.Q.Flag !=2):
                J[0,i.Q.Xindex] = self.EFlag
        
        i=self.Rstrm
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= i.h
             
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex] = i.FTag.Est * i.GradDic[i.TTag]#dhdt           
            
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est * i.GradDic[i.PTag]#dhdt
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est * i.GradDic[i.CTag[j]]#dhdt
  
        i=self.Pstrm
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= -i.h
         
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex] = -i.FTag.Est * i.GradDic[i.TTag]#dhdt          
            
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= -i.FTag.Est * i.GradDic[i.PTag]#dhdt
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= -i.FTag.Est * i.GradDic[i.CTag[j]]#dhdt
        return J
    
    def PressureBalJaco(self,len1):
        J=zeros((self.LenPreRes,len1))
        if (self.Rstrm.PTag.Flag != 2):
            J[0,self.Rstrm.PTag.Xindex] = 1.0
        if (self.Pstrm.PTag.Flag != 2):
            J[0,self.Pstrm.PTag.Xindex] = -1.0
        return J
    
    def MaterialBalJacoNZP(self):
        row=[]
        col=[]
        return row,col
    
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
                if (self.Rstrm.FreeBasis!=[]):
                    if (self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Flag !=2):
                        row.append(ind)
                        col.append(self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex)
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.CTag[i].Flag !=2):
                    row.append(ind)
                    col.append(self.Pstrm.CTag[i].Xindex)
                if (self.Pstrm.FreeBasis!=[]):
                    if (self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Flag !=2):
                        row.append(ind)
                        col.append(self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex)                    
            if (self.Rstrm.FTag.Flag !=2):
                row.append(ind)
                col.append(self.Rstrm.FTag.Xindex)            
            if (self.Pstrm.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Pstrm.FTag.Xindex)
        return row,col
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
         
        for i in self.Qstrm:
            if (i.Q.Flag !=2):
                row.append(0)
                col.append(i.Q.Xindex)
                   
        i=self.Rstrm
        if (i.FTag.Flag!=2):
            row.append(0)
            col.append(i.FTag.Xindex)
        if (i.TTag.Flag!=2):
            row.append(0)
            col.append(i.TTag.Xindex)                       
        if (i.PTag.Flag!=2):
            row.append(0)
            col.append(i.PTag.Xindex)           
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                row.append(0)
                col.append(i.CTag[j].Xindex)

        i=self.Pstrm
        if (i.FTag.Flag!=2):
            row.append(0)
            col.append(i.FTag.Xindex)         
        if (i.TTag.Flag!=2):
            row.append(0)
            col.append(i.TTag.Xindex)            
        if (i.PTag.Flag!=2):
            row.append(0)
            col.append(i.PTag.Xindex)
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                row.append(0)
                col.append(i.CTag[j].Xindex)
        return row,col
    
    def PressureBalJacoNZP(self):
        row=[]
        col=[]
        if (self.Rstrm.PTag.Flag != 2):
            row.append(0)
            col.append(self.Rstrm.PTag.Xindex)
        if (self.Pstrm.PTag.Flag != 2):
            row.append(0)
            col.append(self.Pstrm.PTag.Xindex)
        return row,col
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        for ind1,i in enumerate(self.ListComp):
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[i].Flag !=2):
                    List[ind1].append((self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex))
                    List[ind1].append((self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex))
                if (self.Rstrm.FreeBasis !=[]):
                    if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Flag !=2):
                        List[ind1].append((self.Rstrm.FTag.Xindex,self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex))
                        List[ind1].append((self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex,self.Rstrm.FTag.Xindex))
                    if (self.Rstrm.CTag[i].Flag !=2 and self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Flag !=2):
                        List[ind1].append((self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex,self.Rstrm.CTag[i].Xindex))
                        List[ind1].append((self.Rstrm.CTag[i].Xindex,self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex))
            if (i in self.Pstrm.CTag.keys()):
                if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[i].Flag !=2):
                    List[ind1].append((self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex))
                    List[ind1].append((self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex))
                if (self.Pstrm.FreeBasis !=[]):
                    if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Flag !=2):
                        List[ind1].append((self.Pstrm.FTag.Xindex,self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex))
                        List[ind1].append((self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex,self.Pstrm.FTag.Xindex))
                    if (self.Pstrm.CTag[i].Flag !=2 and self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Flag !=2):
                        List[ind1].append((self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex,self.Pstrm.CTag[i].Xindex))
                        List[ind1].append((self.Pstrm.CTag[i].Xindex,self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex))
        return List
    
    def EnergyBalHessNZP(self):
        List=[[]]*self.LenEneRes
        StreamList=[self.Rstrm,self.Pstrm]
        for i in StreamList:
            if (i.FTag.Flag !=2 and i.TTag.Flag !=2):
                List[0].append((i.FTag.Xindex,i.TTag.Xindex))
                List[0].append((i.TTag.Xindex,i.FTag.Xindex))
            if (i.FTag.Flag !=2 and i.PTag.Flag !=2):
                List[0].append((i.FTag.Xindex,i.PTag.Xindex))
                List[0].append((i.PTag.Xindex,i.FTag.Xindex))
            for j in i.CTag.keys():
                if (i.FTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[0].append((i.FTag.Xindex,i.CTag[j].Xindex))
                    List[0].append((i.CTag[j].Xindex,i.FTag.Xindex))
            
            if (i.TTag.Flag !=2):
                List[0].append((i.TTag.Xindex,i.TTag.Xindex))
            if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
                List[0].append((i.TTag.Xindex,i.PTag.Xindex))
                List[0].append((i.PTag.Xindex,i.TTag.Xindex))
            for j in i.CTag.keys():
                if (i.TTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[0].append((i.TTag.Xindex,i.CTag[j].Xindex))
                    List[0].append((i.CTag[j].Xindex,i.TTag.Xindex))
                
            if (i.PTag.Flag !=2):
                List[0].append((i.PTag.Xindex,i.PTag.Xindex))
            for j in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[0].append((i.PTag.Xindex,i.CTag[j].Xindex))
                    List[0].append((i.CTag[j].Xindex,i.PTag.Xindex))
                
            for ind1,k in enumerate(i.CTag.keys()):
                for ind2,j in enumerate(i.CTag.keys()):
                    if (ind2>=ind1):
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            List[0].append((i.CTag[k].Xindex,i.CTag[j].Xindex))
                            if (ind1!=ind2):
                                List[0].append((i.CTag[j].Xindex,i.CTag[k].Xindex))
        return List
    
    def ComponentBalHess(self):
        List=[]
        for ind1,i in enumerate(self.ListComp):
            Dic={}
            if (i in self.Rstrm.CTag.keys()):
                if (self.Rstrm.FreeBasis == []):
                    if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[i].Flag !=2):
                        Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex)]=1.0
                        Dic[(self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex)]=1.0
                else:
                    if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[i].Flag !=2):
                        if (self.Rstrm.FreeBasis[0]==i):
                            Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex)]=1.0
                            Dic[(self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex)]=1.0
                        else:
                            Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[i].Xindex)]= (1.0-self.Rstrm.CTag[i].Est)
                            Dic[(self.Rstrm.CTag[i].Xindex,self.Rstrm.FTag.Xindex)]= (1.0-self.Rstrm.CTag[i].Est)
                    if (self.Rstrm.CTag[i].Flag !=2 and self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Flag !=2):
                        Dic[(self.Rstrm.CTag[i].Xindex,self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex)] = -self.Rstrm.FTag.Est
                        Dic[(self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex,self.Rstrm.CTag[i].Xindex)] = -self.Rstrm.FTag.Est
                    if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Flag !=2):
                        Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex)] = -self.Rstrm.CTag[i].Est
                        Dic[(self.Rstrm.CTag[self.Rstrm.FreeBasis[0]].Xindex,self.Rstrm.FTag.Xindex)] = -self.Rstrm.CTag[i].Est
                    
                            
            if (i in self.Pstrm.CTag.keys()):
                if (self.Rstrm.FreeBasis == []):
                    if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[i].Flag !=2):
                        Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex)]=-1.0
                        Dic[(self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex)]=-1.0
                else:
                    if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[i].Flag !=2):
                        if (self.Pstrm.FreeBasis[0]==i):
                            Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex)]=1.0
                            Dic[(self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex)]=1.0
                        else:
                            Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[i].Xindex)]= -(1.0-self.Pstrm.CTag[i].Est)
                            Dic[(self.Pstrm.CTag[i].Xindex,self.Pstrm.FTag.Xindex)]= -(1.0-self.Pstrm.CTag[i].Est)
                    if (self.Pstrm.CTag[i].Flag !=2 and self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Flag !=2):
                        Dic[(self.Pstrm.CTag[i].Xindex,self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex)] = self.Pstrm.FTag.Est
                        Dic[(self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex,self.Pstrm.CTag[i].Xindex)] = self.Pstrm.FTag.Est
                    if (self.Pstrm.FTag.Flag !=2 and self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Flag !=2):
                        Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex)] = self.Pstrm.CTag[i].Est
                        Dic[(self.Pstrm.CTag[self.Pstrm.FreeBasis[0]].Xindex,self.Pstrm.FTag.Xindex)] = self.Pstrm.CTag[i].Est
            List.append(Dic)
        return List
    
    def EnergyBalHess(self):
        List=[]
        Dic={}
        i=self.Rstrm
        if (i.FTag.Flag !=2 and i.TTag.Flag !=2):
            Dic[(i.FTag.Xindex,i.TTag.Xindex)]=i.GradDic[i.TTag]
            Dic[(i.TTag.Xindex,i.FTag.Xindex)]=i.GradDic[i.TTag]
        if (i.FTag.Flag !=2 and i.PTag.Flag !=2):
            Dic[(i.FTag.Xindex,i.PTag.Xindex)]=i.GradDic[i.PTag]
            Dic[(i.PTag.Xindex,i.FTag.Xindex)]=i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.FTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.FTag.Xindex,i.CTag[j].Xindex)]=i.GradDic[i.CTag[j]]
                Dic[(i.CTag[j].Xindex,i.FTag.Xindex)]=i.GradDic[i.CTag[j]]
        
        if (i.TTag.Flag !=2):
            Dic[(i.TTag.Xindex,i.TTag.Xindex)]=i.HessDic[(i.TTag,i.TTag)]*i.FTag.Est
        if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
            Dic[(i.TTag.Xindex,i.PTag.Xindex)]=i.HessDic[(i.TTag,i.PTag)]*i.FTag.Est
            Dic[(i.PTag.Xindex,i.TTag.Xindex)]=i.HessDic[(i.TTag,i.PTag)]*i.FTag.Est
        for j in i.CTag.keys():
            if (i.TTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.TTag.Xindex,i.CTag[j].Xindex)]=i.HessDic[(i.TTag,i.CTag[j])]*i.FTag.Est
                Dic[(i.CTag[j].Xindex,i.TTag.Xindex)]=i.HessDic[(i.TTag,i.CTag[j])]*i.FTag.Est
        
        if (i.PTag.Flag !=2):    
            Dic[(i.PTag.Xindex,i.PTag.Xindex)]=i.HessDic[(i.PTag,i.PTag)]*i.FTag.Est
        for j in i.CTag.keys():
            if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.PTag.Xindex,i.CTag[j].Xindex)]=i.HessDic[(i.PTag,i.CTag[j])]*i.FTag.Est
                Dic[(i.CTag[j].Xindex,i.PTag.Xindex)]=i.HessDic[(i.PTag,i.CTag[j])]*i.FTag.Est
            
        for ind1,k in enumerate(i.CTag.keys()):
            for ind2,j in enumerate(i.CTag.keys()):
                if (ind2>=ind1):
                    if (k==j):
                        if (i.CTag[j].Flag !=2):
                            Dic[(i.CTag[j].Xindex,i.CTag[j].Xindex)]=i.HessDic[(i.CTag[j],i.CTag[j])]*i.FTag.Est
                    else:
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            Dic[(i.CTag[k].Xindex,i.CTag[j].Xindex)]=i.HessDic[i.CTag[k],i.CTag[j]]*i.FTag.Est
                            Dic[(i.CTag[j].Xindex,i.CTag[k].Xindex)]=i.HessDic[i.CTag[k],i.CTag[j]]*i.FTag.Est
        '''Inlet streams being processed'''
        i=self.Pstrm
        if (i.FTag.Flag !=2 and i.TTag.Flag !=2):
                Dic[(i.FTag.Xindex,i.TTag.Xindex)]=-i.GradDic[i.TTag]
                Dic[(i.TTag.Xindex,i.FTag.Xindex)]=-i.GradDic[i.TTag]
        if (i.FTag.Flag !=2 and i.PTag.Flag !=2):
            Dic[(i.FTag.Xindex,i.PTag.Xindex)]=-i.GradDic[i.PTag]
            Dic[(i.PTag.Xindex,i.FTag.Xindex)]=-i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.FTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.FTag.Xindex,i.CTag[j].Xindex)]=-i.GradDic[i.CTag[j]]
                Dic[(i.CTag[j].Xindex,i.FTag.Xindex)]=-i.GradDic[i.CTag[j]]
        
        if (i.TTag.Flag !=2):
            Dic[(i.TTag.Xindex,i.TTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.TTag,i.TTag)]
        if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
            Dic[(i.TTag.Xindex,i.PTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.TTag,i.PTag)]
            Dic[(i.PTag.Xindex,i.TTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.TTag,i.PTag)]
        for j in i.CTag.keys():
            if (i.TTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.TTag.Xindex,i.CTag[j].Xindex)]=-i.FTag.Est*i.HessDic[(i.TTag,i.CTag[j])]
                Dic[(i.CTag[j].Xindex,i.TTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.TTag,i.CTag[j])]
        
        if (i.PTag.Flag !=2):    
            Dic[(i.PTag.Xindex,i.PTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.PTag,i.PTag)]   
        for j in i.CTag.keys():
            if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                Dic[(i.PTag.Xindex,i.CTag[j].Xindex)]=-i.FTag.Est*i.HessDic[(i.PTag,i.CTag[j])]
                Dic[(i.CTag[j].Xindex,i.PTag.Xindex)]=-i.FTag.Est*i.HessDic[(i.PTag,i.CTag[j])]
            
        for ind1,k in enumerate(i.CTag.keys()):
            for ind2,j in enumerate(i.CTag.keys()):
                if (ind2>=ind1):
                    if (k==j):
                        if (i.CTag[j].Flag !=2):
                            Dic[(i.CTag[j].Xindex,i.CTag[j].Xindex)]=-i.FTag.Est*i.HessDic[(i.CTag[j],i.CTag[j])]
                    else:
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            Dic[(i.CTag[k].Xindex,i.CTag[j].Xindex)]=-i.FTag.Est*i.HessDic[(i.CTag[k],i.CTag[j])]
                            Dic[(i.CTag[j].Xindex,i.CTag[k].Xindex)]=-i.FTag.Est*i.HessDic[(i.CTag[k],i.CTag[j])]
        List.append(Dic)
        return List

    
    def MaterialBalBound(self):
        LB=zeros((self.LenMatRes))
        UB=zeros((self.LenMatRes))
        return LB,UB
    
    def ComponentBalBound(self):
        LB=zeros((self.LenCompRes))
        UB=zeros((self.LenCompRes))
        return LB,UB
    
    def EnergyBalBound(self):
        LB=zeros((self.LenEneRes))
        UB=zeros((self.LenEneRes))
        return LB,UB
    
    def PressureBalBound(self):
        LB=zeros((self.LenPreRes))
        UB=zeros((self.LenPreRes))
        return LB,UB
