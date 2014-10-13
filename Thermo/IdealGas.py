'''
Created on Jul 7, 2014

@author: Senthil

'''
from math import log
from math import exp
from CommonFunctions.Str2Dic import Str2Dic
class IdealGas():
    Comp=[]
    def __init__(self,Comp,DBfile):
        self.Comp=Comp
        Name=[]
        ID=[]
        a=[]
        b=[]
        c=[]
        d=[]
        dHf=[]
        dGf=[]
        MF=[]
        MW=[]
        self.R=8.314
        f=open("D:\\Gyandata\\PythonRage\\RAGE3\\src\\Thermo\\" + DBfile,'r')
        Lines=f.readlines()
        for i in Lines:
            Temp=i.split('\t')
            Name.append(Temp[1])
            ID.append(Temp[0])
            a.append(float(Temp[5]))
            b.append(float(Temp[6]))
            c.append(float(Temp[7]))
            d.append(float(Temp[8].replace("\n","")))
            dHf.append(float(Temp[2]))
            dGf.append(float(Temp[3]))#.replace("\n","")
            MF.append(Temp[4])
            MW.append(float(Temp[9].replace("\n","")))
        for i in Comp:
            i.Name=Name[i.Id-1]
            i.abcd=[a[i.Id-1],b[i.Id-1],c[i.Id-1],d[i.Id-1]]
            ComputedH=self.EnthalpyComp(i,25)
            print 'H Compute',ComputedH
            print 'H actual', dHf[i.Id-1]
            i.Hos=dHf[i.Id-1] - ComputedH
            ComputedS=self.EntropyComp(i,25,101.325)
            ActualS=(dHf[i.Id-1]-dGf[i.Id-1])/(25+273)
            i.Sos=ActualS - ComputedS
            i.MF=Str2Dic(MF[i.Id-1])
            i.MolWt=MW[i.Id-1]
    
    def EnthalpyComp(self,Comp,T):
        #R=8.314  #KJ/(Kg-mole K)
        a=Comp.abcd
        Temp=T+273
        Hpure=(a[0]*Temp+0.5*a[1]*Temp**2+a[2]/3*Temp**3-a[3]/Temp)*self.R
        Hpure=(Hpure+Comp.Hos)#*1e-6
        return Hpure #GJ/Kg-mole
        
    def EntropyComp(self,Comp,T,P):
        #R=8.314
        a=Comp.abcd
        Temp=T+273
        I=(a[0]*log(Temp)+a[1]*Temp+0.5*a[2]*Temp**2 - (1/3)*a[3]*Temp**(-3))*self.R
        Spure=I+Comp.Sos-self.R*log(P/101.325)
        return Spure
    
    def GibbsComp(self,Comp,T,P):
        Temp=T+273
        H=self.EnthalpyComp(Comp,T)
        S=self.EntropyComp(Comp,T,P)
        G=H-Temp*S
        return G
       
    def DGRxn(self,Rxn,T,P):
        key=Rxn.Coef.keys()
        DG=0.0
        for i in key:
            DG = DG + self.GibbsComp(i,T,P)*Rxn.Coef[i]
        return DG
    
    def EquilibriumConstant(self,Rxn,T,P):
        #R=8.314 # GigaJoules/(Kgmole K)
        Temp = T +273
        K = exp(-self.DGRxn(Rxn,T,P)/(self.R*Temp))
        return K
        
    def EnthalpyStream(self,Stream):
        Hmix = 0
        key = Stream.CTag.keys()
        for i in key:
            Hmix = Hmix + Stream.CTag[i].Est*self.EnthalpyComp(i, Stream.TTag.Est)
        return Hmix
    
    def Fugacity(self,Stream):
        fu={}
        key=Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                fu[i]=Stream.CTag[i].Est*Stream.PTag.Est
        return fu
    def RhoStream(self,Stream,T,P):
        Temp=T+273
        Rho=P/(self.R*Temp)
        return Rho