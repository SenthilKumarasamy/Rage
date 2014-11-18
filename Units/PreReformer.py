from numpy import zeros
from numpy import asarray
from math import exp
from Units.EquilibriumReactor import EquilibriumReactor
class PreReformer(EquilibriumReactor):
    def EquilibriumConstraint(self,Rxn):
        ## This function computes the residual of the equilibibrium Constraint
        
        Prod=1.0
        mu=sum(Rxn.Coef.values())
        for i in Rxn.Coef.keys():
            Prod=Prod*(self.Pstrm.CTag[i].Est)**(Rxn.Coef[i])
        Prod=Prod*(self.Pstrm.PTag.Est/100.0)**mu
        T=self.Pstrm.TTag.Est+Rxn.EquTempApp+273
        Z=(1000.0/T)-1.0
        if (sum(Rxn.Coef.values())==-2):
            ## Equilibrium Constant.
            K=exp(Z*(Z*(Z*(0.2513*Z-0.3665)-0.58101)+27.1337)-3.2770);
            #K=1.0/K
        elif (sum(Rxn.Coef.values())==0):
            K=exp(Z*(Z*(0.63508-0.29353*Z)+4.1778)+0.31688)
        else:
            print 'Error in Unit ',self.Name,'. The specified reaction is neither methanation nor water gas shift reaction'
            exit
        #K=self.Pstrm.Therm.EquilibriumConstant(Rxn,self.Pstrm.TTag.Est,self.Pstrm.State)*(self.Pstrm.PTag.Est/100.0)**(-mu)
        Resid=(1 - Prod/K)
        return Resid