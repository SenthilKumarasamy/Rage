'''
Created on 16-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from Units.Reactor import Reactor
class ElementBalanceReactor(Reactor):
    def __init__(self,Name,Rstrm,Pstrm,Qstrm,ExoEndoFlag=1,dp=0):
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
            print 'Heat streams are not unique'
            exit()
#====================================Validation ends=================================        
        self.Rstrm=Rstrm
        self.Pstrm=Pstrm
        self.Qstrm=Qstrm
        self.Dp=dp
            
        self.ListComp=[]
        for i in self.Pstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        for i in self.Rstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        ''' Validation for Elements of the reactants and products'''                
        RstrmElement=[]
        for i in self.Rstrm.CTag.keys():
            for j in i.MF.keys():
                if (j not in RstrmElement):
                    RstrmElement.append(j)
        PstrmElement=[]
        for i in self.Pstrm.CTag.keys():
            for j in i.MF.keys():
                if (j not in PstrmElement):
                    PstrmElement.append(j)
        for i in RstrmElement:
            if (i not in PstrmElement):
                print 'Some Elements of Reactants are not present in the Products'
                print self.Name
                exit()
        self.ListElement=RstrmElement
        self.EFlag=ExoEndoFlag
        self.LenMatRes=0
        self.LenCompRes=len(self.ListElement)
        self.LenEneRes=1
        self.LenPreRes=1
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
        for i in self.ListElement:
            inlet=0.0
            outlet=0.0
            for j in self.ListComp:
                if (i in j.MF.keys()):
                    if (j in self.Rstrm.CTag.keys()):
                        inlet=inlet + self.Rstrm.CTag[j].Est * self.Rstrm.FTag.Est * j.MF[i]
                    if (j in self.Pstrm.CTag.keys()):
                        outlet=outlet+self.Pstrm.FTag.Est * self.Pstrm.CTag[j].Est * j.MF[i]
            Resid.append(inlet-outlet)
        return Resid
    
    def ComponentBalJaco(self,len1):
        J = zeros((self.LenCompRes,len1))
        for ind,i in enumerate(self.ListElement):
            sumR=0.0
            sumP=0.0
            for j in self.ListComp:
                if (i in j.MF.keys()):
                    if (j in self.Pstrm.CTag.keys()):
                        sumP=sumP+self.Pstrm.CTag[j].Est*j.MF[i]
                    if (j in self.Rstrm.CTag.keys()):
                        sumR=sumR+self.Rstrm.CTag[j].Est*j.MF[i]
            if (self.Rstrm.FTag.Flag !=2):
                J[ind,self.Rstrm.FTag.Xindex]=sumR
            if (self.Pstrm.FTag.Flag !=2):
                J[ind,self.Pstrm.FTag.Xindex]=-sumP
                
            for j in self.Rstrm.CTag.keys():
                if (i in j.MF.keys()):
                    if (self.Rstrm.CTag[j].Flag != 2):
                        J[ind,self.Rstrm.CTag[j].Xindex]= self.Rstrm.FTag.Est * j.MF[i]
            
            for j in self.Pstrm.CTag.keys():
                if (i in j.MF.keys()):
                    if (self.Pstrm.CTag[j].Flag != 2):
                        J[ind,self.Pstrm.CTag[j].Xindex]= -self.Pstrm.FTag.Est * j.MF[i]
        return J
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        for ind,i in enumerate(self.ListElement):
            if (self.Rstrm.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Rstrm.FTag.Xindex)
            
            if (self.Pstrm.FTag.Flag != 2):
                row.append(ind)
                col.append(self.Pstrm.FTag.Xindex)
            
            for j in self.Rstrm.CTag.keys():
                if (i in j.MF.keys()):
                    if (self.Rstrm.CTag[j].Flag != 2):
                        row.append(ind)
                        col.append(self.Rstrm.CTag[j].Xindex)
            
            for j in self.Pstrm.CTag.keys():
                if (i in j.MF.keys()):
                    if (self.Pstrm.CTag[j].Flag != 2):
                        row.append(ind)
                        col.append(self.Pstrm.CTag[j].Xindex)
        return row,col
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        for ind,i in enumerate(self.ListElement):
            List[ind]=[]
            for j in self.ListComp:
                if (i in j.MF.keys()):
                    if (j in self.Rstrm.CTag.keys()):
                        if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[j].Flag !=2):
                            List[ind].append((self.Rstrm.FTag.Xindex,self.Rstrm.CTag[j].Xindex))
                            List[ind].append((self.Rstrm.CTag[j].Xindex,self.Rstrm.FTag.Xindex))
                    if (j in self.Pstrm.CTag.keys()):
                        if (self.Pstrm.FTag.Flag != 2 and self.Pstrm.CTag[j].Flag !=2):
                            List[ind].append((self.Pstrm.FTag.Xindex,self.Pstrm.CTag[j].Xindex))
                            List[ind].append((self.Pstrm.CTag[j].Xindex,self.Pstrm.FTag.Xindex))
        return List
    
    def ComponentBalHess(self):
        List=[]
        for i in self.ListElement:
            Dic={}
            for j in self.ListComp:
                if (i in j.MF.keys()):
                    if (j in self.Rstrm.CTag.keys()):
                        if (self.Rstrm.FTag.Flag !=2 and self.Rstrm.CTag[j].Flag !=2):
                            Dic[(self.Rstrm.FTag.Xindex,self.Rstrm.CTag[j].Xindex)]=j.MF[i]/j.MolWt
                            Dic[(self.Rstrm.CTag[j].Xindex,self.Rstrm.FTag.Xindex)]=j.MF[i]/j.MolWt
                    if (j in self.Pstrm.CTag.keys()):
                        if (self.Pstrm.FTag.Flag != 2 and self.Pstrm.CTag[j].Flag !=2):
                            Dic[(self.Pstrm.FTag.Xindex,self.Pstrm.CTag[j].Xindex)]=-j.MF[i]/j.MolWt
                            Dic[(self.Pstrm.CTag[j].Xindex,self.Pstrm.FTag.Xindex)]=-j.MF[i]/j.MolWt
            List.append(Dic)
        return List