'''
Created on 17-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from Units.Heater import Heater
class HeaterVaporizer(Heater):
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
        self.LenCompRes=len(self.input.CTag.keys())-1
        self.CompList=self.input.CTag.keys()
        self.LenEneRes=2
        self.LenPreRes=1
        self.Resid=[]
        self.Qstrm=Q1
        #self.Qstrm.Q.Meas=abs(self.output.FTag.Est * self.output.Therm.EnthalpyStream(self.output) - self.input.FTag.Est * self.input.Therm.EnthalpyStream(self.input))
        #self.Qstrm.Q.Est=abs(self.output.FTag.Est*self.output.Therm.EnthalpyStream(self.output)-self.input.FTag.Est*self.input.Therm.EnthalpyStream(self.input))
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
        for i in self.input.CTag.keys():
            if (i not in self.output.CTag.keys()):
                print 'All components in the inlet stream are not present in output streams'
                exit()
        if (self.input.State !=1):
            print 'The inlet of the tube side of vaporizer ',self.Name, 'must be liquid'
            exit()
        elif (self.output.State !=2):
            print 'The outlet of the tube side of vaporizer ',self.Name, 'must be vapour'
            exit()
            
        
    def EnergyBalRes(self):
        Resid=[]
        QShell= self.input.FTag.Est*self.input.h + self.Qstrm.Q.Est*self.HCFlag - self.output.FTag.Est*self.output.h
        Resid.append(QShell)
        '''Forcing Temperature,Pressure of the outlet stream to be on Saturation line '''
        Psat=self.output.Therm.PsatStream(self.output)
        Resid.append(Psat-self.output.PTag.Est)                   
        return Resid
        
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        i=self.input
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex] = i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]= i.FTag.Est*i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est*i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est*i.GradDic[i.CTag[j]]
                
        i = self.output
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex] = -i.FTag.Est*i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex] = -i.FTag.Est*i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est*i.GradDic[i.CTag[j]]
        
        J[0,self.Qstrm.Q.Xindex] = self.HCFlag
        
        i=self.output
        PsatGradDic=i.PsatGradient()
        if (i.TTag.Flag!=2):            
            J[1,i.TTag.Xindex]=PsatGradDic[i.TTag]
        if (i.PTag.Flag != 2):
            J[1,i.PTag.Xindex]=PsatGradDic[i.PTag]-1
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[1,i.CTag[j].Xindex]=PsatGradDic[i.CTag[j]]
        return J
    
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
        
        i=self.output       
        if (i.TTag.Flag!=2):            
            row.append(1)
            col.append(i.TTag.Xindex)
        if (i.PTag.Flag != 2):
            row.append(1)
            col.append(i.PTag.Xindex)
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                row.append(1)
                col.append(i.CTag[j].Xindex)

        return row,col
    
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
        
        '''Psat line constraint'''
        i=self.output
        if (i.TTag.Flag !=2):
            List[1].append((i.TTag.Xindex,i.TTag.Xindex))
            if (i.TTag.Flag !=2 and i.PTag.Flag !=2):
                List[1].append((i.TTag.Xindex,i.PTag.Xindex))
                List[1].append((i.PTag.Xindex,i.TTag.Xindex))
            for j in i.CTag.keys():
                if (i.TTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[1].append((i.TTag.Xindex,i.CTag[j].Xindex))
                    List[1].append((i.CTag[j].Xindex,i.TTag.Xindex))
                
            if (i.PTag.Flag !=2):
                List[0].append((i.PTag.Xindex,i.PTag.Xindex))
            for j in i.CTag.keys():
                if (i.PTag.Flag !=2 and i.CTag[j].Flag !=2):
                    List[1].append((i.PTag.Xindex,i.CTag[j].Xindex))
                    List[1].append((i.CTag[j].Xindex,i.PTag.Xindex))
                
            for ind1,k in enumerate(i.CTag.keys()):
                for ind2,j in enumerate(i.CTag.keys()):
                    if (ind2>=ind1):
                        if (i.CTag[k].Flag !=2 and i.CTag[j].Flag !=2):
                            List[1].append((i.CTag[k].Xindex,i.CTag[j].Xindex))
                            if (ind1!=ind2):
                                List[1].append((i.CTag[j].Xindex,i.CTag[k].Xindex))
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
        '''Psat line constraint'''
        k=self.output
        PsatHess=k.PsatHessian()
        Dic={}
        if (k.TTag.Flag !=2):
            Dic[(k.TTag.Xindex,k.TTag.Xindex)]=PsatHess[(k.TTag,k.TTag)]
        if (k.TTag.Flag !=2 and k.PTag.Flag !=2):
            Dic[(k.TTag.Xindex,k.PTag.Xindex)]=PsatHess[(k.TTag,k.PTag)]
            Dic[(k.PTag.Xindex,k.TTag.Xindex)]=PsatHess[(k.TTag,k.PTag)]
        for j in i.CTag.keys():
            if (k.TTag.Flag !=2 and k.CTag[j].Flag !=2):
                Dic[(k.TTag.Xindex,k.CTag[j].Xindex)]=PsatHess[(k.TTag,k.CTag[j])]
                Dic[(k.CTag[j].Xindex,k.TTag.Xindex)]=PsatHess[(k.TTag,k.CTag[j])]
        
        if (k.PTag.Flag !=2):    
            Dic[(k.PTag.Xindex,k.PTag.Xindex)]=PsatHess[(k.PTag,k.PTag)]   
        for j in i.CTag.keys():
            if (k.PTag.Flag !=2 and k.CTag[j].Flag !=2):
                Dic[(k.PTag.Xindex,k.CTag[j].Xindex)]=PsatHess[(k.PTag,k.CTag[j])]
                Dic[(k.CTag[j].Xindex,k.PTag.Xindex)]=PsatHess[(k.PTag,k.CTag[j])]
        
        for ind1,m in enumerate(k.CTag.keys()):
            for ind2,j in enumerate(k.CTag.keys()):
                if (ind2>=ind1):
                    if (m==j):
                        if (k.CTag[j].Flag !=2):
                            Dic[(k.CTag[j].Xindex,k.CTag[j].Xindex)]=PsatHess[(k.CTag[j],k.CTag[j])]
                    else:
                        if (k.CTag[m].Flag !=2 and k.CTag[j].Flag !=2):
                            Dic[(k.CTag[m].Xindex,k.CTag[j].Xindex)]=PsatHess[(k.CTag[m],k.CTag[j])]
                            Dic[(k.CTag[j].Xindex,k.CTag[m].Xindex)]=PsatHess[(k.CTag[m],k.CTag[j])]
        List.append(Dic)
        return List



