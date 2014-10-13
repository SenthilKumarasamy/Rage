#import REFPROP2 as ref
from Streams.Comp import Comp
from Streams.Material_Stream import Material_Stream
from Streams.Reaction import Reaction
from Streams.Energy_Stream import Energy_Stream
from Units.Reactor import Reactor
from Streams.Therm import Therm
from Units.EquilibriumReactor import EquilibriumReactor
from Units.Heater import Heater
import ConstructionX as conx
import Constraints as Cons

CH4=Comp(48)
O2=Comp(64)
CO2=Comp(16)
H2O=Comp(110)
N2=Comp(60)

CL=[CH4,O2,CO2,H2O,N2]
Therm1=Therm(CL,0,0,200+273.16,101.325)

# Therm1.StdState_And_StdH_Of_Comp(CH4)
# Therm1.StdState_And_StdH_Of_Comp(O2)
# Therm1.StdState_And_StdH_Of_Comp(N2)
# Therm1.StdState_And_StdH_Of_Comp(CO2)
# Therm1.StdState_And_StdH_Of_Comp(H2O)

#print CH4.StdState,O2.StdState,CO2.StdState,H2O.StdState
#print CH4.StdH,O2.StdH,CO2.StdH,H2O.StdH
#print CH4.StdS,O2.StdS,CO2.StdS,H2O.StdS



c1=[0.2,0.7,0.1]
c2=['CT104','CT105','CT106','CT107','CT108']
Pstrm1=Material_Stream(41,300.0,101.325,2,Therm1,[CH4,O2,N2,CO2,H2O],c2)
#Therm1.H_Material_Stream(Pstrm1)
#Rstrm1=Material_Stream('FT102','TT102','PT102',2,[CH4,O2,N2],c1,)
Rstrm1=Material_Stream('FT102','TT102','PT102',2,Therm1,[CH4,O2,N2],c1)
Rstrm2=Material_Stream('FT102','TT102','PT102',2,Therm1,[CH4,O2,N2],c1)
Es=Energy_Stream(100)
Hex=Heater(Rstrm1,Rstrm2,Es)
Hex.Residual()
#print Hex.Resid
 
Reaction1=Reaction([CH4,O2,CO2,H2O],[-1,-2,1,2],-891,-50)
# 
Reactor1=EquilibriumReactor(Rstrm1,Pstrm1,[Es],[Reaction1])
Reactor1.Residual()
Reactor1.Residual()

LU=[Reactor1,Hex]
LS=[Rstrm1,Rstrm2,Pstrm1,Es]
L=conx.ConstructX(LU, LS)
XFlag=conx.ConstructXFlag(LU,LS)
j=conx.DeconstructX(L,LU,LS)

Res=Cons.Constraints(L, LU, LS)
obj=Cons.Objective(L, L, XFlag)
print obj

# Reactor1.Residual()
# print Reactor1.dhRxnInlet
# print Reactor1.Resid
#print Reactor1.K
 
#===============================================================================
# c2=[Comp(6),Comp(7),Comp(8)]  
# sm1=Material_Stream('FT100','TT100','PT100',c2[0])
# sm2=Material_Stream('FT101','TT101','PT101',c2[0])
# sm3=Material_Stream('FT102','TT102','PT102',c2[1])
# sm4=Material_Stream('FT103','TT103','PT103',c2[1])
# sm3=strm.Material_Stream('FT102','TT102','PT102',c2[2])
# sm1.h=200.0
# sm2.h=100.0
# sm3.h=50.0
# sm4.h=45.0
# Hex=HeatExchanger(sm1,sm2,sm3,sm4,300,500,2)
# Hex.Residual()
# print Hex.Resid
# c1=['CT101','CT102','CT103']
# smc=strm.Material_Stream('FT103','TT103','PT103',c1,c2)
# smc.h=300.0
# Mixer_input=[sm1,sm2,sm3]
# Mix1=unt.Splitter(smc,Mixer_input)
# Mix1.Residual()
# print Mix1.Resid
#===============================================================================
