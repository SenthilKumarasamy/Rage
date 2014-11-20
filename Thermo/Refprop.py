import RefpropDLLInterface as Rp
# from math import log
# from math import exp
# from numpy import asarray
import numpy
import math
#from CommonFunctions.Str2Dic import Str2Dic
class Refprop():
    Comp=[]
    def __init__(self,Comp):
        DBfile='Refprop.dat'
        self.Comp=Comp
        Name=[]
        ID=[]
        dHf=[]
        dGf=[]
        MF=[]
        MW=[]
        CompNameList=[]
        self.Xfrac=[0]*len(self.Comp)
        #f=open("D:\\Gyandata\\PythonRage\\RAGE2\\Rage\\Thermo\\" + DBfile,'r')
        #f=open("C:\\Users\\admin\\workspace\\Rage\\Thermo\\" + DBfile,'r')
        f=open("C:\\Users\\Senthil\\git\\Rage\\Thermo\\"+ DBfile,'r')
        Lines=f.readlines()
        for i in Lines:
            Temp=i.split('\t')
            ID.append(Temp[0])
            Name.append(Temp[1])
            dHf.append(float(Temp[2]))
            dGf.append(float(Temp[3]))#.replace("\n","")
            MF.append(Temp[4]) 
            MW.append(float(Temp[9].replace("\n","")))      
        for ind,i in enumerate(Comp):
            i.Name=Name[i.Id-1]
            CompNameList.append(i.Name)
            i.CompIndex=ind
        Rp.SETUP(CompNameList)
        Rp.PREOS(2)
        for i in Comp:
            Rp.PUREFLD(i.CompIndex+1)
            Rho,err=Rp.TPRHO(25+273, 101.325, [1], i.StdState)
            ComputedH=Rp.ENTHAL(25+273,[1],Rho)
            i.Hos=dHf[i.Id-1] - ComputedH
            ComputedS=Rp.ENTRO(25+273,[1],Rho)
            ActualS=(dHf[i.Id-1]-dGf[i.Id-1])/(25+273)
            i.Sos=ActualS - ComputedS
            i.MF=i.Str2Dic(MF[i.Id-1])
            i.MolWt=MW[i.Id-1]
        Rp.PUREFLD(0) #Resetting to mixture mode
    def EnthalpyComp(self,Comp,T,P,State):
        Temp=T+273
        Rp.PUREFLD(Comp.CompIndex+1)
        Rho,err=Rp.TPRHO(Temp, P, [1], State)
        Hpure=(Rp.ENTHAL(Temp, [1], Rho)+Comp.Hos)#*1e-6
        Rp.PUREFLD(0)
        return Hpure #GJ/Kg-mole
        
    def EntropyComp(self,Comp,T,P,State):
        Temp=T+273
        Rp.PUREFLD(Comp.CompIndex+1)
        Rho,err=Rp.TPRHO(Temp, P, [1], State)
        Spure=(Rp.ENTRO(Temp, [1], Rho)+Comp.Sos)#*1e-6
        Rp.PUREFLD(0)
        return Spure
    
    def GibbsComp(self,Comp,T,P,State):
        Temp=T+273
        H=self.EnthalpyComp(Comp,T,P,State)
        S=self.EntropyComp(Comp,T,P,State)
        G=H-Temp*S
        return G
    
    def DGRxn(self,Rxn,T,State):
    #def DGRxn(self,Rxn,T,P,State):
        key=Rxn.Coef.keys()
        DG=0.0
        for i in key:
            DG = DG + self.GibbsComp(i,T,100.0,State)*Rxn.Coef[i]
        return DG
    
    def EquilibriumConstant(self,Rxn,T,State,AppTemp=0.0):
    #def EquilibriumConstant(self,Rxn,T,P,State):
        R=8.314 # GigaJoules/(Kgmole K)
        Temp = T + AppTemp + 273
        #K = math.exp(-self.DGRxn(Rxn,T,P,State)/(R*Temp))
        K = math.exp(-self.DGRxn(Rxn,T+AppTemp,State)/(R*Temp))
        return K
        
