'''
Created on Jun 19, 2014

@author: Senthil
'''
from numpy import zeros
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
        self.InitialExt=self.InitialGuessRxnExt()        

    def StoichioMatrix(self):
        NRxn=len(self.RxnExt)
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
            b[ind,0]=self.Pstrm.FTag.Meas * self.Pstrm.CTag[i].Meas - self.Rstrm.FTag.Meas * self.Rstrm.CTag[i].Meas
        return b
    
    def InitialGuessRxnExt(self):
        A=self.StoichioMatrix()
        b=self.Const()
        B=pinv(dot(A.T,A))
        C=dot(B,A.T)
        Ext=dot(C,b)
        for ind,i in enumerate(self.RxnExt.keys()):
            self.RxnExt[i]=Ext[ind,0]
        return Ext
                
                
    
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
                inletcomp=self.Rstrm.FTag.Est*self.Rstrm.CTag[i].Est
            else:
                inletcomp=0.0
            if (i in self.Pstrm.CTag.keys()):
                outletcomp=self.Pstrm.FTag.Est*self.Pstrm.CTag[i].Est
            else:
                outletcomp=0.0
            Resid.append((inletcomp-outletcomp+sumC)/self.Rstrm.FTag.Est)
        return Resid
    
    def EnergyBalRes(self):
        Resid=[]
        sumH=0.0
        for i in self.Qstrm:
            sumH=sumH+i.Q.Est*self.EFlag
        Resid.append(1 + (sumH - self.Pstrm.h * self.Pstrm.FTag.Est)/(self.Rstrm.h * self.Rstrm.FTag.Est))
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(1 - (self.Pstrm.PTag.Est + self.Dp)/self.Rstrm.PTag.Est)
        return Resid
    
    def MaterialBalJaco(self,len1):
        J = zeros((self.LenMatRes,len1))
        return J
    def ComponentBalJaco(self,len1):
        J = zeros((self.LenCompRes,len1))
        Rconc=0.0
        Pconc=0.0
        for ind,i in enumerate(self.ListComp):
            sumC=0.0
            for j in self.RxnExt.keys():
                if (i in j.Coef.keys()):
                    J[ind,self.RxnExtXindex[j]] = j.Coef[i]/self.Rstrm.FTag.Est
                    sumC=sumC+j.Coef[i]*self.RxnExt[j]
            
            if (i in self.Rstrm.CTag.keys()):
                Rconc=self.Rstrm.CTag[i].Est
                if (self.Rstrm.CTag[i].Flag != 2):
                    J[ind,self.Rstrm.CTag[i].Xindex] = 1
            else:
                Rconc=0.0
            
            if (i in self.Pstrm.CTag.keys()):
                Pconc=self.Pstrm.CTag[i].Est
                if (self.Pstrm.CTag[i].Flag !=2):
                    J[ind,self.Pstrm.CTag[i].Xindex] = -self.Pstrm.FTag.Est/self.Rstrm.FTag.Est
            else:
                Pconc=0.0
                    
            if (self.Rstrm.FTag.Flag !=2):
                J[ind,self.Rstrm.FTag.Xindex] = -(sumC - self.Pstrm.FTag.Est * Pconc)/self.Rstrm.FTag.Est**2
            
            if (self.Pstrm.FTag.Flag != 2):
                J[ind,self.Pstrm.FTag.Xindex] = -Pconc/self.Rstrm.FTag.Est
        return J
    
    def EnergyBalJaco(self,len1):
        J = zeros((self.LenEneRes,len1))
        sumQ=0.0
        for i in self.Qstrm:
            #J[0,i.Xindex] = self.EFlag/(self.Rstrm.FTag.Est * self.Rstrm.h )
            if (i.Q.Flag !=2):
                J[0,i.Q.Xindex] = self.EFlag/(self.Rstrm.FTag.Est * self.Rstrm.h )
            sumQ=sumQ+i.Q.Est*self.EFlag
        
        i=self.Rstrm
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= -(sumQ - self.Pstrm.FTag.Est * self.Pstrm.h)/(i.h * i.FTag.Est**2)
             
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex] = -(sumQ - self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            
            
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= -(sumQ - self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.PTag.Xindex]=0
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= -(sumQ - self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)

        i=self.Pstrm
        Term1=self.Rstrm.FTag.Est * self.Rstrm.h
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= -i.h/Term1
         
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex] = -i.FTag.Est/Term1 * dhdt
            #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            
            
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= -i.FTag.Est/Term1 * dhdt
            #J[0,i.PTag.Xindex]=0
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= -i.FTag.Est/Term1 * dhdt
                #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)
        return J
    
    def PressureBalJaco(self,len1):
        J=zeros((self.LenPreRes,len1))
        if (self.Rstrm.PTag.Flag != 2):
            J[0,self.Rstrm.PTag.Xindex] = (self.Dp+self.Pstrm.PTag.Est)/self.Rstrm.PTag.Est**2
        if (self.Pstrm.PTag.Flag != 2):
            J[0,self.Pstrm.PTag.Xindex] = -1/self.Pstrm.PTag.Est
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
        return row,col
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
         
        for i in self.Qstrm:
            if (i.Q.Flag !=2):
                row.append(0)
                #col.append(i.Xindex)
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
   