'''
Created on Jun 19, 2014
This class assumes that the hot fluid is flowing in the shell side and the cold fluid is folwing in the tube side
@author: Senthil
'''
import math
from numpy import zeros
from numpy import ones
from numpy import inf
class HeatExchanger:
    def __init__(self,Name,Shellin,Shellout,Tubein,Tubeout,area=1,Type=1,ShellDp=0,TubeDp=0):
        self.Name=Name
        self.Shellin=Shellin
        self.Shellout=Shellout
        self.Tubein=Tubein
        self.Tubeout=Tubeout
        self.area=area
        self.Resid=[]
        self.UXindex=[]
        #self.U=100
        # Type=1 stands for countercurrent
        self.Type=Type
        self.ShellDp=ShellDp
        self.TubeDp=TubeDp
        self.LenMatRes = 2
        self.LenCompRes = len(self.Shellin.CTag.keys()) + len(self.Tubeout.CTag.keys()) - 2
        if (self.Type == 1 or self.Type == 2):
            self.LenEneRes = 3
        else:
            self.LenEneRes = 1
        self.U=self.UEst()
        self.LenPreRes = 2
    def UEst(self):
        Q=(self.Shellin.FTag.Est*self.Shellin.h-self.Shellout.FTag.Est*self.Shellout.h)
        if (self.Type==1):
            dT1=(self.Shellin.TTag.Est-self.Tubeout.TTag.Est)
            dT2=(self.Shellout.TTag.Est-self.Tubein.TTag.Est)
            dTLMTD=(dT1-dT2)/math.log(dT1/dT2)
            U=Q/(self.area*dTLMTD)
        elif (self.Type==2):
            dT1=(self.Shellin.TTag.Est-self.Tubein.TTag.Est)
            dT2=(self.Shellout.TTag.Est-self.Tubeout.TTag.Est)
            dTLMTD=(dT1-dT2)/math.log(dT1/dT2)
            U=Q/(self.area*dTLMTD)
        else:
            U=0.0
        return U
    def MaterialBalRes(self):
        Resid=[]
        Resid.append(1-self.Shellout.FTag.Est/self.Shellin.FTag.Est)
        Resid.append(1-self.Tubeout.FTag.Est/self.Tubein.FTag.Est)
        return Resid
    
    def ComponentBalRes(self):
        Resid=[]
        ShellComp=self.Shellin.CTag.keys()
        for i in ShellComp[:-1]:
            Resid.append(1-self.Shellout.FTag.Est*self.Shellout.CTag[i].Est/(self.Shellin.FTag.Est*self.Shellin.CTag[i].Est))
        TubeComp=self.Tubein.CTag.keys()
        for i in TubeComp[:-1]:
            Resid.append(1-self.Tubeout.FTag.Est*self.Tubeout.CTag[i].Est/(self.Tubein.FTag.Est*self.Tubein.CTag[i].Est))
        return Resid
    
    def EnergyBalRes(self):
        Resid=[]
        QShell= 1-self.Shellout.FTag.Est*self.Shellout.h/(self.Shellin.FTag.Est*self.Shellin.h)
        QTube=(self.Tubein.FTag.Est*self.Tubein.h-self.Tubeout.FTag.Est*self.Tubeout.h)/(self.Shellin.FTag.Est*self.Shellin.h)
        Resid.append(QShell+QTube)
