'''
Created on Jun 19, 2014

@author: Senthil
'''
import numpy
class Material_Stream:
    def __init__(self,Name,FlowTag,TempTag,PresTag,State,Therm,CTag,FreeBasis=[]):
        self.Name=Name
        self.FTag=FlowTag
        self.TTag=TempTag
        self.PTag=PresTag
        self.State=State
        self.h=0
        self.Therm=Therm
        self.FreeBasis=FreeBasis
        self.CTag=CTag
        self.CompList=CTag.keys()
        if (self.FreeBasis !=[]):
            if (len(self.FreeBasis)>1):
                print 'Error in Stream ',self.Name
                print 'Free Basis List has more than one component'
                exit()
            if (self.FreeBasis[0] not in self.CompList):
                print 'Error in Stream ',self.Name
                print 'Free Basis Component ','(', self.FreeBasis[0].Name, ')', 'is not present in the Stream'
                exit()
            if (self.CTag[self.FreeBasis[0]].Flag==1):
                print 'Error in Stream ',self.Name
                print 'Free Basis Component can not be measured'
                exit()
#             for i in self.CTag.keys():
#                 if (self.FreeBasis[0]!=i):
#                     self.CTag[i].Est=self.CTag[i].Est/(1.0+self.CTag[self.FreeBasis[0]].Est)
        self.Rho=Therm.RhoStream(self)
        self.perturb=1e-2
        self.HessDic={}
        self.GradDic={}
        self.PsatGradDic={}
        self.PsatHessDic={}

    def EnthalpyGradient(self):
        XID=[self.TTag,self.PTag]
        for i in self.CompList:
            XID.append(self.CTag[i])
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
        for i in self.CompList:
            XID.append(self.CTag[i])
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
                elif (ind1==ind2):
                    x=i.Est
                    dx=i.Est*self.perturb
                    i.Est=x+dx
                    f1=self.Therm.EnthalpyStream(self)
                    i.Est=x-dx
                    f_1=self.Therm.EnthalpyStream(self)
                    f0=self.h
                    i.Est=x
                    dhdt=(f1-2*f0+f_1)/(dx**2)
                    HDic[(i,i)]=dhdt
        return HDic
    
    def PsatGradient(self):
        XID=[self.TTag,self.PTag]
        for i in self.CompList:
            XID.append(self.CTag[i])
        GDic={}
        for i in XID:
            x=i.Est
            dx=i.Est*self.perturb
            i.Est=x+dx
            f1=self.Therm.PsatStream(self.output)
            i.Est=x-dx
            f_1=self.Therm.PsatStream(self.output)
            i.Est=x
            dhdt=(f1-f_1)/(2*dx)
            GDic[i]=dhdt
        return GDic
    
    def PsatHessian(self):
        XID=[self.TTag,self.PTag]
        for i in self.CompList:
            XID.append(self.CTag[i])
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
                    f11=self.Therm.PsatStream(self.output)
                    j.Est=y-dy
                    f1_1=self.Therm.PsatStream(self.output)
                    i.Est=x-dx
                    f_1_1=self.Therm.PsatStream(self.output)
                    j.Est=y+dy
                    f_11=self.Therm.PsatStream(self.output)
                    i.Est=x
                    j.Est=y
                    dhdt=(f11-f1_1-f_11+f_1_1)/(4*dx*dy)
                    HDic[(i,j)]=dhdt
                    HDic[(j,i)]=dhdt
                elif (ind1==ind1):
                    x=i.Est
                    dx=i.Est*self.perturb
                    i.Est=x+dx
                    f1=self.Therm.PsatStream(self.output)
                    i.Est=x-dx
                    f_1=self.Therm.PsatStream(self.output)
                    i.Est=x
                    f0=self.Therm.PsatStream(self.output)
                    dhdt=(f1-2*f0+f_1)/(dx**2)
                    HDic[(i,i)]=dhdt
        return HDic