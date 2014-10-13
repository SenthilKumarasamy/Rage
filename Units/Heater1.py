from Units.Seperator import Seperator
from numpy import zeros
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
#         self.input.append(input)
#         self.output.append(output)
        self.LenMatRes=1
        self.LenCompRes=len(self.input.CTag.keys())-1
        self.LenEneRes=1
        self.LenPreRes=1
        self.Resid=[]
        self.Qstrm=Q1
        #self.Qstrm.Q.Meas=abs(self.output.FTag.Est * self.output.Therm.EnthalpyStream(self.output) - self.input.FTag.Est * self.input.Therm.EnthalpyStream(self.input))
        #self.Qstrm.Q.Est=abs(self.output.FTag.Est*self.output.Therm.EnthalpyStream(self.output)-self.input.FTag.Est*self.input.Therm.EnthalpyStream(self.input))
        self.validation()
    
    def MaterialBalRes(self):
        Resid=[]
        Resid.append(1-self.output.FTag.Est/self.input.FTag.Est)
        return Resid
    
    def ComponentBalRes(self):
        Resid=[]
        ShellComp=self.input.CTag.keys()
        for i in ShellComp[:-1]:
            Resid.append(1-self.output.FTag.Est*self.output.CTag[i].Est/(self.input.FTag.Est*self.input.CTag[i].Est))
        return Resid
        
    def EnergyBalRes(self):
        Resid=[]
        QShell= 1 + self.Qstrm.Q.Est*self.HCFlag/(self.input.FTag.Est*self.input.h) - self.output.FTag.Est*self.output.h/(self.input.FTag.Est*self.input.h)
        Resid.append(QShell)                   
        return Resid
    
    def PressureBalRes(self):
        Resid=[]
        Resid.append(1 - (self.output.PTag.Est + self.Dp)/self.input.PTag.Est)
        return Resid

    def MaterialBalJaco(self,len1):
        J=zeros((self.LenMatRes,len1))
        if (self.input.FTag.Flag != 2):
            J[0,self.input.FTag.Xindex] = self.output.FTag.Est/self.input.FTag.Est**2
        if (self.output.FTag.Flag != 2):
            J[0,self.output.FTag.Xindex] = -1.0/self.input.FTag.Est
        return J
    
    def ComponentBalJaco(self,len1):
        J=zeros((self.LenCompRes,len1))
        inputcomp=self.input.CTag.keys()
        for ind,i in enumerate(inputcomp[:-1]):
            if (self.input.FTag.Flag != 2):
                J[ind,self.input.FTag.Xindex] = (self.output.CTag[i].Est*self.output.FTag.Est)/(self.input.CTag[i].Est*self.input.FTag.Est**2)
            if (self.input.CTag[i].Flag != 2):
                J[ind,self.input.CTag[i].Xindex] = (self.output.CTag[i].Est * self.output.FTag.Est)/(self.input.FTag.Est * self.input.CTag[i].Est **2)
            if (self.output.FTag.Flag != 2):
                J[ind,self.output.FTag.Xindex] = -self.output.CTag[i].Est/(self.input.CTag[i].Est * self.input.FTag.Est)
            if (self.output.CTag[i].Flag != 2):
                J[ind,self.output.CTag[i].Xindex] = -self.output.FTag.Est/(self.input.CTag[i].Est * self.input.FTag.Est)      
        return J
    
    def EnergyBalJaco(self,len1):
        J=zeros((self.LenEneRes,len1))
        Term1=-(self.Qstrm.Q.Est*self.HCFlag-self.output.FTag.Est*self.output.h)
        i=self.input
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=Term1/(i.h*i.FTag.Est**2)
                
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)
                       
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)

        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= Term1*dhdt/(i.FTag.Est * i.h**2)

        i = self.output
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]=-i.h/(self.input.FTag.Est * self.input.h)
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex]=-i.FTag.Est*dhdt/(self.input.FTag.Est * self.input.h)
                           
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]=-i.FTag.Est*dhdt/(self.input.FTag.Est * self.input.h)

        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]=-i.FTag.Est*dhdt/(self.input.FTag.Est * self.input.h)
        #J[0,self.Qstrm.Xindex] = self.HCFlag/(self.input.FTag.Est*self.input.h)
        J[0,self.Qstrm.Q.Xindex] = self.HCFlag/(self.input.FTag.Est*self.input.h)
                
        return J

    def PressureBalJaco(self,len1):
        J=zeros((self.LenPreRes,len1))
        if (self.input.PTag.Flag != 2):
            J[0,self.input.PTag.Xindex] = (self.Dp+self.output.PTag.Est)/self.input.PTag.Est**2
        if (self.output.PTag.Flag != 2):
            J[0,self.output.PTag.Xindex] = -1/self.input.PTag.Est
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
        inputcomp=self.input.CTag.keys()
        for ind,i in enumerate(inputcomp[:-1]):
            if (self.input.FTag.Flag != 2):
                row.append(ind)
                col.append(self.input.FTag.Xindex)
            if (self.input.CTag[i].Flag != 2):
                row.append(ind)
                col.append(self.input.CTag[i].Xindex)
            if (self.output.FTag.Flag != 2):
                row.append(ind)
                col.append(self.output.FTag.Xindex)
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
        #col.append(self.Qstrm.Xindex)
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
    
    def validation(self):
        for i in self.input.CTag.keys():
            if (i not in self.output.CTag.keys()):
                print 'All components in the inlet stream are not present in output streams'
                exit()
 