#         if (self.Type==1):
#             dT1=(self.Shellin.TTag.Est-self.Tubeout.TTag.Est)
#             dT2=(self.Shellout.TTag.Est-self.Tubein.TTag.Est)
#         else:
#             dT1=(self.Shellin.TTag.Est-self.Tubein.TTag.Est)
#             dT2=(self.Shellout.TTag.Est-self.Tubeout.TTag.Est)
#         dTLMTD=(dT1-dT2)/math.log(dT1/dT2)
#         Resid.append(QShell-self.U*self.area*dTLMTD)
        if (self.Type == 1): #counter-current
            Resid.append(self.Tubeout.TTag.Est/self.Shellin.TTag.Est)
            Resid.append(self.Tubein.TTag.Est/self.Shellout.TTag.Est )
        elif (self.Type ==2 ): #co-current
            Resid.append(self.Tubein.TTag.Est/self.Shellin.TTag.Est)
            Resid.append(self.Tubeout.TTag.Est/self.Shellout.TTag.Est)                    
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(1 - (self.Shellout.PTag.Est + self.ShellDp)/self.Shellin.PTag.Est)
        Resid.append(1 - (self.Tubeout.PTag.Est + self.TubeDp)/self.Tubein.PTag.Est)
        return Resid
    
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
        if (self.Type ==1 or self.Type == 2):
            UB[1]=1
            UB[2]=1
        return LB,UB
    
    def PressureBalBound(self):
        LB=zeros((self.LenPreRes))
        UB=zeros((self.LenPreRes))
        return LB,UB
    
    def MaterialBalJaco(self,len1):
        J=zeros((self.LenMatRes,len1))
        if (self.Shellin.FTag.Flag != 2):
            J[0,self.Shellin.FTag.Xindex] = self.Shellout.FTag.Est/self.Shellin.FTag.Est**2
        if (self.Shellout.FTag.Flag != 2):
            J[0,self.Shellout.FTag.Xindex] = -1.0/self.Shellin.FTag.Est
        if (self.Tubein.FTag.Flag != 2):
            J[1,self.Tubein.FTag.Xindex] = self.Tubeout.FTag.Est/self.Tubein.FTag.Est**2
        if (self.Tubeout.FTag.Xindex != 2):
            J[1,self.Tubeout.FTag.Xindex] = -1.0/self.Tubein.FTag.Est
        return J
    
    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        shellcomp=self.Shellin.CTag.keys()
        for ind,i in enumerate(shellcomp[:-1]):
            if (self.Shellin.FTag.Flag != 2):
                J[ind,self.Shellin.FTag.Xindex] = (self.Shellout.CTag[i].Est*self.Shellout.FTag.Est)/(self.Shellin.CTag[i].Est*self.Shellin.FTag.Est**2)
            if (self.Shellin.CTag[i].Flag != 2):
                J[ind,self.Shellin.CTag[i].Xindex] = (self.Shellout.CTag[i].Est * self.Shellout.FTag.Est)/(self.Shellin.FTag.Est * self.Shellin.CTag[i].Est **2)
            if (self.Shellout.FTag.Flag != 2):
                J[ind,self.Shellout.FTag.Xindex] = -self.Shellout.CTag[i].Est/(self.Shellin.CTag[i].Est * self.Shellin.FTag.Est)
            if (self.Shellout.CTag[i].Flag != 2):
                J[ind,self.Shellout.CTag[i].Xindex] = -self.Shellout.FTag.Est/(self.Shellin.CTag[i].Est * self.Shellin.FTag.Est)
        
        TubeComp = self.Tubein.CTag.keys()
        
        for ind,i in enumerate(TubeComp[:-1]):
            if (self.Tubein.FTag.Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubein.FTag.Xindex] = (self.Tubeout.CTag[i].Est*self.Tubeout.FTag.Est)/(self.Tubein.CTag[i].Est*self.Tubein.FTag.Est**2)
            if (self.Tubein.CTag[i].Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubein.CTag[i].Xindex] = (self.Tubeout.CTag[i].Est * self.Tubeout.FTag.Est)/(self.Tubein.FTag.Est * self.Tubein.CTag[i].Est **2)
            if (self.Tubeout.FTag.Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubeout.FTag.Xindex] = -self.Tubeout.CTag[i].Est/(self.Tubein.CTag[i].Est * self.Tubein.FTag.Est)
            if (self.Tubeout.CTag[i].Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubeout.CTag[i].Xindex]= -self.Tubeout.FTag.Est/(self.Tubein.CTag[i].Est * self.Tubein.FTag.Est)      
        return J
    
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        # Shell side Energy balance Starts
#         if (self.Type==1):
#             dT1=(self.Shellin.TTag.Est - self.Tubeout.TTag.Est)
#             dT2=(self.Shellout.TTag.Est - self.Tubein.TTag.Est)
#         else:
#             dT1=(self.Shellin.TTag.Est - self.Tubein.TTag.Est)
#             dT2=(self.Shellout.TTag.Est - self.Tubeout.TTag.Est)
#         B=dT1/dT2
#         dTLMTD=(dT1-dT2)/math.log(dT1/dT2)
        Term1 = self.Shellout.FTag.Est * self.Shellout.h - self.Tubein.FTag.Est * self.Tubein.h + self.Tubeout.FTag.Est * self.Tubeout.h
        i=self.Shellin
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=Term1/(i.h*i.FTag.Est**2)
#             J[1,i.FTag.Xindex]=i.h    
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)
#             dAdT= 1/math.log(B) - (1-1/B)/(math.log(B))**2
#             J[1,i.TTag.Xindex]= i.FTag.Est*dhdt - self.U * self.area * dAdT
                       
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)
#             J[1,i.PTag.Xindex]=i.FTag.Est*dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)
#                 J[1,i.CTag[j].Xindex]=i.FTag.Est*dhdt
        i = self.Shellout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h/(self.Shellin.FTag.Est * self.Shellin.h)
