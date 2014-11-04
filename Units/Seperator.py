'''
Created on 15-Aug-2014

@author: admin
'''
from numpy import zeros
from numpy import asarray
from CommonFunctions.DerivativeEnthalpyStream import DerivativeEnthalpyStream
class Seperator:
    def __init__(self,Name,input,output,dp=[]):
        self.Name=Name
        self.input=[]
        self.output=[]
        for i in output:
            self.output.append(i)
        self.input.append(input)
        self.LenMatRes=1
        self.LenCompRes=len(input.CTag.keys())-1
        self.LenEneRes=1
        self.LenPreRes=len(self.output)
        if (len(dp)==0):
            self.dp=zeros((len(self.output)))
        elif (len(dp)==len(self.output)):
            self.dp=dp
        self.validation()
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
            print 'The number of Components in the inlet and outlet streams are not matching in the seperator ',self.Name
            exit()
        if (len(self.dp)!=len(self.output)):
            print 'Length of delta pressure and number of output streams not matching'
            exit()
    
    '''Constraints Computaion starts here'''
    def MaterialBalRes(self):
        Resid=[]
        sum1=0
        for i in self.output:
            sum1=sum1+i.FTag.Est
        Resid.append(sum1-self.input[0].FTag.Est)
        return (Resid) # Overall Mass balance
    
    def ComponentBalRes(self):
        Resid=[]
        key=self.input[0].CTag.keys()
        for i in key[:-1]:
            sum1=0
            for j in self.output:
                if (i in j.CTag.keys()):                        
                    sum1=sum1+j.FTag.Est * j.CTag[i].Est           
            Resid.append(sum1-self.input[0].FTag.Est*self.input[0].CTag[i].Est) # N-1 Component Balances
        return (Resid) # N-1 Component Balances 
                   
    def EnergyBalRes(self):
        Resid=[]
        EnergyBal=0;
        for i in range(len(self.output)):
            EnergyBal=EnergyBal+self.output[i].FTag.Est*self.output[i].h  
        EnergyBal=EnergyBal-self.input[0].FTag.Est*self.input[0].h
        Resid.append(EnergyBal)
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        for ind,i in enumerate(self.output):
            Resid.append(self.input[0].PTag.Est - i.PTag.Est - self.dp[ind])
        return Resid
    
    '''Jacobian Computation starts here'''
    def MaterialBalJacoNZP(self):
        row=[]
        col=[]
        for i in self.output:
            if (i.FTag.Flag!=2):
                row.append(0)
                col.append(i.FTag.Xindex)
        if (self.input[0].FTag.Flag!=2):
            row.append(0)
            col.append(self.input[0].FTag.Xindex)
        return row,col
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
        key=self.input[0].CTag.keys()
        for ind,i in enumerate(key[:-1]):
            for j in self.output:
                if (i in j.CTag.keys()):
                    if (j.FTag.Flag!=2):                  
                        row.append(ind)
                        col.append(j.FTag.Xindex)
                    if (j.CTag[i].Flag!=2):
                        row.append(ind)
                        col.append(j.CTag[i].Xindex)
            if (self.input[0].FTag.Flag!=2):
                row.append(ind)
                col.append(self.input[0].FTag.Xindex)
            if (self.input[0].CTag[i].Flag!=2):
                row.append(ind)
                col.append(self.input[0].CTag[i].Xindex)
        return row,col
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
        sumFH=0.0
        for i in self.output:
            if (i.FTag.Flag!=2):
                row.append(0)
                col.append(i.FTag.Xindex)
            if (i.TTag.Flag!=2):
                row.append(0)
                col.append(i.TTag.Xindex)
            if (i.PTag.Flag!=2):
                row.append(0)
                col.append(i.PTag.Xindex)
            for ind in i.CTag.keys():
                if (i.CTag[ind].Flag!=2):
                    row.append(0)
                    col.append(i.CTag[ind].Xindex)
        
        if (self.input[0].FTag.Flag!=2):
            row.append(0)
            col.append(self.input[0].FTag.Xindex)
        if (self.input[0].TTag.Flag!=2):
            row.append(0)
            col.append(self.input[0].TTag.Xindex)
        if (self.input[0].PTag.Flag!=2):
            row.append(0)
            col.append(self.input[0].PTag.Xindex)
        
        for i in self.input[0].CTag.keys():
            if (self.input[0].CTag[i].Flag!=2):
                row.append(0)
                col.append(self.input[0].CTag[i].Xindex)
        return row,col
    
    def PressureBalJacoNZP(self):
        row=[]
        col=[]
        for ind,i in enumerate(self.output):
            if (i.PTag.Flag!=2):
                row.append(ind)
                col.append(i.PTag.Xindex)
            if (self.input[0].PTag.Flag!=2):
                row.append(ind)
                col.append(self.input[0].PTag.Xindex)
        return row,col
      
    
    def MaterialBalJaco(self,len1):
        J=zeros((1,len1))
        for i in self.output:
            if (i.FTag.Flag!=2):
                J[0,i.FTag.Xindex] = 1.0
        if (self.input[0].FTag.Flag!=2):
            J[0,self.input[0].FTag.Xindex]=-1.0
        return J

    def ComponentBalJaco(self,len1):
        J=zeros((len(self.input[0].CTag.keys())-1,len1))
        key=self.input[0].CTag.keys()
        for ind,i in enumerate(key[:-1]):
            for j in self.output:
                if (i in j.CTag.keys()):
                    if (j.FTag.Flag!=2):
                        J[ind,j.FTag.Xindex] = j.CTag[i].Est
                    if (j.CTag[i].Flag!=2):
                        J[ind,j.CTag[i].Xindex] = j.FTag.Est
               
            if (self.input[0].FTag.Flag!=2):
                J[ind,self.input[0].FTag.Xindex] = -self.input[0].CTag[i].Est
            if (self.input[0].CTag[i].Flag!=2):
                J[ind,self.input[0].CTag[i].Xindex] = -self.input[0].FTag.Est
        return J

                    
    def EnergyBalJaco(self,len1):
        J=zeros((1,len1))
        for i in self.output:
            if (i.FTag.Flag!=2):
                J[0,i.FTag.Xindex]=i.h
             
            if (i.TTag.Flag!=2):            
                J[0,i.TTag.Xindex]=i.FTag.Est*i.GradDic[i.TTag]            
 
            if (i.PTag.Flag!=2):
                J[0,i.PTag.Xindex]=i.FTag.Est*i.GradDic[i.PTag]
  
            for j in i.CTag.keys():
                if (i.CTag[j].Flag!=2):
                    J[0,i.CTag[j].Xindex]=i.FTag.Est*i.GradDic[i.CTag[j]]
         
        k=self.input[0]
        if (k.FTag.Flag!=2):
            J[0,k.FTag.Xindex]=-k.h
         
        if (k.TTag.Flag!=2):
            J[0,k.TTag.Xindex]=-k.FTag.Est * k.GradDic[k.TTag]
         
        if (k.PTag.Flag!=2):
            J[0,k.PTag.Xindex] = -k.FTag.Est * k.GradDic[k.PTag]
         
        for i in k.CTag.keys():
            if (k.CTag[i].Flag!=2):
                J[0,k.CTag[i].Xindex]=-k.FTag.Est * k.GradDic[k.CTag[i]]      
        return J
    
    def PressureBalJaco(self,len1):
        J=zeros((len(self.output),len1))
        for ind,i in enumerate(self.output):
            if (i.PTag.Flag!=2):
                J[ind,i.PTag.Xindex]=-1.0
            if (self.input[0].PTag.Flag!=2):
                J[ind,self.input[0].PTag.Xindex]=1.0
        return J 
        
    '''Hessian Computation starts here'''    
