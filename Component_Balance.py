from Streams.Comp import Comp
from Streams.Material_Stream import Material_Stream
from Streams.Reaction import Reaction
from Streams.Energy_Stream import Energy_Stream
from Streams.Therm import Therm

from Units.Reactor import Reactor
from Units.EquilibriumReactor import EquilibriumReactor
from Units.Heater import Heater
from Units.Mixer import Mixer
from Units import Seperator.Splitter

#import ConstructionX as conx

from scipy.optimize import minimize
from numpy import inf
from numpy import array

import Constraints as Con
#global ListUnits, ListStreams
if __name__ == "__main__":
    CH4=Comp(48)
    C2H6=Comp(29)


    CL=[CH4,C2H6]
    Therm1=Therm(CL,0,0,200+273.16,101.325)


    F=Material_Stream('FT100','TT100',101.325,2,Therm1,CL,['CT100','CT101'])
    T=Material_Stream('FT101','TT101',101.325,2,Therm1,CL,['CT102','CT103'])
    B=Material_Stream('FT102','TT102',101.325,2,Therm1,CL,['CT104','CT105'])
    SPL=Seperator(F,[T,B])
    SPL.Residual()
    
    ListUnits=[SPL]
    ListStreams=[F,T,B]
    Xmeas=Con.ConstructX(ListUnits, ListStreams)
    [XFlag,LUB]=Con.ConstructXFlag(ListUnits, ListStreams)
    Con.Constraints(Xmeas,ListUnits,ListStreams)
    Con.DeconstructX(Xmeas,ListUnits,ListStreams)
    constraint_list = [{"type":"eq", "fun":Con.Constraints, "args":(ListUnits,ListStreams)}]
    #Opt=[{"maxiter":500,"disp":True}]
 
    result = minimize(Con.Objective, Xmeas, args=(Xmeas,XFlag),method='SLSQP', bounds=LUB, 
                       constraints=constraint_list,options={'disp':True})
    print result
#     print F.Flow,F.Conc[0],F.Conc[1]
#     print T.Flow,T.Conc[0],T.Conc[1]
#     print B.Flow,B.Conc[0],B.Conc[1]