#             J[1,i.FTag.Xindex]=-i.h
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
#             dAdT=-1/math.log(B) +(B - 1)/(math.log(B))**2
#             J[1,i.TTag.Xindex]=-i.FTag.Est*dhdt - self.U * self.area * dAdT
                           
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
#             J[1,i.PTag.Xindex]=-i.FTag.Est*dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
#                 J[1,i.CTag[j].Xindex]=-i.FTag.Est*dhdt
        # Shell side energy Balance ends and Tube side energy balance starts
        i=self.Tubein
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=i.h/(self.Shellin.FTag.Est * self.Shellin.h)
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]=i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
#             if (self.Type==1):
#                 dAdT=1/math.log(B) - (B-1)/(math.log(B))**2
#             else:
#                 dAdT=-1/math.log(B) + (1-1/B)/(math.log(B))**2
#             J[1,i.TTag.Xindex]= -self.U*self.area*dAdT
                
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]=i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]=i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
        i=self.Tubeout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h/(self.Shellin.FTag.Est * self.Shellin.h)    
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
#             if (self.Type==1):
#                 dAdT=-1/math.log(B) - (1-1/B)/(math.log(B))**2
#             else:
#                 dAdT=1/math.log(B) - (B-1)/(math.log(B))**2
#             J[1,i.TTag.Xindex]= -self.U*self.area*dAdT           
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]=-i.FTag.Est*dhdt/(self.Shellin.FTag.Est * self.Shellin.h)
        
