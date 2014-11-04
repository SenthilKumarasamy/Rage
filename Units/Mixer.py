'''
Created on 15-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from Units.Seperator import Seperator
class Mixer(Seperator):
    def __init__(self,Name,input,output):
        self.Name=Name
        self.input=[]
        self.output=[]
        for i in input:
            self.output.append(i)
        self.input.append(output)
        self.LenMatRes=1
        self.LenCompRes=len(output.CTag.keys())-1
        self.LenEneRes=1
        self.LenPreRes=1
        self.validation()
#         self.MB_SF=abs(asarray(self.MaterialBalRes()))
#         self.CB_SF=abs(asarray(self.ComponentBalRes()))
#         self.EB_SF=abs(asarray(self.EnergyBalRes()))
#         self.PB_SF=abs(asarray(self.PressureBalRes()))
#         self.CheckForZero()
#     
#     def CheckForZero(self):
#         Min_SF=1
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
    
    def validation(self):
        C=[]
        for i in self.output:
            for j in i.CTag.keys():
                if (j not in C):
                    C.append(j)
        if (len(C)==len(self.input[0].CTag.keys())):
            for i in self.input[0].CTag.keys():
                if (i not in C):
                    print 'The outlet streams do not contain some of the components present in the inlet stream'
                    exit()
        else:
            print 'The number of Components in the inlet and outlet streams are not matching in the Mixer ',self.Name
            exit()
    
    def PressureBalRes(self):
        Resid = []
        sumP = 0
        N = len(self.output)
        for i in self.output:
            sumP = sumP + i.PTag.Est
        Resid.append(sumP/N - self.input[0].PTag.Est)
        return Resid
    
    def PressureBalJacoNZP(self):
        row = []
        col = []
        for i in self.output:
            if (i.PTag.Flag != 2):
                row.append(0)
                col.append(i.PTag.Xindex)
        if (self.input[0].PTag.Flag != 2):
            row.append(0)
            col.append(self.input[0].PTag.Xindex)
        return row,col
        
    def PressureBalJaco(self,len1):
        J = zeros((self.LenPreRes,len1))
        N = len(self.output)
        for i in self.output:
            if (i.PTag.Flag != 2):
                J[0,i.PTag.Xindex] = 1.00/N
        if (self.input[0].PTag.Flag != 2):
            J[0,self.input[0].PTag.Xindex] = -1.0
        return J
 