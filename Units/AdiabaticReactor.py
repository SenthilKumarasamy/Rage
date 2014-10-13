'''
Created on Aug 6, 2014

@author: Senthil
'''
from numpy import zeros
from Units.Reactor import Reactor
class AdiabaticReactor(Reactor):
    def __init__(self,Name,Rstrm,Pstrm,Rxn,dp=0): #ExoEndoFlag=1,
#===================Validation Starts======================================
        self.Name=Name
#         if ((ExoEndoFlag != -1) and (ExoEndoFlag != 1)):
#             print 'Error: ExoEndoFlag of a Reactor is not valid option. The valid option is 1 for Endo and -1 for Exo thermic reactions'
#             exit()        
        if (Rstrm==Pstrm):
            print 'Reactant and Product streams are the same. They have to be different'
            exit()
#         elif (len(Rstrm)>1):
#             print 'More than one reactant stream is defined. But only one reactant stream is allowed'
#             exit()
#         elif (len(Pstrm)>1):
#             print 'More than one product stream is defined. But only one product stream is allowed'
#             exit()
        # Checking for uniqueness of Rxn
        C=[]
        for i in Rxn:
            if (i not in C):
                C.append(i)
        if (len(C)!=len(Rxn)):
            print 'Reactions of a reactor are not uniques'
            exit()
        R=[]
        P=[]    
        for i in Rxn:
            for j in i.Coef.keys():
                if ((i.Coef[j]>0) and (j not in P)):
                    P.append(j)
                elif ((i.Coef[j]<0) and (j not in C)):
                    R.append(j)
        for i in R:
            if (i not in Rstrm.CTag.keys()):
                print 'One of the reactants of a reaction is not present in the reactant stream of a reactor'
                exit()
        
        for i in P:
            if (i not in Pstrm.CTag.keys()):
                print 'One of the products of a reaction is not present in the product stream of a reactor'
                exit()
#====================================Validation ends=================================        
        self.Rstrm=Rstrm
        self.Pstrm=Pstrm
        self.Dp=dp
        self.RxnExt={}
        self.RxnExtXindex={}
        for i in Rxn:
            self.RxnExt[i]=0
            self.RxnExtXindex[i]=0
            
        self.ListComp=[]
        for i in self.Pstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        for i in self.Rstrm.CTag.keys():
            if (i not in self.ListComp):
                self.ListComp.append(i)
        self.SMat=self.StoichioMatrix()
#         self.EFlag=ExoEndoFlag
        self.LenMatRes=0
        self.LenCompRes=len(self.ListComp)
        self.LenEneRes=1
        self.LenPreRes=1
        self.InitialExt=self.InitialGuessRxnExt()
    
    def EnergyBalRes(self):
        Resid=[]
        Resid.append(1 - self.Pstrm.h * self.Pstrm.FTag.Est/(self.Rstrm.h * self.Rstrm.FTag.Est))
        return Resid
    
    def EnergyBalJaco(self,len1):
        J = zeros((self.LenEneRes,len1))
               
        i=self.Rstrm
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= -(- self.Pstrm.FTag.Est * self.Pstrm.h)/(i.h * i.FTag.Est**2)
             
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex] = -(- self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            
            
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= -(- self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.PTag.Xindex]=0
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= -(- self.Pstrm.FTag.Est * self.Pstrm.h)/(i.FTag.Est * i.h**2) * dhdt
            #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)

        i=self.Pstrm
        Term1=self.Rstrm.FTag.Est * self.Rstrm.h
        if (i.FTag.Flag!=2):
            J[0,i.FTag.Xindex]= -i.h/Term1
         
        if (i.TTag.Flag!=2):            
            x=i.TTag.Est      
            dx=x*1e-5
            i.TTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)            
            i.TTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.TTag.Xindex] = -i.FTag.Est/Term1 * dhdt
            #J[0,i.TTag.Xindex]=i.FTag.Est*i.Therm.CpStream(i)
            
            
        if (i.PTag.Flag!=2):
            x=i.PTag.Est
            dx=x*1e-5
            i.PTag.Est=x+dx
            f=i.Therm.EnthalpyStream(i)
            i.PTag.Est=x
            dhdt=(f-i.h)/dx
            J[0,i.PTag.Xindex]= -i.FTag.Est/Term1 * dhdt
            #J[0,i.PTag.Xindex]=0
            
        for j in i.CTag.keys():
            if (i.CTag[j].Flag!=2):
                x=i.CTag[j].Est
                dx=x*1e-5
                i.CTag[j].Est=x+dx
                f=i.Therm.EnthalpyStream(i)
                i.CTag[j].Est=x
                dhdt=(f-i.h)/dx
                J[0,i.CTag[j].Xindex]= -i.FTag.Est/Term1 * dhdt
                #J[0,i.CTag[j].Xindex]=i.FTag.Est*i.Therm.EnthalpyComp(j,i.TTag.Est)
        return J
    
    def EnergyBalJacoNZP(self):
        row=[]
        col=[]
                           
        i=self.Rstrm
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

        i=self.Pstrm
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