#         J[1,self.UXindex]= -self.area*dTLMTD
        
        if (self.Type == 1): #Counter-Current
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= -self.Tubeout.TTag.Est/self.Shellin.TTag.Est**2
            if (self.Tubeout.TTag.Flag != 2):
                J[1,self.Tubeout.TTag.Xindex]= 1/self.Shellin.TTag.Est
                
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= -self.Tubein.TTag.Est/self.Shellout.TTag.Est**2
            if (self.Tubein.TTag.Flag != 2):
                J[2,self.Tubein.TTag.Xindex]= 1/self.Shellout.TTag.Est
        elif (self.Type == 2):  #Co-Current              
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= -self.Tubein.TTag.Est/self.Shellin.TTag.Est**2
            if (self.Tubein.TTag.Flag != 2):
                J[1,self.Tubein.TTag.Xindex]= 1/self.Shellin.TTag.Est
                 
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= -self.Tubeout.TTag.Est/self.Shellout.TTag.Est**2
            if (self.Tubeout.TTag.Flag != 2):
                J[2,self.Tubeout.TTag.Xindex]= 1/self.Shellout.TTag.Est
        
        return J
    
    def EnergyBalJaco1(self,len1): #numerical implementation
        J=zeros((self.LenEneRes,len1))
        res=self.EnergyBalRes()
        List=[self.Shellin,self.Shellout,self.Tubein,self.Tubeout]
        for i in List:
            if (i.FTag.Flag!=2):
                x=i.FTag.Est      
                dx=x*1e-5
                i.FTag.Est=x+dx
                res1=self.EnergyBalRes()            
                i.FTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                J[0,i.FTag.Xindex]=dhdt
            
            if (i.TTag.Flag!=2):            
                x=i.TTag.Est      
                dx=x*1e-5
                i.TTag.Est=x+dx
                res1=self.EnergyBalRes()            
                i.TTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                print dhdt
                J[0,i.TTag.Xindex]=dhdt
                #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            

            if (i.PTag.Flag!=2):
                x=i.PTag.Est
                dx=x*1e-5
                i.PTag.Est=x+dx
                res1=self.EnergyBalRes()
                i.PTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                J[0,i.PTag.Xindex]=dhdt
                #J[0,i.PTag.Xindex]=0

            for j in i.CTag.keys():
                if (i.CTag[j].Flag!=2):
                    x=i.CTag[j].Est
                    dx=x*1e-5
                    i.CTag[j].Est=x+dx
                    res1=self.EnergyBalRes()
                    i.CTag[j].Est=x
                    dhdt=(res1[0]-res[0])/dx
                    J[0,i.CTag[j].Xindex]=dhdt
                        
        if (self.Type == 1): #Counter-Current
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= -self.Tubeout.TTag.Est/self.Shellin.TTag.Est**2
            if (self.Tubeout.TTag.Flag != 2):
                J[1,self.Tubeout.TTag.Xindex]= 1/self.Shellin.TTag.Est
                
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= -self.Tubein.TTag.Est/self.Shellout.TTag.Est**2
            if (self.Tubein.TTag.Flag != 2):
                J[2,self.Tubein.TTag.Xindex]= 1/self.Shellout.TTag.Est
        elif (self.Type == 2):  #Co-Current              
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= -self.Tubein.TTag.Est/self.Shellin.TTag.Est**2
            if (self.Tubein.TTag.Flag != 2):
                J[1,self.Tubein.TTag.Xindex]= 1/self.Shellin.TTag.Est
                 
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= -self.Tubeout.TTag.Est/self.Shellout.TTag.Est**2
            if (self.Tubeout.TTag.Flag != 2):
                J[2,self.Tubeout.TTag.Xindex]= 1/self.Shellout.TTag.Est
       
        return J


    def PressureBalJaco(self,len1):
        J=zeros((2,len1))
        if (self.Shellin.PTag.Flag != 2):
            J[0,self.Shellin.PTag.Xindex] = (self.ShellDp+self.Shellout.PTag.Est)/self.Shellin.PTag.Est**2#1
        if (self.Shellout.PTag.Flag != 2):
            J[0,self.Shellout.PTag.Xindex] = -1/self.Shellin.PTag.Est
        if (self.Tubein.PTag.Flag != 2):
            J[1,self.Tubein.PTag.Xindex] = (self.TubeDp+self.Tubeout.PTag.Est)/self.Tubein.PTag.Est**2#1
        if (self.Tubeout.PTag.Flag != 2):
            J[1,self.Tubeout.PTag.Xindex] = -1/self.Tubein.PTag.Est
        return J
    
    def MaterialBalJacoNZP(self):
        row=[]
        col=[]
        if (self.Shellin.FTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.FTag.Xindex)
        if (self.Shellout.FTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.FTag.Xindex)
        if (self.Tubein.FTag.Flag != 2):
            row.append(1)
            col.append(self.Tubein.FTag.Xindex)
        if (self.Tubeout.FTag.Xindex != 2):
            row.append(1)
            col.append(self.Tubeout.FTag.Xindex)
        return row,col
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        shellcomp=self.Shellin.CTag.keys()
        for ind,i in enumerate(shellcomp[:-1]):
            if (self.Shellin.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Shellin.FTag.Xindex)
            if (self.Shellin.CTag[i].Flag != 2):
                row.append(ind)
                col.append(self.Shellin.CTag[i].Xindex)
            if (self.Shellout.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Shellout.FTag.Xindex)
            if (self.Shellout.CTag[i].Flag != 2):
                row.append(ind)
                col.append(self.Shellout.CTag[i].Xindex)             
        TubeComp = self.Tubein.CTag.keys()
        NShellCompRes=len(shellcomp)-1
        for ind,i in enumerate(TubeComp[:-1]):
            if (self.Tubein.FTag.Flag != 2):
                row.append(NShellCompRes+ind)
                col.append(self.Tubein.FTag.Xindex)
            if (self.Tubein.CTag[i].Flag != 2):
                row.append(NShellCompRes+ind)
                col.append(self.Tubein.CTag[i].Xindex)
            if (self.Tubeout.FTag.Flag != 2):
                row.append(NShellCompRes+ind)
                col.append(self.Tubeout.FTag.Xindex)
            if (self.Tubeout.CTag[i].Flag != 2):
                row.append(NShellCompRes+ind)
                col.append(self.Tubeout.CTag[i].Xindex)
  
        return row,col
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
        i=self.Shellin
        if (self.Shellin.FTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.FTag.Xindex)
