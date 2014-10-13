'''
Created on Jun 19, 2014

@author: Senthil
'''

from numpy import zeros
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

    def MaterialBalRes(self):
        Resid=[]
        sum1=0
        for i in self.output:
            sum1=sum1+i.FTag.Est
#         Resid.append(sum1-self.input[0].FTag.Est)
        Resid.append(sum1/self.input[0].FTag.Est -1)
        return (Resid) # Overall Mass balance
    
#     def ComponentBalRes(self):
#         Resid=[]
#         key=self.input[0].CTag.keys()
#         for i in key[:-1]:
#             sum1=0
#             for j in self.output:
#                 if (i in j.CTag.keys()):                        
#                     sum1=sum1+j.FTag.Est * j.CTag[i].Est           
# #             sum2=self.input[0].FTag.Est*self.input[0].CTag[i].Est
#             Resid.append(sum1/(self.input[0].FTag.Est*self.input[0].CTag[i].Est) - 1) # N-1 Component Balances
#         return (Resid) # N-1 Component Balances

    def ComponentBalRes(self):
        Resid=[]
        key=self.input[0].CTag.keys()
        for i in key[:-1]:
            sum1=0
            for j in self.output:
                if (i in j.CTag.keys()):                        
                    sum1=sum1+j.FTag.Est * j.CTag[i].Est           
#             sum2=self.input[0].FTag.Est*self.input[0].CTag[i].Est
            Resid.append(sum1/(self.input[0].FTag.Est)-self.input[0].CTag[i].Est) # N-1 Component Balances
        return (Resid) # N-1 Component Balances
    
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
            print 'The number of Components in the inlet and outlet streams are not matching in the seperator'
            exit()
        if (len(self.dp)!=len(self.output)):
            print 'Length of delta pressure and number of output streams not matching'
            exit()
                   
    def EnergyBalRes(self):
        Resid=[]
        EnergyBal=0;
        for i in range(len(self.output)):
            EnergyBal=EnergyBal+self.output[i].FTag.Est*self.output[i].h  
        EnergyBal=EnergyBal/(self.input[0].FTag.Est*self.input[0].h) - 1 
        Resid.append(EnergyBal)
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        for ind,i in enumerate(self.output):
            Resid.append(1-(i.PTag.Est+self.dp[ind])/self.input[0].PTag.Est)
        return Resid      
    
    def MaterialBalJaco(self,len1):
        J=zeros((1,len1))
        sumM=0
        for i in self.output:
            sumM=sumM + i.FTag.Est
            if (i.FTag.Xindex!=2):
                J[0,i.FTag.Xindex]=1/self.input[0].FTag.Est;
        if (self.input[0].FTag.Xindex!=2):
            J[0,self.input[0].FTag.Xindex]=-sumM/(self.input[0].FTag.Est**2)
        return J
    