#     def MaterialBalHessNZP(self):
#         return [[]]*self.LenMatRes
#       
#     def PressureBalHessNZP(self):
#         return [[]]*self.LenPreRes

    def ComponentBalHessNZP(self):
        List=[[]]*self.LenCompRes
        for ind,j in enumerate(self.input[0].CTag.keys()[:-1]):
            for i in self.output:
                if (j in i.CTag.keys()):
                    if (i.FTag.Flag !=2 and i.CTag[j].Flag !=2):
                        List[ind].append((i.FTag.Xindex,i.CTag[j].Xindex))
                        List[ind].append((i.CTag[j].Xindex,i.FTag.Xindex))
            if (self.input[0].FTag.Flag !=2 and self.input[0].CTag[j].Flag !=2):
                List[ind].append((self.input[0].FTag.Xindex,self.input[0].CTag[j].Xindex))
                List[ind].append((self.input[0].CTag[j].Xindex,self.input[0].FTag.Xindex))    
        return List
    
    def EnergyBalHessNZP(self):
        List=[[]]*self.LenEneRes
        StreamList=[]
        StreamList.extend(self.output)
        StreamList.extend(self.input)
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
        List=[]#*self.LenCompRes
        for j in (self.input[0].CTag.keys()[:-1]):
            Dic={}
            for i in self.output:
                if (j in i.CTag.keys()):
                    if (i.FTag.Flag !=2 and i.CTag[j].Flag !=2):
                        Dic[(i.FTag.Xindex,i.CTag[j].Xindex)]=1.0
                        Dic[(i.CTag[j].Xindex,i.FTag.Xindex)]=1.0
            if (self.input[0].FTag.Flag !=2 and self.input[0].CTag[j].Flag !=2):
                Dic[(self.input[0].FTag.Xindex,self.input[0].CTag[j].Xindex)]=-1.0
                Dic[(self.input[0].CTag[j].Xindex,self.input[0].FTag.Xindex)]=-1.0
            List.append(Dic)
        return List
        
    def EnergyBalHess(self):
        List=[]
        Dic={}
        for i in self.output:
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
        i=self.input[0]
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
