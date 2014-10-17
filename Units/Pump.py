'''
Created on 15-Oct-2014

@author: Sam
'''
from numpy import zeros
from numpy import asarray
from numpy.linalg import pinv
from numpy import dot
class Pump:
    def __init__(self,Name,Inlet,Outlet,Qstrm,dp=0):
#===================Validation Starts======================================
        self.Name=Name    
        
#====================================Validation ends=================================        
        self.Inlet=Inlet
        self.Outlet=Outlet
        self.Qstrm=Qstrm
        self.Dp=dp        
            
        self.ListComp=[]
        for i in self.Inlet.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        for i in self.Outlet.CTag.keys():
            if (i not in self.ListComp):
                print 'Inlet and outlet streams not matching'
                quit()
                self.ListComp.append(i)
        self.LenMatRes=1
        self.LenCompRes=len(Inlet.CTag.keys())-1
        self.LenEneRes=1
        self.LenPreRes=1
    
                
                
    
    def MaterialBalRes(self):
        Resid=[]
        sum1=self.Inlet.FTag.Est - self.Outlet.FTag.Est        
        Resid.append(sum1)
        return (Resid) # Overall Mass balance
        
    def ComponentBalRes(self):
        Resid=[]
        key=self.Inlet.CTag.keys()
        for i in key[:-1]:  # N-1 Component Balances
            Resid.append(self.Inlet.FTag.Est*self.Inlet.CTag[i].Est - self.Outlet.FTag.Est*self.Outlet.CTag[i].Est) # N-1 Component Balances
        return (Resid) # N-1 Component Balances     
    
    def EnergyBalRes(self):
        Resid=[]
        Resid.append(self.Inlet.h * self.Inlet.FTag.Est +  self.Qstrm.Q.Est - self.Outlet.h * self.Outlet.FTag.Est)
        return (Resid)
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(self.Inlet.PTag.Est - self.Outlet.PTag.Est - self.Dp)
        return (Resid)
    

    def MaterialBalJaco(self,len1):
        J=zeros((1,len1))        
        if (self.Inlet.FTag.Flag != 2):
            J[0,self.Inlet.FTag.Xindex] = 1.0
        if (self.Outlet.FTag.Flag != 2):
            J[0,self.Outlet.FTag.Xindex]=-1.0
        return J
    

    def ComponentBalJaco(self,len1):
        J=zeros((len(self.Inlet.CTag.keys())-1,len1))
        key=self.Inlet.CTag.keys()
        for ind,i in enumerate(key[:-1]):               
            if (self.Inlet.FTag.Flag!=2):
                J[ind,self.Inlet.FTag.Xindex] = self.Inlet.CTag[i].Est
            if (self.Inlet.CTag[i].Flag!=2):
                J[ind,self.Inlet.CTag[i].Xindex] = self.Inlet.FTag.Est
                
#             if (i in self.Outlet.CTag.keys()): # Indent the below 4 lines if this line is uncommented (taken from separator)
            if (self.Outlet.FTag.Flag!=2):
                J[ind,self.Outlet.FTag.Xindex] = -self.Outlet.CTag[i].Est
            if (self.Outlet.CTag[i].Flag!=2):
                J[ind,self.Outlet.CTag[i].Xindex] = -self.Outlet.FTag.Est

        return J
    
    def EnergyBalJaco(self,len1):
        J = zeros((self.LenEneRes,len1))
        i=self.Qstrm
        if (i.Q.Flag !=2):
            J[0,i.Q.Xindex] = 1 #self.EFlag, Since energy is always given into the system by pump.
        
        i=self.Inlet
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= i.h
             
        if (i.TTag.Flag!=2):            
            J[0,i.TTag.Xindex] = i.FTag.Est * i.GradDic[i.TTag]#dhdt           
            
        if (i.PTag.Flag!=2):
            J[0,i.PTag.Xindex]= i.FTag.Est * i.GradDic[i.PTag]#dhdt
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                J[0,i.CTag[j].Xindex]= i.FTag.Est * i.GradDic[i.CTag[j]]#dhdt
  
        i=self.Outlet
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
        if (self.Inlet.PTag.Flag != 2):
            J[0,self.Inlet.PTag.Xindex] = 1.0
        if (self.Outlet.PTag.Flag != 2):
            J[0,self.Outlet.PTag.Xindex] = -1.0
        return J
    
    def MaterialBalJacoNZP(self):
        row=[]
        col=[]
        if (self.Inlet.FTag.Flag!=2):
            row.append(0)
            col.append(self.Inlet.FTag.Xindex)
        #for i in self.output:    # Indent the below 3 lines if this line is uncommented (taken from separator)
        if (self.Outlet.FTag.Flag!=2):
            row.append(0)
            col.append(self.Outlet.FTag.Xindex)        
        return row,col
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        key=self.Inlet.CTag.keys()
        for ind,i in enumerate(key[:-1]):
            if (self.Inlet.FTag.Flag!=2):
                row.append(ind)
                col.append(self.Inlet.FTag.Xindex)
            if (self.Inlet.CTag[i].Flag!=2):
                row.append(ind)
                col.append(self.Inlet.CTag[i].Xindex)
                            
