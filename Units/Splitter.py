'''
Created on 15-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from Units.Seperator import Seperator
from Streams.FixedConcStream import FixedConcStream 
class Splitter(Seperator):
    def __init__(self,Name,input,output,dp=[]):
        self.Name=Name
        self.input=[]
        self.output=[]
        for i in output:
            self.output.append(i)
        self.input.append(input)
        self.LenMatRes=1
        self.FixedConcStreamFlag=1
        for i in self.output:
            self.FixedConcStreamFlag=self.FixedConcStreamFlag*isinstance(i,FixedConcStream)
        self.FixedConcStreamFlag=self.FixedConcStreamFlag*isinstance(self.input[0],FixedConcStream)
        print isinstance(self.input[0],FixedConcStream)
        if (self.FixedConcStreamFlag==0):
            self.LenCompRes=(len(self.input[0].CTag.keys())-1)*len(self.output)
        else:
            self.LenCompRes=0
        print self.LenCompRes
        self.LenEneRes=len(self.output)
        self.LenPreRes=len(self.output)
        #self.dp=zeros((self.LenPreRes))
        if (len(dp)==0):
            self.dp=zeros((len(self.output)))
        elif (len(dp)==len(self.output)):
            self.dp=dp
        self.validation()
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

    def validation(self):
        for i in self.input[0].CTag.keys():
            for j in self.output:
                if (i not in j.CTag.keys()):
                    print 'All components in the inlet stream are not present in output streams'
                    exit()
        
    def ComponentBalRes(self):
        Resid=[]
        if (self.FixedConcStreamFlag==0):
            for j in self.output:
                key=self.input[0].CTag.keys()
                for i in key[:-1]:
                    Resid.append(j.CTag[i].Est-self.input[0].CTag[i].Est)
        return Resid
                
    def EnergyBalRes(self):
        Resid=[]
        for i in self.output:
            Resid.append(i.TTag.Est-self.input[0].TTag.Est)
        return (Resid)
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        if (self.FixedConcStreamFlag==0):
            inputcomp=self.input[0].CTag.keys()
            N=len(inputcomp)-1
            for jind,j in enumerate(self.output):
                for ind,i in enumerate(inputcomp[:-1]):
                    if (j.CTag[i].Flag!=2):
                        row.append(jind*N+ind)
                        col.append(j.CTag[i].Xindex)
                    if (self.input[0].CTag[i].Flag!=2):
                        row.append(jind*N+ind)
                        col.append(self.input[0].CTag[i].Xindex)
        return row,col

    def EnergyBalJacoNZP(self):
        row=[]
        col=[]                    
        for ind,i in enumerate(self.output):
            if (i.TTag.Flag!=2):
                row.append(ind)
                col.append(i.TTag.Xindex)
            if (self.input[0].TTag.Flag!=2):
                row.append(ind)
                col.append(self.input[0].TTag.Xindex)
        return row,col 
    
    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        if (self.FixedConcStreamFlag==0):
            inputcomp=self.input[0].CTag.keys()
            N=len(inputcomp[:-1])
            for jind,j in enumerate(self.output):
                for ind,i in enumerate(inputcomp[:-1]):
                    if (j.CTag[i].Flag!=2):
                        J[jind*N+ind,j.CTag[i].Xindex]=1
                    if (self.input[0].CTag[i].Flag!=2):
                        J[jind*N+ind,self.input[0].CTag[i].Xindex]=-1
        return J
     
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        for ind,i in enumerate(self.output):
            if (i.TTag.Flag!=2):
                J[ind,i.TTag.Xindex] = 1.0
            if (self.input[0].TTag.Flag!=2):
                J[ind,self.input[0].TTag.Xindex] = -1.0       
        return J
    
#     def MaterialBalHessNZP(self):
#         return [[]]*self.LenMatRes
#       
#     def PressureBalHessNZP(self):
#         return [[]]*self.LenPreRes
    
    def ComponentBalHessNZP(self):
        return [[]]*self.LenCompRes
    
    def EnergyBalHessNZP(self):
        return [[]]*self.LenEneRes
    
    def ComponentBalHess(self):
        return[{}]*self.LenCompRes
        
    def EnergyBalHess(self):
        return [{}]*self.LenEneRes

