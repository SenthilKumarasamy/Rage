from numpy import zeros
from Units.Seperator import Seperator
class Splitter(Seperator):
    def __init__(self,Name,input,output):
        self.Name=Name
        self.input=[]
        self.output=[]
        for i in output:
            self.output.append(i)
        self.input.append(input)
        self.LenMatRes=1
        self.LenCompRes=(len(self.input[0].CTag.keys())-1)*len(self.output)
        self.LenEneRes=len(self.output)
        self.LenPreRes=len(self.output)
        self.dp=zeros((self.LenPreRes))
        self.validation()
        
    def ComponentBalRes(self):
        Resid=[]
        for j in self.output:
            key=self.input[0].CTag.keys()
            for i in key[:-1]:
                Resid.append(j.CTag[i].Est-self.input[0].CTag[i].Est)
        return Resid
                
    def EnergyBalRes(self):
        Resid=[]
        for i in self.output:
            Resid.append(1-self.input[0].TTag.Est/i.TTag.Est)
        return (Resid)
    
    def ComponentBalJaco(self,len1):
        inputcomp=self.input[0].CTag.keys()
        N=len(inputcomp[:-1])
        J=zeros((self.LenCompRes,len1))
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
                J[ind,i.TTag.Xindex]=self.input[0].TTag.Est/i.TTag.Est**2
            if (self.input[0].TTag.Flag!=2):
                J[ind,self.input[0].TTag.Xindex]=-1/i.TTag.Est       
        return J
    
    
    def ComponentBalJacoNZP(self):
        row=[]
        col=[]
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
    
    
    def validation(self):
        for i in self.input[0].CTag.keys():
            for j in self.output:
                if (i not in j.CTag.keys()):
                    print 'All components in the inlet stream are not present in output streams'
                    exit()
 