#             row.append(1)
#             col.append(self.Shellin.FTag.Xindex)
        if (self.Shellin.TTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.TTag.Xindex)
#             row.append(1)
#             col.append(self.Shellin.TTag.Xindex)
        if (self.Shellin.PTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.PTag.Xindex)
#             row.append(1)
#             col.append(self.Shellin.PTag.Xindex)
        for i in self.Shellin.CTag.keys():
            if (self.Shellin.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Shellin.CTag[i].Xindex)
#                 row.append(1)
#                 col.append(self.Shellin.CTag[i].Xindex)
        
        if (self.Shellout.FTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.FTag.Xindex)
#             row.append(1)
#             col.append(self.Shellout.FTag.Xindex)
        if (self.Shellout.TTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.TTag.Xindex)
#             row.append(1)
#             col.append(self.Shellout.FTag.Xindex)
        if (self.Shellout.PTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.PTag.Xindex)
#             row.append(1)
#             col.append(self.Shellout.PTag.Xindex)
        for i in self.Shellout.CTag.keys():
            if (self.Shellout.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Shellout.CTag[i].Xindex)
#                 row.append(1)
#                 col.append(self.Shellout.CTag[i].Xindex)
        
        if (self.Tubein.FTag.Flag != 2):    
            row.append(0)
            col.append(self.Tubein.FTag.Xindex)
        if (self.Tubein.TTag.Flag != 2):
            row.append(0)
            col.append(self.Tubein.TTag.Xindex)
#             row.append(1)
#             col.append(self.Tubein.TTag.Xindex)
        if (self.Tubein.PTag.Flag != 2):
            row.append(0)
            col.append(self.Tubein.PTag.Xindex)
        for i in self.Tubein.CTag.keys():
            if (self.Tubein.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Tubein.CTag[i].Xindex)
        
        if (self.Tubeout.FTag.Flag != 2):
            row.append(0)
            col.append(self.Tubeout.FTag.Xindex)
        if (self.Tubeout.TTag.Flag != 2):
            row.append(0)
            col.append(self.Tubeout.TTag.Xindex)
#             row.append(1)
#             col.append(self.Tubeout.TTag.Xindex)
        if (self.Tubeout.PTag.Flag != 2):
            row.append(0)
            col.append(self.Tubeout.PTag.Xindex)
        for i in self.Tubeout.CTag.keys():
            if (self.Tubeout.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Tubeout.CTag[i].Xindex)
#         row.append(1)
#         col.append(self.UXindex)
        if (self.Type==1): #Counter Current          
            if (self.Shellin.TTag.Flag != 2):
                row.append(1)
                col.append(self.Shellin.TTag.Xindex)
            if (self.Tubeout.TTag.Flag != 2):
                row.append(1)
                col.append(self.Tubeout.TTag.Xindex)
               
            if (self.Shellout.TTag.Flag != 2):
                row.append(2)
                col.append(self.Shellout.TTag.Xindex)
            if (self.Tubein.TTag.Flag != 2):
                row.append(2)
                col.append(self.Tubein.TTag.Xindex)
        elif (self.Type == 2): #Co-Current
            if (self.Shellin.TTag.Flag != 2):
                row.append(1)
                col.append(self.Shellin.TTag.Xindex)
            if (self.Tubein.TTag.Flag != 2):
                row.append(1)
                col.append(self.Tubein.TTag.Xindex)
                
            if (self.Shellout.TTag.Flag != 2):
                row.append(2)
                col.append(self.Shellout.TTag.Xindex)
            if (self.Tubeout.TTag.Flag != 2):
                row.append(2)
                col.append(self.Tubeout.TTag.Xindex)           
        return row,col
    
    def PressureBalJacoNZP(self):
        row=[]
        col=[]
        if (self.Shellin.PTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.PTag.Xindex)
        if (self.Shellout.PTag.Flag != 2): 
            row.append(0)
            col.append(self.Shellout.PTag.Xindex)
        if (self.Tubein.PTag.Flag != 2):
            row.append(1)
            col.append(self.Tubein.PTag.Xindex)
        if (self.Tubeout.PTag.Flag != 2):
            row.append(1)
            col.append(self.Tubeout.PTag.Xindex)
        return row,col