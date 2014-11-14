from numpy import zeros
from numpy import asarray
from math import exp
from Units.EquilibriumReactor import EquilibriumReactor
class ShiftReactor(EquilibriumReactor):
    def EquilibriumConstraint(self,Rxn):
        ## This function computes the residual of the equilibibrium Constraint
        
        Prod=1.0
        mu=sum(Rxn.Coef.values())
        for i in Rxn.Coef.keys():
            Prod=Prod*(self.Pstrm.CTag[i].Est)**(Rxn.Coef[i])
        Prod=Prod*(self.Pstrm.PTag.Est/100.0)**mu
        T=self.Pstrm.TTag.Est+self.EquEff[Rxn]+273.0
        Z=(1000.0/T)-1.0
        K=exp(Z*(Z*(0.63508-0.29353*Z)+4.1778)+0.31688)
        Resid=(1 - Prod/K)
        return Resid