#     def EnthalpyStream(self,Stream):
#         Rp.PUREFLD(0)
#         key = Stream.CTag.keys()
#         Hos=0.0
#         for i in key:
#             Hos=Hos+i.Hos*Stream.CTag[i].Est # Computing Mixture Offset
#             if i in self.Comp:
#                 self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
#             else:
#                 self.Xfrac[i.CompIndex]=0.0
#         Rho,err=Rp.TPRHO(Stream.TTag.Est+273, Stream.PTag.Est, self.Xfrac, Stream.State)
#         if (err!=0):
#             print 'Error while calculating density of the stream ',Stream.Name
#             print 'Error occurred when temperature and pressure are ', Stream.TTag.Est, ' and ', Stream.PTag.Est 
#             exit()
#         Hstrm=Rp.ENTHAL(Stream.TTag.Est+273,self.Xfrac,Rho)+Hos
#         return Hstrm

    def EnthalpyStream(self,Stream):
        Rp.PUREFLD(0)
        key = Stream.CTag.keys()
        Hos=0.0
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
                Hos=Hos+i.Hos*Stream.CTag[i].Est # Computing Mixture Offset
            else:
                self.Xfrac[i.CompIndex]=0.0
        Rho,err=Rp.TPRHO(Stream.TTag.Est+273, Stream.PTag.Est, self.Xfrac, Stream.State,1,Stream.Rho)
        if (err!=0):
            print 'Error code ',err
            print 'Error while calculating density of the stream ',Stream.Name
            print 'Error occurred when temperature and pressure are ', Stream.TTag.Est, ' and ', Stream.PTag.Est 
            exit()
        Stream.Rho=Rho
        Hstrm=Rp.ENTHAL(Stream.TTag.Est+273,self.Xfrac,Rho)+Hos
        return Hstrm

    
    def Fugacity(self,Stream):
        fu={}
        Rp.PUREFLD(0)
        key = Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
            else:
                self.Xfrac[i.CompIndex]=0
        sum1=sum(numpy.asarray(self.Xfrac))
        for i in self.Comp:
            self.Xfrac[i.CompIndex]=self.Xfrac[i.CompIndex]/sum1
        Rho,err=Rp.TPRHO(Stream.TTag.Est+273, Stream.PTag.Est, self.Xfrac, Stream.State)           
        Fgctystrm=Rp.FGCTY(Stream.TTag.Est+273,self.Xfrac,Rho)
        for ind,i in enumerate(self.Comp):
            if i in key:
                fu[i]=Fgctystrm[ind]
        return fu
    
#     def FugacityCoefficient(self,Temp,Press,State,Composition):
#         fu={}
#         Rp.PUREFLD(0)
#         key = Composition.keys()
#         for i in self.Comp:
#             if i in key:
#                 self.Xfrac[i.CompIndex]=Composition[i]
#             else:
#                 self.Xfrac[i.CompIndex]=0
#         Rho,err=Rp.TPRHO(Temp+273, Press, self.Xfrac, State)           
#         Fgctystrm,err=Rp.FUGCOF(Temp+273,self.Xfrac,Rho)
#         if (err!=0):
#             print 'Error: Occured while computing Fucacity Coefficient'
#             exit()
#         else:
#             for ind,i in enumerate(self.Comp):
#                 if i in key:
#                     fu[i]=Fgctystrm[ind]
#         return fu
#     
#     def MolWtComp(self,Comp):
#         Rp.PUREFLD(Comp.CompIndex+1)
#         Mw=Rp.WMOL([1])
#         Rp.PUREFLD(0)
#         return Mw
    
    def RhoStreamAtNTP(self,Stream):
        key = Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
            else:
                self.Xfrac[i.CompIndex]=0
        Rho,err=Rp.TPRHO(273, 101.325, self.Xfrac, Stream.State)
        return Rho
    
    def RhoStreamAtSTP(self,Stream):
        key = Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
            else:
                self.Xfrac[i.CompIndex]=0
        Rho,err=Rp.TPRHO(15.5+273, 101.325, self.Xfrac, Stream.State)
        return Rho
    
    def PsatStream(self,Stream):
        key = Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
            else:
                self.Xfrac[i.CompIndex]=0
        Psat,err=Rp.SATT(Stream.TTag.Est+273,self.Xfrac,1)
        if (err!=0):
            print 'Error code ',err
            print 'Error while calculating saturation pressure  of the stream ',Stream.Name
            print 'Error occurred when temperature and pressure are ', Stream.TTag.Est, ' and ', Stream.PTag.Est 
            exit()
            #return Psat
        else:
            return Psat
    
    def RhoStream(self,Stream):
        Rp.PUREFLD(0)
        key = Stream.CTag.keys()
        for i in self.Comp:
            if i in key:
                self.Xfrac[i.CompIndex]=Stream.CTag[i].Est
            else:
                self.Xfrac[i.CompIndex]=0.0
        Rho,err=Rp.TPRHO(Stream.TTag.Est+273.0, Stream.PTag.Est, self.Xfrac, Stream.State)
        if (err!=0):
            print 'Error code ',err
            print 'Error while calculating density of the stream ',Stream.Name
            print 'Error occurred when temperature and pressure are ', Stream.TTag.Est, ' and ', Stream.PTag.Est 
            exit()
        else:
            return Rho

        
        
        