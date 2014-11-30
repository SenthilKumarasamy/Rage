from Streams.Sensor import Sensor
from Thermo.Refprop import Refprop
from Component.Comp import Comp
class FixedConcStream:
    def __init__(self,Name,FlowTag,TempTag,PresTag,State,Therm,Cval,CUnit,Describe=[]):
        self.FTag=FlowTag
        self.TTag=TempTag
        self.PTag=PresTag
        self.State=State
        self.Name=Name
        self.Describe=Describe
        self.h=0
        self.Therm=Therm
        self.CTag={}
        if (sum(Cval.values())!=1):
            print 'Error in ',self.Name,' Concentration of the components are not summing up one.'
            quit()
        else:
            for i in Cval.keys():
                self.CTag.update({i:Sensor(Cval[i])})
            for i in Cval.keys():
                self.CTag[i].Unit=CUnit
                self.CTag[i].Sigma=1
                self.CTag[i].Flag=2 
        self.Rho=Therm.RhoStream(self)             
        self.h=Therm.EnthalpyStream(self)
        self.perturb=1e-2
        self.HessDic={}
        self.GradDic={}
#------------------------------------------------------------------------
    def EnthalpyGradient(self):
        XID=[self.TTag,self.PTag]
        GDic={}
        for i in XID:
            x=i.Est
            dx=i.Est*self.perturb
            if (dx==0.0):
                dx=0.01
            i.Est=x+dx
            f1=self.Therm.EnthalpyStream(self)
            i.Est=x-dx
            f_1=self.Therm.EnthalpyStream(self)
            i.Est=x
            dhdt=(f1-f_1)/(2*dx)
            GDic[i]=dhdt 
        return GDic
    
    def EnthalpyHessian(self):
        XID=[self.TTag,self.PTag]
        HDic={}
        for ind1,i in enumerate(XID):
            for ind2,j in enumerate(XID):
                if (ind1>ind2):
                    x=i.Est
                    y=j.Est
                    dx=i.Est*self.perturb
                    dy=i.Est*self.perturb
                    if (dx==0.0):
                        dx=0.01
                    if (dy==0.0):
                        dy=0.01
                    if (dx !=0 and dy !=0):
                        i.Est=x+dx
                        j.Est=y+dy
                        f11=self.Therm.EnthalpyStream(self)
                        j.Est=y-dy
                        f1_1=self.Therm.EnthalpyStream(self)
                        i.Est=x-dx
                        f_1_1=self.Therm.EnthalpyStream(self)
                        j.Est=y+dy
                        f_11=self.Therm.EnthalpyStream(self)
                        i.Est=x
                        j.Est=y
                        dhdt=(f11-f1_1-f_11+f_1_1)/(4*dx*dy)
                        HDic[(i,j)]=dhdt
                        HDic[(j,i)]=dhdt
                    else:
                        print 'Error: Divide by zero. Name of the Stream is  ',self.Name
                        exit()
                elif (ind1==ind2):
                    x=i.Est
                    dx=i.Est*self.perturb
                    if (dx!=0):
                        i.Est=x+dx
                        f1=self.Therm.EnthalpyStream(self)
                        i.Est=x-dx
                        f_1=self.Therm.EnthalpyStream(self)
                        f0=self.h
                        i.Est=x
                        dhdt=(f1-2*f0+f_1)/(dx**2)
                        HDic[(i,i)]=dhdt
                    else:
                        print 'Error: Divide by zero. Name of the Stream is  ',self.Name
                        exit()
        return HDic
    
    def PsatGradient(self):
        XID=[self.TTag,self.PTag]
        GDic={}
        for i in XID:
            x=i.Est
            dx=i.Est*self.perturb
            i.Est=x+dx
            f1=self.Therm.PsatStream(self)
            i.Est=x-dx
            f_1=self.Therm.PsatStream(self)
            i.Est=x
            dhdt=(f1-f_1)/(2*dx)
            GDic[i]=dhdt
        return GDic
    
    def PsatHessian(self):
        XID=[self.TTag,self.PTag]
        HDic={}
        for ind1,i in enumerate(XID):
            for ind2,j in enumerate(XID):
                if (ind1>ind2):
                    x=i.Est
                    y=j.Est
                    dx=i.Est*self.perturb
                    dy=i.Est*self.perturb
                    i.Est=x+dx
                    j.Est=y+dy
                    f11=self.Therm.PsatStream(self)
                    j.Est=y-dy
                    f1_1=self.Therm.PsatStream(self)
                    i.Est=x-dx
                    f_1_1=self.Therm.PsatStream(self)
                    j.Est=y+dy
                    f_11=self.Therm.PsatStream(self)
                    i.Est=x
                    j.Est=y
                    dhdt=(f11-f1_1-f_11+f_1_1)/(4*dx*dy)
                    HDic[(i,j)]=dhdt
                    HDic[(j,i)]=dhdt
                elif (ind1==ind1):
                    x=i.Est
                    dx=i.Est*self.perturb
                    i.Est=x+dx
                    f1=self.Therm.PsatStream(self)
                    i.Est=x-dx
                    f_1=self.Therm.PsatStream(self)
                    i.Est=x
                    f0=self.Therm.PsatStream(self)
                    dhdt=(f1-2*f0+f_1)/(dx**2)
                    HDic[(i,i)]=dhdt
        return HDic