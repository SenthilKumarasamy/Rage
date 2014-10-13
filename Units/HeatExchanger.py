'''
Created on 15-Aug-2014

@author: admin
'''
import math
from numpy import zeros
from numpy import ones
from numpy import inf
from numpy import asarray
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
        self.validation()
        self.U=self.UEst()
        self.LenPreRes = 2
        self.MB_SF=abs(asarray(self.MaterialBalRes()))
        self.CB_SF=abs(asarray(self.ComponentBalRes()))
        self.EB_SF=abs(asarray(self.EnergyBalRes()))
        self.PB_SF=abs(asarray(self.PressureBalRes()))
        self.CheckForZero()
    
    def validation(self):
        if (set(self.Shellin.CTag.keys()) !=set(self.Shellout.CTag.keys())):
            print 'Error in heat Exchanger : ',self.Name
            print 'Shell side inlet and outlet fluids have different set of components'
            exit()
        elif (set(self.Tubein.CTag.keys())!=set(self.Tubeout.CTag.keys())):
            print 'Error in heat Exchanger : ',self.Name
            print 'Tube side inlet and outlet fluids have different set of components'
            exit()

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
        Resid.append(self.Shellin.FTag.Est - self.Shellout.FTag.Est)
        Resid.append(self.Tubein.FTag.Est - self.Tubeout.FTag.Est)
        return Resid

    def ComponentBalRes(self):
        Resid=[]
        ShellComp=self.Shellin.CTag.keys()
        for i in ShellComp[:-1]:
            Resid.append(self.Shellin.CTag[i].Est - self.Shellout.CTag[i].Est)
        TubeComp=self.Tubein.CTag.keys()
        for i in TubeComp[:-1]:
            Resid.append(self.Tubein.CTag[i].Est - self.Tubeout.CTag[i].Est)
        return Resid
    
    def EnergyBalRes(self):
        Resid=[]
        QShell = self.Shellin.FTag.Est*self.Shellin.h-self.Shellout.FTag.Est*self.Shellout.h
        QTube = self.Tubein.FTag.Est*self.Tubein.h-self.Tubeout.FTag.Est*self.Tubeout.h
        Resid.append(QShell+QTube)
        if (self.Type == 1): #counter-current
            Resid.append(self.Shellin.TTag.Est - self.Tubeout.TTag.Est)
            Resid.append(self.Shellout.TTag.Est - self.Tubein.TTag.Est)
        elif (self.Type ==2 ): #co-current
            Resid.append(self.Shellin.TTag.Est - self.Tubein.TTag.Est)
            Resid.append(self.Shellout.TTag.Est - self.Tubeout.TTag.Est)                    
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(self.Shellin.PTag.Est - self.Shellout.PTag.Est - self.ShellDp)
        Resid.append(self.Tubein.PTag.Est - self.Tubeout.PTag.Est - self.TubeDp)
        return Resid
        
    def MaterialBalJaco(self,len1):
        J=zeros((self.LenMatRes,len1))
        if (self.Shellin.FTag.Flag != 2):
            J[0,self.Shellin.FTag.Xindex] = 1.0
        if (self.Shellout.FTag.Flag != 2):
            J[0,self.Shellout.FTag.Xindex] = -1.0
        if (self.Tubein.FTag.Flag != 2):
            J[1,self.Tubein.FTag.Xindex] = 1.0
        if (self.Tubeout.FTag.Xindex != 2):
            J[1,self.Tubeout.FTag.Xindex] = -1.0
        return J

    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        shellcomp=self.Shellin.CTag.keys()
        for ind,i in enumerate(shellcomp[:-1]):
            if (self.Shellin.CTag[i].Flag != 2):
                J[ind,self.Shellin.CTag[i].Xindex] = 1.0
            if (self.Shellout.CTag[i].Flag != 2):
                J[ind,self.Shellout.CTag[i].Xindex] = -1.0
        TubeComp = self.Tubein.CTag.keys()
        for ind,i in enumerate(TubeComp[:-1]):
            if (self.Tubein.CTag[i].Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubein.CTag[i].Xindex] = 1.0
            if (self.Tubeout.CTag[i].Flag != 2):
                J[len(shellcomp)+ind-1,self.Tubeout.CTag[i].Xindex]= -1.0      
        return J

    
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        # Shell side Energy balance Starts
        i=self.Shellin
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]= i.FTag.Est * i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est*i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est * i.GradDic[i.CTag[j]]

        i = self.Shellout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=-i.FTag.Est* i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=-i.FTag.Est* i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est* i.GradDic[i.CTag[j]]
        # Shell side energy Balance ends and Tube side energy balance starts
        i=self.Tubein
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=i.FTag.Est* i.GradDic[i.TTag]#dhdt
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=i.FTag.Est* i.GradDic[i.PTag]#dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=i.FTag.Est* i.GradDic[i.CTag[j]]#dhdt
        
        i=self.Tubeout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h    
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=-i.FTag.Est* i.GradDic[i.TTag]#dhdt
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=-i.FTag.Est* i.GradDic[i.PTag]#dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est* i.GradDic[i.CTag[j]]#dhdt
        
        if (self.Type == 1): #Counter-Current
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= 1
            if (self.Tubeout.TTag.Flag != 2):
                J[1,self.Tubeout.TTag.Xindex]= -1
                
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= 1
            if (self.Tubein.TTag.Flag != 2):
                J[2,self.Tubein.TTag.Xindex]= -1
        elif (self.Type == 2):  #Co-Current              
            if (self.Shellin.TTag.Flag != 2):
                J[1,self.Shellin.TTag.Xindex]= 1
            if (self.Tubein.TTag.Flag != 2):
                J[1,self.Tubein.TTag.Xindex]= -1
                 
            if (self.Shellout.TTag.Flag != 2):
                J[2,self.Shellout.TTag.Xindex]= 1
            if (self.Tubeout.TTag.Flag != 2):
                J[2,self.Tubeout.TTag.Xindex]= -1
        return J
    
    def PressureBalJaco(self,len1):
        J=zeros((2,len1))
        if (self.Shellin.PTag.Flag != 2):
            J[0,self.Shellin.PTag.Xindex] = 1.0
        if (self.Shellout.PTag.Flag != 2):
            J[0,self.Shellout.PTag.Xindex] = -1.0
        if (self.Tubein.PTag.Flag != 2):
            J[1,self.Tubein.PTag.Xindex] = 1.0
        if (self.Tubeout.PTag.Flag != 2):
            J[1,self.Tubeout.PTag.Xindex] = -1.0
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
            if (self.Shellin.CTag[i].Flag != 2):
                row.append(ind)
                col.append(self.Shellin.CTag[i].Xindex)
            if (self.Shellout.CTag[i].Flag != 2):
                row.append(ind)
                col.append(self.Shellout.CTag[i].Xindex)             
        TubeComp = self.Tubein.CTag.keys()
        NShellCompRes=len(shellcomp)-1
        for ind,i in enumerate(TubeComp[:-1]):
            if (self.Tubein.CTag[i].Flag != 2):
                row.append(NShellCompRes+ind)
                col.append(self.Tubein.CTag[i].Xindex)
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
        if (self.Shellin.TTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.TTag.Xindex)
        if (self.Shellin.PTag.Flag != 2):
            row.append(0)
            col.append(self.Shellin.PTag.Xindex)
        for i in self.Shellin.CTag.keys():
            if (self.Shellin.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Shellin.CTag[i].Xindex)

        
        if (self.Shellout.FTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.FTag.Xindex)
        if (self.Shellout.TTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.TTag.Xindex)
        if (self.Shellout.PTag.Flag != 2):
            row.append(0)
            col.append(self.Shellout.PTag.Xindex)
        for i in self.Shellout.CTag.keys():
            if (self.Shellout.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Shellout.CTag[i].Xindex)
        
        if (self.Tubein.FTag.Flag != 2):    
            row.append(0)
            col.append(self.Tubein.FTag.Xindex)
        if (self.Tubein.TTag.Flag != 2):
            row.append(0)
            col.append(self.Tubein.TTag.Xindex)
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
        if (self.Tubeout.PTag.Flag != 2):
            row.append(0)
            col.append(self.Tubeout.PTag.Xindex)
        for i in self.Tubeout.CTag.keys():
            if (self.Tubeout.CTag[i].Flag != 2):
                row.append(0)
                col.append(self.Tubeout.CTag[i].Xindex)

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
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        return List

    
    def EnergyBalHessNZP(self):
        List=[[]]*self.LenEneRes
        StreamList=[self.Shellin,self.Shellout,self.Tubein,self.Tubeout]
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
        shellcomp=self.Shellin.CTag.keys()
        Dic={}
        for ind1,i in enumerate(shellcomp[:-1]):
            List.append(Dic)
        Tubecomp=self.Tubein.CTag.keys()
        for ind2,i in enumerate(Tubecomp[:-1]):
            List.append(Dic)
        return List    
    
    def EnergyBalHess(self):
        List=[]
        Dic={}
        StreamIn=[]
        StreamOut=[]
        StreamIn.extend([self.Shellin,self.Tubein])
        StreamOut.extend([self.Shellout,self.Tubeout])
        for i in StreamIn:
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
            
        for i in StreamOut:
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
        if (self.Type ==1 or self.Type == 2):
            UB[1]=inf
            UB[2]=inf
        return LB,UB
    
    def PressureBalBound(self):
        LB=zeros((self.LenPreRes))
        UB=zeros((self.LenPreRes))
        return LB,UB
