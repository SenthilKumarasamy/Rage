from Units.Seperator import Seperator
from numpy import *
class PSA(Seperator):
    def __init__(self,Name,input,output,RecLmt=[],dp=[]):
        self.Name=Name
        self.input=[]
        self.output=[]
        for i in output:
            self.output.append(i)
        self.input.append(input)
        self.LenMatRes=1
        self.LenCompRes=len(input.CTag.keys())+len(RecLmt.keys())-1
        self.LenEneRes=1
        self.LenPreRes=len(self.output)
        if (len(dp)==0):
            self.dp=zeros((len(self.output)))
        elif (len(dp)==len(self.output)):
            self.dp=dp
        self.RecLmt=RecLmt
        self.validation()
    def ComponentBalRes(self):
        Resid=[]
        key=self.input[0].CTag.keys()
        for i in key[:-1]:
            sum1=0
            for j in self.output:
                if (i in j.CTag.keys()):                        
                    sum1=sum1+j.FTag.Est * j.CTag[i].Est           
            Resid.append(sum1-self.input[0].FTag.Est*self.input[0].CTag[i].Est) # N-1 Component Balances
        for i in self.RecLmt.keys():
            Resid.append(self.RecoveryConstraint(i))
        return (Resid) # N-1 Component Balances
    
    def RecoveryConstraint(self,RecLmt):
        Resid= -self.RecLmt[RecLmt] * self.input[0].FTag.Est * self.input[0].CTag[RecLmt[1]].Est + RecLmt[0].FTag.Est * RecLmt[0].CTag[RecLmt[1]].Est
        return (Resid)
    
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
        ind=ind+1
        for ind1, i in enumerate(self.RecLmt.keys()):
            if (self.input[0].FTag.Flag!=2):
                row.append(ind+ind1)
                col.append(self.input[0].FTag.Xindex)
            if (self.input[0].CTag[i[1]].Flag!=2):
                row.append(ind+ind1)
                col.append(self.input[0].CTag[i[1]].Xindex)
            if (i[0].FTag.Flag !=2):
                row.append(ind+ind1)
                col.append(i[0].FTag.Xindex)
            if (i[0].CTag[i[1]].Flag!=2):
                row.append(ind+ind1)
                col.append(i[0].CTag[i[1]].Xindex)
        return row,col
    
    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        print J.shape
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
        ind=ind+1
        for ind1, i in enumerate(self.RecLmt.keys()):
            if (self.input[0].FTag.Flag!=2):
                J[ind+ind1,self.input[0].FTag.Xindex] = - self.RecLmt[i] * self.input[0].CTag[i[1]].Est
            if (self.input[0].CTag[i[1]].Flag!=2):
                J[ind+ind1,self.input[0].CTag[i[1]].Xindex] = - self.RecLmt[i] * self.input[0].FTag.Est
            if (i[0].FTag.Flag !=2):
                J[ind+ind1,i[0].FTag.Xindex]= i[0].CTag[i[1]].Est
            if (i[0].CTag[i[1]].Flag!=2):
                J[ind+ind1,i[0].CTag[i[1]].Xindex]= i[0].FTag.Est
        return J
    
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
        ind=ind+1
        for ind1,i in enumerate(self.RecLmt.keys()):
            if (self.input[0].FTag.Flag !=2 and self.input[0].CTag[j].Flag !=2):
                List[ind+ind1].append((self.input[0].FTag.Xindex,self.input[0].CTag[i[1]].Xindex))
                List[ind+ind1].append((self.input[0].CTag[i[1]].Xindex,self.input[0].FTag.Xindex))
            if (i[0].FTag.Flag !=2 and i[0].CTag[i[1]].Flag !=2):
                List[ind+ind1].append((i[0].FTag.Xindex,i[0].CTag[i[1]].Xindex))
                List[ind+ind1].append((i[0].CTag[i[1]].Xindex,i[0].FTag.Xindex))    
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
        for i in self.RecLmt.keys():
            Dic={}
            if (self.input[0].FTag.Flag !=2 and self.input[0].CTag[i[1]].Flag !=2):
                Dic[(self.input[0].FTag.Xindex,self.input[0].CTag[i[1]].Xindex)]=-self.RecLmt[i]
                Dic[(self.input[0].CTag[i[1]].Xindex,self.input[0].FTag.Xindex)]=-self.RecLmt[i]
            if (i[0].FTag.Flag !=2 and i[0].CTag[i[1]].Flag !=2):
                Dic[(i[0].FTag.Xindex,i[0].CTag[i[1]].Xindex)]=1
                Dic[(i[0].CTag[i[1]].Xindex,i[0].FTag.Xindex)]=1
            List.append(Dic)
        return List
    
    def ComponentBalBound(self):
        LB=zeros((self.LenCompRes))
        UB=zeros((self.LenCompRes))
        for i in range(len(self.input[0].CTag.keys())-1,self.LenCompRes):
            LB[i]=-inf
        return LB,UB
 
