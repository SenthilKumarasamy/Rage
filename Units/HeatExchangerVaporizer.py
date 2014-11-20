'''
Created on 16-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import ones
from numpy import inf
from numpy import asarray
from Units.HeatExchanger import HeatExchanger
class HeatExchangerVaporizer(HeatExchanger):
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
            self.LenEneRes = 4
        else:
            self.LenEneRes = 2
        self.Validation()
        self.U=self.UEst()
        self.LenPreRes = 2
        if (self.Tubein.State !=1):
            print 'The inlet of the tube side of vaporizer ',self.Name, 'must be liquid'
            exit()
        elif (self.Tubeout.State !=2):
            print 'The outlet of the tube side of vaporizer ',self.Name, 'must be vapour'
            exit()    

        
    def EnergyBalRes(self):
        Resid=[]
        QShell = self.Shellin.FTag.Est*self.Shellin.h-self.Shellout.FTag.Est*self.Shellout.h
        QTube = self.Tubein.FTag.Est*self.Tubein.h-self.Tubeout.FTag.Est*self.Tubeout.h
        Resid.append(QShell+QTube)
        '''Forcing Temperature,Pressure of the Tube side outlet to be on Saturation line '''
        Psat=self.Tubeout.Therm.PsatStream(self.Tubeout)
        Resid.append(Psat-self.Tubeout.PTag.Est)
        if (self.Type == 1): #counter-current
            Resid.append(self.Shellin.TTag.Est - self.Tubeout.TTag.Est)
            Resid.append(self.Shellout.TTag.Est - self.Tubein.TTag.Est)
        elif (self.Type ==2 ): #co-current
            Resid.append(self.Shellin.TTag.Est - self.Tubein.TTag.Est)
            Resid.append(self.Shellout.TTag.Est - self.Tubeout.TTag.Est)                    
        return Resid
    
    def EnergyBalBound(self):
        LB=zeros((self.LenEneRes))
        UB=zeros((self.LenEneRes))
        if (self.Type ==1 or self.Type == 2):
            UB[2]=inf
            UB[3]=inf
        return LB,UB
    
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        # Shell side Energy balance Starts
        i=self.Shellin
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]= i.FTag.Est * i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est *i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est * i.GradDic[i.CTag[j]]

        i = self.Shellout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=-i.FTag.Est* i.GradDic[i.TTag]                
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=-i.FTag.Est* i.GradDic[i.PTag]#dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est*i.GradDic[i.CTag[j]]#dhdt
        # Shell side energy Balance ends and Tube side energy balance starts
        i=self.Tubein
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=i.h
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=i.FTag.Est* i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=i.FTag.Est* i.GradDic[i.PTag]
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=i.FTag.Est* i.GradDic[i.CTag[j]]
        
        i=self.Tubeout
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h    
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex]=-i.FTag.Est* i.GradDic[i.TTag]
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]=-i.FTag.Est* i.GradDic[i.PTag]#dhdt
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]=-i.FTag.Est* i.GradDic[i.CTag[j]]#dhdt
        
        '''Saturation line'''
        PsatGradDic=i.PsatGradient()
        if (i.TTag.Flag!=2):            
            J[1,i.TTag.Xindex]=PsatGradDic[i.TTag]
        if (i.PTag.Flag != 2):
            J[1,i.PTag.Xindex]=-1
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[1,i.CTag[j].Xindex]=PsatGradDic[i.CTag[j]]

        
        if (self.Type == 1): #Counter-Current
            if (self.Shellin.TTag.Flag != 2):
                J[2,self.Shellin.TTag.Xindex]= 1
            if (self.Tubeout.TTag.Flag != 2):
                J[2,self.Tubeout.TTag.Xindex]= -1
                
            if (self.Shellout.TTag.Flag != 2):
                J[3,self.Shellout.TTag.Xindex]= 1
            if (self.Tubein.TTag.Flag != 2):
                J[3,self.Tubein.TTag.Xindex]= -1
        elif (self.Type == 2):  #Co-Current              
            if (self.Shellin.TTag.Flag != 2):
                J[2,self.Shellin.TTag.Xindex]= 1
            if (self.Tubein.TTag.Flag != 2):
                J[2,self.Tubein.TTag.Xindex]= -1
                 
            if (self.Shellout.TTag.Flag != 2):
                J[3,self.Shellout.TTag.Xindex]= 1
            if (self.Tubeout.TTag.Flag != 2):
                J[3,self.Tubeout.TTag.Xindex]= -1
        return J
    
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
        
        i=self.Tubeout        
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


        if (self.Type==1): #Counter Current          
            if (self.Shellin.TTag.Flag != 2):
                row.append(2)
                col.append(self.Shellin.TTag.Xindex)
            if (self.Tubeout.TTag.Flag != 2):
                row.append(2)
                col.append(self.Tubeout.TTag.Xindex)
            if (self.Shellout.TTag.Flag != 2):
                row.append(3)
                col.append(self.Shellout.TTag.Xindex)
            if (self.Tubein.TTag.Flag != 2):
                row.append(3)
                col.append(self.Tubein.TTag.Xindex)
        elif (self.Type == 2): #Co-Current
            if (self.Shellin.TTag.Flag != 2):
                row.append(2)
                col.append(self.Shellin.TTag.Xindex)
            if (self.Tubein.TTag.Flag != 2):
                row.append(2)
                col.append(self.Tubein.TTag.Xindex)
            if (self.Shellout.TTag.Flag != 2):
                row.append(3)
                col.append(self.Shellout.TTag.Xindex)
            if (self.Tubeout.TTag.Flag != 2):
                row.append(3)
                col.append(self.Tubeout.TTag.Xindex)           
        return row,col
    
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
        
        '''Psat line constraint'''
        i=self.Tubeout
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
        
        '''Psat line constraint'''
        k=self.Tubeout
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
