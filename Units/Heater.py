'''
Created on 16-Aug-2014

@author: admin
'''
from Units.Seperator import Seperator
from Streams.FixedConcStream import FixedConcStream
from numpy import zeros
from numpy import asarray
class Heater():
    def __init__(self,Name,input,output,Q1,HeatCoolFlag=1,Dp=0):
        self.Name=Name
        if (HeatCoolFlag not in [1,-1]):
            print 'Error: Invalid HeatCoolFlag for a heater or cooler'
            exit()
        self.input=input
        self.output=output
        self.HCFlag=HeatCoolFlag
        self.Dp=Dp
        self.LenMatRes=1
        if (not (isinstance(self.input,FixedConcStream) and isinstance(self.output,FixedConcStream))):
            self.LenCompRes=len(self.input.CTag.keys())-1
        else:
            self.LenCompRes=0
        self.LenEneRes=1
        self.LenPreRes=1
        self.Resid=[]
        self.Qstrm=Q1
        #self.Qstrm.Q.Meas=abs(self.output.FTag.Est * self.output.Therm.EnthalpyStream(self.output) - self.input.FTag.Est * self.input.Therm.EnthalpyStream(self.input))
        #self.Qstrm.Q.Est=abs(self.output.FTag.Est*self.output.Therm.EnthalpyStream(self.output)-self.input.FTag.Est*self.input.Therm.EnthalpyStream(self.input))
        self.validation()
        
    def validation(self):
        if (set(self.input.CTag.keys()) !=set(self.output.CTag.keys())):
            print 'Error in heat Exchanger : ',self.Name
            print 'Fluid inlet and outlet have different set of components'
            exit()
    
    def MaterialBalRes(self):
        Resid=[]
        Resid.append(self.input.FTag.Est-self.output.FTag.Est)
        return Resid
    
    def ComponentBalRes(self):
        Resid=[]
        if (not (isinstance(self.input,FixedConcStream) and isinstance(self.output,FixedConcStream))):
            ShellComp=self.input.CTag.keys()
            for i in ShellComp[:-1]:
                Resid.append(self.input.CTag[i].Est-self.output.CTag[i].Est)
        return Resid
        
    def EnergyBalRes(self):
        Resid=[]
        QShell= self.input.FTag.Est*self.input.h + self.Qstrm.Q.Est*self.HCFlag - self.output.FTag.Est*self.output.h
        Resid.append(QShell)                   
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(self.input.PTag.Est - self.output.PTag.Est - self.Dp)
        return Resid

    def MaterialBalJaco(self,len1):
        J=zeros((self.LenMatRes,len1))
        if (self.input.FTag.Flag != 2):
            J[0,self.input.FTag.Xindex] = 1.0
        if (self.output.FTag.Flag != 2):
            J[0,self.output.FTag.Xindex] = -1.0
        return J
    
    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        if (not (isinstance(self.input,FixedConcStream) and isinstance(self.output,FixedConcStream))):
            inputcomp=self.input.CTag.keys()
            for ind,i in enumerate(inputcomp[:-1]):
                if (self.input.CTag[i].Flag != 2):
                    J[ind,self.input.CTag[i].Xindex] = 1.0
                if (self.output.CTag[i].Flag != 2):
                    J[ind,self.output.CTag[i].Xindex] = -1.0      
        return J
    
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        i=self.input
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex] = i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]= i.FTag.Est* i.GradDic[i.TTag]  
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est* i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est* i.GradDic[i.CTag[j]]
                
        i = self.output
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex] = -i.FTag.Est* i.GradDic[i.TTag]               
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex] = -i.FTag.Est* i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est* i.GradDic[i.CTag[j]]#dhdt
        
        J[0,self.Qstrm.Q.Xindex] = self.HCFlag
                
        return J

    def PressureBalJaco(self,len1):
        J=zeros((self.LenPreRes,len1))
        if (self.input.PTag.Flag != 2):
            J[0,self.input.PTag.Xindex] = 1.0
        if (self.output.PTag.Flag != 2):
            J[0,self.output.PTag.Xindex] = -1.0
        return J
    
    def MaterialBalJacoNZP(self):
        row=[]
        col=[]
        if (self.input.FTag.Flag != 2):
            row.append(0)
            col.append(self.input.FTag.Xindex)
        if (self.output.FTag.Flag != 2):
            row.append(0)
            col.append(self.output.FTag.Xindex)
        return row,col
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        if (not (isinstance(self.input,FixedConcStream) and isinstance(self.output,FixedConcStream))):
            inputcomp=self.input.CTag.keys()
            for ind,i in enumerate(inputcomp[:-1]):
                if (self.input.CTag[i].Flag != 2):
                    row.append(ind)
                    col.append(self.input.CTag[i].Xindex)
                if (self.output.CTag[i].Flag != 2):
                    row.append(ind)
                    col.append(self.output.CTag[i].Xindex)             
        return row,col
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
        In=self.input
        if (In.FTag.Flag != 2):
            row.append(0)
            col.append(In.FTag.Xindex)
        if (In.TTag.Flag != 2):
            row.append(0)
            col.append(In.TTag.Xindex)
        if (In.PTag.Flag != 2):
            row.append(0)
            col.append(In.PTag.Xindex)
        for i in In.CTag.keys():
            if (In.CTag[i].Flag != 2):
                row.append(0)
                col.append(In.CTag[i].Xindex)
        
        Out=self.output
        if (Out.FTag.Flag != 2):
            row.append(0)
            col.append(Out.FTag.Xindex)
        if (Out.TTag.Flag != 2):
            row.append(0)
            col.append(Out.TTag.Xindex)
        if (Out.PTag.Flag != 2):
            row.append(0)
            col.append(Out.PTag.Xindex)
        for i in Out.CTag.keys():
            if (Out.CTag[i].Flag != 2):
                row.append(0)
                col.append(Out.CTag[i].Xindex)
        
        row.append(0)
        col.append(self.Qstrm.Q.Xindex)
        return row,col
    
    def PressureBalJacoNZP(self):
        row=[]
        col=[]
        if (self.input.PTag.Flag != 2):
            row.append(0)
            col.append(self.input.PTag.Xindex)
        if (self.output.PTag.Flag != 2): 
            row.append(0)
            col.append(self.output.PTag.Xindex)
        return row,col
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        return List
    
    def EnergyBalHessNZP(self):
        List=[[]]*self.LenEneRes
        StreamList=[self.input,self.output]
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
        if (self.LenCompRes>0):
            ListComp=self.input.CTag.keys()
            Dic={}
            for ind1,i in enumerate(ListComp[:-1]):
                List.append(Dic)
        return List
    
    def EnergyBalHess(self):
        List=[]
        Dic={}
        i=self.input
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
        i=self.output
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