#            for j in self.output:# Indent the below block if this line is uncommented (taken from separator)
            if (self.Outlet in self.Outlet.CTag.keys()):
                if (self.Outlet.FTag.Flag!=2):                  
                    row.append(ind)
                    col.append(self.Outlet.FTag.Xindex)
                if (j.CTag[i].Flag!=2):
                    row.append(ind)
                    col.append(self.Outlet.CTag[i].Xindex)
        return row,col
        
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
         
        if (self.Qstrm.Q.Flag !=2):
            row.append(0)
            col.append(self.Qstrm.Q.Xindex)
                   
        i=self.Inlet
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

        i=self.Outlet
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
        if (self.Inlet.PTag.Flag != 2):
            row.append(0)
            col.append(self.Inlet.PTag.Xindex)
        if (self.Outlet.PTag.Flag != 2):
            row.append(0)
            col.append(self.Outlet.PTag.Xindex)
        return row,col
    
    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        for ind1,i in enumerate(self.ListComp[:-1]):
            if (i in self.Inlet.CTag.keys()):
                if (self.Inlet.FTag.Flag !=2 and self.Inlet.CTag[i].Flag !=2):
                    List[ind1].append((self.Inlet.FTag.Xindex,self.Inlet.CTag[i].Xindex))
                    List[ind1].append((self.Inlet.CTag[i].Xindex,self.Inlet.FTag.Xindex))
            if (i in self.Outlet.CTag.keys()):
                if (self.Outlet.FTag.Flag !=2 and self.Outlet.CTag[i].Flag !=2):
                    List[ind1].append((self.Outlet.FTag.Xindex,self.Outlet.CTag[i].Xindex))
                    List[ind1].append((self.Outlet.CTag[i].Xindex,self.Outlet.FTag.Xindex))
        return List
    
    def EnergyBalHessNZP(self):
        List=[[]]*self.LenEneRes
        StreamList=[self.Inlet,self.Outlet]
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
        for ind1,i in enumerate(self.ListComp[:-1]):
            Dic={}
            if (i in self.Inlet.CTag.keys()):
                if (self.Inlet.FTag.Flag !=2 and self.Inlet.CTag[i].Flag !=2):
                    Dic[(self.Inlet.FTag.Xindex,self.Inlet.CTag[i].Xindex)]=1.0
                    Dic[(self.Inlet.CTag[i].Xindex,self.Inlet.FTag.Xindex)]=1.0
            if (i in self.Outlet.CTag.keys()):
                if (self.Outlet.FTag.Flag !=2 and self.Outlet.CTag[i].Flag !=2):
                    Dic[(self.Outlet.FTag.Xindex,self.Outlet.CTag[i].Xindex)]=-1.0
                    Dic[(self.Outlet.CTag[i].Xindex,self.Outlet.FTag.Xindex)]=-1.0
            List.append(Dic)
        return List
    
    def EnergyBalHess(self):
        List=[]
        Dic={}
        i=self.Inlet
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
        i=self.Outlet
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