#     def ComponentBalJaco(self,len1):
#         J=zeros((len(self.input[0].CTag.keys())-1,len1))
#         key=self.input[0].CTag.keys()
#         for ind,i in enumerate(key[:-1]):
#             sumC=0.0
#             for j in self.output:
#                 if (i in j.CTag.keys()):
#                     sumC=sumC + j.FTag.Est*j.CTag[i].Est
#                     if (j.FTag.Flag!=2):
#                         J[ind,j.FTag.Xindex]=j.CTag[i].Est/(self.input[0].FTag.Est*self.input[0].CTag[i].Est)
#                     if (j.CTag[i].Flag!=2):
#                         J[ind,j.CTag[i].Xindex]=j.FTag.Est/(self.input[0].FTag.Est*self.input[0].CTag[i].Est)
#                
#             if (self.input[0].FTag.Flag!=2):
#                 J[ind,self.input[0].FTag.Xindex]=-sumC/(self.input[0].CTag[i].Est*self.input[0].FTag.Est**2)
#             if (self.input[0].CTag[i].Flag!=2):
#                 J[ind,self.input[0].CTag[i].Xindex]=-sumC/(self.input[0].FTag.Est*self.input[0].CTag[i].Est**2)
#         return J

    def ComponentBalJaco(self,len1):
        J=zeros((len(self.input[0].CTag.keys())-1,len1))
        key=self.input[0].CTag.keys()
        for ind,i in enumerate(key[:-1]):
            sumC=0.0
            for j in self.output:
                if (i in j.CTag.keys()):
                    sumC=sumC + j.FTag.Est*j.CTag[i].Est
                    if (j.FTag.Flag!=2):
                        J[ind,j.FTag.Xindex]=j.CTag[i].Est/(self.input[0].FTag.Est)
                    if (j.CTag[i].Flag!=2):
                        J[ind,j.CTag[i].Xindex]=j.FTag.Est/(self.input[0].FTag.Est)
               
            if (self.input[0].FTag.Flag!=2):
                J[ind,self.input[0].FTag.Xindex]=-sumC/(self.input[0].FTag.Est**2)
            if (self.input[0].CTag[i].Flag!=2):
                J[ind,self.input[0].CTag[i].Xindex]=-1
        return J

                    
    def EnergyBalJaco(self,len1):
        J=zeros((1,len1))
        sumFH=0.0
        finhin=self.input[0].FTag.Est*self.input[0].h
        for i in self.output:
            sumFH=sumFH + i.FTag.Est*i.h
            if (i.FTag.Flag!=2):
                J[0,i.FTag.Xindex]=i.h/finhin
             
            if (i.TTag.Flag!=2):            
                x=i.TTag.Est      
                dx=x*1e-5
                i.TTag.Est=x+dx
                f=i.Therm.EnthalpyStream(i)            
                i.TTag.Est=x
                dhdt=(f-i.h)/dx
                J[0,i.TTag.Xindex]=i.FTag.Est*dhdt/finhin
                #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
             
 
            if (i.PTag.Flag!=2):
                x=i.PTag.Est
                dx=x*1e-5
                i.PTag.Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.PTag.Est=x
                dhdt=(f-i.h)/dx
                J[0,i.PTag.Xindex]=i.FTag.Est*dhdt/finhin
                #J[0,i.PTag.Xindex]=0
 
            for j in i.CTag.keys():
                if (i.CTag[j].Flag!=2):
                    x=i.CTag[j].Est
                    dx=x*1e-5
                    i.CTag[j].Est=x+dx
                    f=i.Therm.EnthalpyStream(i)
                    i.CTag[j].Est=x
                    dhdt=(f-i.h)/dx
                    J[0,i.CTag[j].Xindex]=i.FTag.Est*dhdt/finhin
                    #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)
         
        if (self.input[0].FTag.Flag!=2):
            J[0,self.input[0].FTag.Xindex]=-sumFH/(self.input[0].h*self.input[0].FTag.Est**2)
         
        if (self.input[0].TTag.Flag!=2):
            x=self.input[0].TTag.Est
            dx=x*1e-5
            self.input[0].TTag.Est=x+dx
            f=self.input[0].Therm.EnthalpyStream(self.input[0])
            self.input[0].TTag.Est=x
            dhdt=(f-self.input[0].h)/dx
            J[0,self.input[0].TTag.Xindex]=-sumFH/(self.input[0].FTag.Est * self.input[0].h**2)*dhdt
            #J[0,self.input[0].TTag.Xindex]=-self.input[0].FTag.Est*self.input[0].Therm.CpStream(self.input[0])
         
        if (self.input[0].PTag.Flag!=2):
            x=self.input[0].PTag.Est
            dx=x*1e-5
            self.input[0].PTag.Est=x+dx
            f=self.input[0].Therm.EnthalpyStream(self.input[0])
            self.input[0].PTag.Est=x
            dhdt=(f-self.input[0].h)/dx
            J[0,self.input[0].PTag.Xindex]=-sumFH/(self.input[0].FTag.Est * self.input[0].h**2)*dhdt
            #J[0,self.input[0].PTag.Xindex]=0
         
        for i in self.input[0].CTag.keys():
            if (self.input[0].CTag[i].Flag!=2):
                x=self.input[0].CTag[i].Est
                dx=x*1e-5
                self.input[0].CTag[i].Est=x+dx
                f=self.input[0].Therm.EnthalpyStream(self.input[0])
                self.input[0].CTag[i].Est=x
                dhdt=(f-self.input[0].h)/dx
                J[0,self.input[0].CTag[i].Xindex]=-sumFH/(self.input[0].FTag.Est * self.input[0].h**2)*dhdt
                #J[0,self.input[0].CTag[i].Xindex]=-self.input[0].FTag.Est*self.input[0].Therm.CpComp(i,self.input[0].TTag.Est)        
        return J

    def EnergyBalJaco1(self,len1):
        J=zeros((1,len1))
        res=self.EnergyBalRes()
        for i in self.output:
            if (i.FTag.Flag!=2):
                x=i.FTag.Est      
                dx=x*1e-5
                i.FTag.Est=x+dx
                res1=self.EnergyBalRes()            
                i.FTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                J[0,i.FTag.Xindex]=dhdt
            
            if (i.TTag.Flag!=2):            
                x=i.TTag.Est      
                dx=x*1e-5
                i.TTag.Est=x+dx
                res1=self.EnergyBalRes()            
                i.TTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                print dhdt
                J[0,i.TTag.Xindex]=dhdt
                #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            

            if (i.PTag.Flag!=2):
                x=i.PTag.Est
                dx=x*1e-5
                i.PTag.Est=x+dx
                res1=self.EnergyBalRes()
                i.PTag.Est=x
                dhdt=(res1[0]-res[0])/dx
                J[0,i.PTag.Xindex]=dhdt
                #J[0,i.PTag.Xindex]=0

            for j in i.CTag.keys():
                if (i.CTag[j].Flag!=2):
                    x=i.CTag[j].Est
                    dx=x*1e-5
                    i.CTag[j].Est=x+dx
                    res1=self.EnergyBalRes()
                    i.CTag[j].Est=x
                    dhdt=(res1[0]-res[0])/dx
                    J[0,i.CTag[j].Xindex]=dhdt
                    #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)
        
        if (self.input[0].FTag.Flag!=2):
            x=self.input[0].FTag.Est      
            dx=x*1e-5
            self.input[0].FTag.Est=x+dx
            res1=self.EnergyBalRes()            
            self.input[0].FTag.Est=x
            dhdt=(res1[0]-res[0])/dx
            J[0,self.input[0].FTag.Xindex]=dhdt
        
        if (self.input[0].TTag.Flag!=2):
            x=self.input[0].TTag.Est
            dx=x*1e-5
            self.input[0].TTag.Est=x+dx
            res1=self.EnergyBalRes()
            self.input[0].TTag.Est=x
            dhdt=(res1[0]-res[0])/dx
            J[0,self.input[0].TTag.Xindex]=dhdt
            #J[0,self.input[0].TTag.Xindex]=-self.input[0].FTag.Est*self.input[0].Therm.CpStream(self.input[0])
        
        if (self.input[0].PTag.Flag!=2):
            x=self.input[0].PTag.Est
            dx=x*1e-5
            self.input[0].PTag.Est=x+dx
            res1=self.EnergyBalRes()
            self.input[0].PTag.Est=x
            dhdt=(res1[0]-res[0])/dx
            J[0,self.input[0].PTag.Xindex] = dhdt
            #J[0,self.input[0].PTag.Xindex]=0
        
        for i in self.input[0].CTag.keys():
            if (self.input[0].CTag[i].Flag!=2):
                x=self.input[0].CTag[i].Est
                dx=x*1e-5
                self.input[0].CTag[i].Est=x+dx
                res1=self.EnergyBalRes()
                self.input[0].CTag[i].Est=x
                dhdt=(res1[0]-res[0])/dx
                J[0,self.input[0].CTag[i].Xindex]=dhdt
                #J[0,self.input[0].CTag[i].Xindex]=-self.input[0].FTag.Est*self.input[0].Therm.CpComp(i,self.input[0].TTag.Est)        
        return J

    
    def PressureBalJaco(self,len1):
        J=zeros((len(self.output),len1))
        for ind,i in enumerate(self.output):
            if (i.PTag.Flag!=2):
                J[ind,i.PTag.Xindex]=-1/self.input[0].PTag.Est
            if (self.input[0].PTag.Flag!=2):
                J[ind,self.input[0].PTag.Xindex]=(i.PTag.Est+self.dp[ind])/(self.input[0].PTag.Est**2)
        return J 
    
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
   