from fpdf import FPDF
from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
from scipy.optimize import minimize
import pyipopt
from numpy import float_
from numpy import exp

import Constraints as Con
from Streams.Readfile import Readfile
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Thermo.IdealGas import IdealGas
from Streams.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.Mixer import Mixer
from Units.Reactor import Reactor
from Units.EquilibriumReactor import EquilibriumReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Splitter import Splitter
from Units.ElementBalanceReactor import ElementBalanceReactor
from Units.AdiabaticElementBalanceReactor import AdiabaticElementBalanceReactor
from optim.ipopt import ipopt
from CommonFunctions.Report import Report
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from Thermo.Refprop import Refprop

if __name__=="__main__":
    
    '------------------ Reading the Measurement file--------------------'
    #str1="C:\\Users\\admin\\workspace\\RAGE2\\src//NPLMeas.dat"
    str1="D:\\Gyandata\\PythonRage\\RAGE3\\src//NPLMeas.dat"
    R1=Readfile(str1)
    '-----------------------Creating Objects--------------------------------------------'   
    
    '''Defining Components '''
    N2=Comp(8,StdState=2)
    H2=Comp(4,StdState=2)
    O2=Comp(6,StdState=2)
    CH4=Comp(5,StdState=2)
    C2H6=Comp(3,StdState=2)
    C3H8=Comp(9,StdState=2)
    CO=Comp(1,StdState=2)
    CO2=Comp(2,StdState=2)
    H2O=Comp(7,StdState=2)
#     nC4H10=Comp(18,StdState=2)
#     iC4H10=Comp(19,StdState=2)
#     nC5H12=Comp(20,StdState=1)
#     iC5H12=Comp(21,StdState=1)
#     CO=Comp(5,StdState=2)
#     CO2=Comp(4,StdState=2)
#     H2O=Comp(15,StdState=1)
    
    '''Defining Thermo object '''
    
    T1=Refprop([N2,H2,O2,CH4,C2H6,C3H8,CO,CO2,H2O])#,nC4H10,iC4H10,nC5H12,iC5H12,CO,CO2,H2O])
#     T1=IdealGas([N2,H2,CH4,C2H6,C3H8],'Refprop.dat')
    
    '''Stream NG1(1) Natural gas from GAIL'''
    FI4133=Sensor('FI4133',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4140=Sensor('TI4140',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4107=Sensor('PI4107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:0.9371222,N2:0.0041252,C2H6:0.0447413,C3H8:0.0140113}
    StrmNG1=FixedConcStream('StrmNG1',FI4133,TI4140,PI4107,2,T1,CTag,'xfrac')
    
    '''Defining Stream NG2(11) Fuel to Furnace'''
    FI4131=Sensor('FI4131',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG2=Sensor('TU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG2=Sensor('PU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG2=Sensor('CH4_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG2=Sensor('N2_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG2=Sensor('C2H6_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG2=Sensor('C3H8_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag1={CH4:CH4_NG2,N2:N2_NG2,C2H6:C2H6_NG2,C3H8:C3H8_NG2}
    StrmNG2=Material_Stream('StrmNG2',FI4131,TU_NG2,PU_NG2,2,T1,CTag1)
    
    ''' Defining Stream NG3 (3) NG to Desulphurization uint'''
    FI4132=Sensor('FI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG3=Sensor('TU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG3=Sensor('PU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG3=Sensor('CH4_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG3=Sensor('N2_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG3=Sensor('C2H6_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG3=Sensor('C3H8_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={CH4:CH4_NG3,N2:N2_NG3,C2H6:C2H6_NG3,C3H8:C3H8_NG3}
    StrmNG3=Material_Stream('StrmNG3',FI4132,TU_NG3,PU_NG3,2,T1,CTag2)
    
    ''' Defining Splitter SPL1'''
    SPL1=Splitter('SPL1',StrmNG1,[StrmNG2,StrmNG3])
    
    '''Defining Stream H1 (12)'''
    FIC3103=Sensor('FIC3103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3156=Sensor('TI3156',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3150=Sensor('PIC3150',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:1}
    StrmH1=FixedConcStream('StrmH1',FIC3103,TI3156,PIC3150,2,T1,CTag,'xfrac')
    
    ''' Defining Stream NG4 (4) Cold side inlet of heat exchanger E-2'''
    FU_NG4=Sensor('FU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG4=Sensor('TU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG4=Sensor('PU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG4=Sensor('CH4_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG4=Sensor('N2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG4=Sensor('C2H6_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG4=Sensor('C3H8_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG4=Sensor('H2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_NG4,CH4:CH4_NG4,N2:N2_NG4,C2H6:C2H6_NG4,C3H8:C3H8_NG4}
    StrmNG4=Material_Stream('StrmNG4',FU_NG4,TU_NG4,PU_NG4,2,T1,CTag2)
    
    '''Defining Mix1'''
    MIX1=Mixer('MIX1',[StrmNG3,StrmH1],StrmNG4)
    
    ''' Defining a Stream NG5 (5) Cold side outlet of heat exchanger E-2'''
    FIC3105=Sensor('FIC3105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC4101=Sensor('TIC4101',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3112=Sensor('PIC3112',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG5=Sensor('CH4_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG5=Sensor('N2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG5=Sensor('C2H6_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG5=Sensor('C3H8_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG5=Sensor('H2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_NG5,CH4:CH4_NG5,N2:N2_NG5,C2H6:C2H6_NG5,C3H8:C3H8_NG5}
    StrmNG5=Material_Stream('StrmNG5',FIC3105,TIC4101,PIC3112,2,T1,CTag2)
    
    '''Defining Stream HT1 (23) Hot side inlet of heat exchanger E-2'''
    FU_HT1=Sensor('FU_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4181=Sensor('TI4181',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT1=Sensor('PU_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT1=Sensor('H2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT1=Sensor('CH4_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT1=Sensor('CO_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT1=Sensor('CO2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT1=Sensor('H2O_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_HT1=Sensor('N2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_HT1,CH4:CH4_HT1,CO:CO_HT1,CO2:CO2_HT1,H2O:H2O_HT1,N2:N2_HT1}
    StrmHT1=Material_Stream('StrmHT1',FU_HT1,TI4181,PU_HT1,2,T1,CTag2)
    
    '''Defining Stream HT2(24) Hotside outlet of heat exchanger E-2 and hotside inlet of Exchanger E-16'''
    FU_HT2=Sensor('FU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_HT2=Sensor('TU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT2=Sensor('PU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT2=Sensor('H2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT2=Sensor('CH4_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT2=Sensor('CO_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT2=Sensor('CO2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT2=Sensor('H2O_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_HT2=Sensor('N2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_HT2,CH4:CH4_HT2,CO:CO_HT2,CO2:CO2_HT2,H2O:H2O_HT2,N2:N2_HT2}
    StrmHT2=Material_Stream('StrmHT2',FU_HT2,TU_HT2,PU_HT2,2,T1,CTag2)
    
    '''Defining Heat Exchanger HEX1'''
    HEX1=HeatExchanger('HEX1',StrmHT1,StrmHT2,StrmNG4,StrmNG5,Type=1)
    
    '''Defining Stream ST1 (19) steam mixed with NG before pre-reformer'''
    FIC3104=Sensor('FIC3104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123a=Sensor('TIC3123a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116a=Sensor('PI3116a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST1=FixedConcStream('StrmST1',FIC3104,TIC3123a,PI3116a,2,T1,CTag,'xfrac')
    
    '''Defining Stream NS1 (6-I) inlet to the Heater1 which is before pre-reformer'''
    FU_NS1=Sensor('FU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4169=Sensor('TI4169',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS1=Sensor('PU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS1=Sensor('H2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS1=Sensor('CH4_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS1=Sensor('H2O_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS1=Sensor('N2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS1=Sensor('C2H6_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS1=Sensor('C3H8_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS1,CH4:CH4_NS1,H2O:H2O_NS1,N2:N2_NS1,C2H6:C2H6_NS1,C3H8:C3H8_NS1}
    StrmNS1=Material_Stream('StrmNS1',FU_NS1,TI4169,PU_NS1,2,T1,CTag)
    
    ''' Defining MIX2 (D-10)'''
    MIX2=Mixer('MIX2',[StrmNG5,StrmST1],StrmNS1)
    
    '''Defining Energy Stream E1'''
    E1=Energy_Stream('E1',100)
    
    ''' Defining Stream NS2(6) (PreReformer Inlet)'''
    FU_NS2=Sensor('FU_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TRC4167=Sensor('TRC4167',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4103=Sensor('PI4103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2=Sensor('H2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2=Sensor('CH4_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2=Sensor('H2O_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2=Sensor('N2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2=Sensor('C2H6_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2=Sensor('C3H8_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS2,CH4:CH4_NS2,H2O:H2O_NS2,N2:N2_NS2,C2H6:C2H6_NS2,C3H8:C3H8_NS2}
    StrmNS2=Material_Stream('StrmNS2',FU_NS2,TRC4167,PI4103,2,T1,CTag)
    
    ''' Defining Heat1'''
    HEAT1=Heater('HEAT1',StrmNS1,StrmNS2,E1,1)
    
    '''Defining Stream NS3(7) (PreReformer outlet)'''
    FU_NS3=Sensor('FU_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3119=Sensor('TI3119',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4132=Sensor('PI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS3=Sensor('H2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS3=Sensor('CH4_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS3=Sensor('H2O_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS3=Sensor('N2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS3=Sensor('CO_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS3=Sensor('CO2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS3,CH4:CH4_NS3,H2O:H2O_NS3,N2:N2_NS3,CO:CO_NS3,CO2:CO2_NS3}
    StrmNS3=Material_Stream('StrmNS3',FU_NS3,TI3119,PI4132,2,T1,CTag)
    
    ''' Defining Energy Stream E2. E2 is not included in the list of streams as E2.Q not to be part of X'''
    E2=Energy_Stream('E2',0)
    E2.Q.Flag=2
    
    '''Definig REX1 (PreReformer)'''
    REX1=ElementBalanceReactor('REX1',StrmNS2,StrmNS3,[E2],ExoEndoFlag=-1)
    #REX1=AdiabaticElementBalanceReactor('REX1',StrmNS2,StrmNS3)
    
    '''Defining Streams ST2(18) Steam being mixed with pre reformer outlet'''
    FIC3107=Sensor('FIC3107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123b=Sensor('TIC3123b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116b=Sensor('PI3116b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST2=FixedConcStream('StrmST2',FIC3107,TIC3123b,PI3116b,2,T1,CTag,'xfrac')
    
    ''' Defining Stream NS4 (8) Feed to heater2'''
    FU_NS4=Sensor('FU_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS4=Sensor('TU_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS4=Sensor('PU_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS4=Sensor('H2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS4=Sensor('CH4_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS4=Sensor('H2O_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS4=Sensor('N2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS4=Sensor('CO_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS4=Sensor('CO2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS4,CH4:CH4_NS4,H2O:H2O_NS4,N2:N2_NS4,CO:CO_NS4,CO2:CO2_NS4}
    StrmNS4=Material_Stream('StrmNS4',FU_NS4,TU_NS4,PU_NS4,2,T1,CTag)
    
    ''' Defining Mixer MIX3'''
    MIX3=Mixer('MIX3',[StrmNS3,StrmST2],StrmNS4)
    
    '''Defining Stream NS5 (9) Feed to Steam Reformer'''
    FU_NS5=Sensor('FU_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3124=Sensor('TIC3124',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3117=Sensor('PI3117',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5=Sensor('H2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5=Sensor('CH4_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5=Sensor('H2O_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5=Sensor('N2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5=Sensor('CO_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5=Sensor('CO2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5,CH4:CH4_NS5,H2O:H2O_NS5,N2:N2_NS5,CO:CO_NS5,CO2:CO2_NS5}
    StrmNS5=Material_Stream('StrmNS5',FU_NS5,TIC3124,PI3117,2,T1,CTag)
    
    '''Defining Energy Stream E3'''
    E3=Energy_Stream('E3',600000)
    
    '''Defining Heater HEAT2'''
    HEAT2=Heater('HEAT2',StrmNS4,StrmNS5,E3,1)
    
    '''Defining Stream NS6 (10) Outlet of Stream Reformer'''
    FU_NS6=Sensor('FU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3132=Sensor('TI3132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS6=Sensor('PU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS6=Sensor('H2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS6=Sensor('CH4_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS6=Sensor('H2O_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS6=Sensor('N2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS6=Sensor('CO_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS6=Sensor('CO2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS6,CH4:CH4_NS6,H2O:H2O_NS6,N2:N2_NS6,CO:CO_NS6,CO2:CO2_NS6}
    StrmNS6=Material_Stream('StrmNS6',FU_NS6,TI3132,PU_NS6,2,T1,CTag)
    
    '''Defining Energy Stream E4'''
    E4=Energy_Stream('E4',600000)
    
    '''Defining REX2 (Steam Reformer) '''
    REX2=ElementBalanceReactor('REX2',StrmNS5,StrmNS6,[E4],ExoEndoFlag=1)
    
    '''Defining Stream NS7 (22) Inlet to HT shift Reactor'''
    FU_NS7=Sensor('FU_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS7=Sensor('TU_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3129=Sensor('PI3129',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS7=Sensor('H2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS7=Sensor('CH4_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS7=Sensor('H2O_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS7=Sensor('N2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS7=Sensor('CO_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS7=Sensor('CO2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS7,CH4:CH4_NS7,H2O:H2O_NS7,N2:N2_NS7,CO:CO_NS7,CO2:CO2_NS7}
    StrmNS7=Material_Stream('StrmNS7',FU_NS7,TU_NS7,PI3129,2,T1,CTag)
    
    ''' Defining Stream W1 (Feed water to RG Boiler)'''
    FI4110=Sensor('FI4110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W1=Sensor('TU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W1=Sensor('PU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW1=FixedConcStream('StrmW1',FI4110,TU_W1,PU_W1,1,T1,CTag,'xfrac')
    
    '''Defining Stream ST3 (Steam from RG Boiler)'''
    FU_ST3=Sensor('FU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST3=Sensor('TU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST3=Sensor('PU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST3=FixedConcStream('StrmST3',FU_ST3,TU_ST3,PU_ST3,2,T1,CTag,'xfrac')
    
    '''Defining Heat Exchanger HEX2 (E-1) RG Boiler'''
    HEX2=HeatExchanger('HEX2',StrmNS6,StrmNS7,StrmW1,StrmST3,Type=1)
    
    '''Defining Energy Stream E5'''
    E5=Energy_Stream('E5',0)
    E5.Q.Flag=2
    
    '''Defining REX3 (Adiabatic Reactor) (High Temperature Shift Reactor)'''
    REX3=ElementBalanceReactor('REX3',StrmNS7,StrmHT1,[E5],ExoEndoFlag=-1)
    
    '''Defining Stream HT3 (24A)'''
    FU_HT3=Sensor('FU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4172=Sensor('TI4172',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT3=Sensor('PU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT3=Sensor('H2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT3=Sensor('CH4_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT3=Sensor('CO_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT3=Sensor('CO2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT3=Sensor('H2O_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_HT3=Sensor('N2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_HT3,CH4:CH4_HT3,CO:CO_HT3,CO2:CO2_HT3,H2O:H2O_HT3,N2:N2_HT3}
    StrmHT3=Material_Stream('StrmHT3',FU_HT3,TI4172,PU_HT3,2,T1,CTag2)
    
    ''' Defining Stream W2'''
    FU_W2=Sensor('FU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W2=Sensor('TU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W2=Sensor('PU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW2=FixedConcStream('StrmW2',FU_W2,TU_W2,PU_W2,1,T1,CTag,'xfrac')
    
    ''' Defining Stream W3 (34)'''
    FU_W3=Sensor('FU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W3=Sensor('TU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W3=Sensor('PU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW3=FixedConcStream('StrmW3',FU_W3,TU_W3,PU_W3,1,T1,CTag,'xfrac')
    
    ''' Defining HEX3 (E16)'''
    HEX3=HeatExchanger('HEX3',StrmHT2,StrmHT3,StrmW2,StrmW3,Type=1)
    
    '''Defining Stream LT1 (24b)'''
    FU_LT1=Sensor('FU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT1=Sensor('TU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT1=Sensor('PU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT1=Sensor('H2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT1=Sensor('CH4_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT1=Sensor('CO_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT1=Sensor('CO2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_LT1=Sensor('H2O_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_LT1=Sensor('N2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT1,CH4:CH4_LT1,CO:CO_LT1,CO2:CO2_LT1,H2O:H2O_LT1,N2:N2_LT1}
    StrmLT1=Material_Stream('StrmLT1',FU_LT1,TU_LT1,PU_LT1,2,T1,CTag2)
    
    '''Defining Energy Stream E5'''
    E6=Energy_Stream('E6',0)
    E6.Q.Flag=2
    
    '''Defining REX4 (Low Temp Shift Reactor) '''
    REX4=ElementBalanceReactor('REX4',StrmHT3,StrmLT1,[E6],ExoEndoFlag=-1)
    
    '''Steam Circuit Starts'''
    
    ''' Defining Stream W4 (feed to steam drum or FG boiler)'''
    FI3110=Sensor('FI3110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W4=Sensor('TU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W4=Sensor('PU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW4=FixedConcStream('StrmW4',FI3110,TU_W4,PU_W4,1,T1,CTag,'xfrac')
    
    '''Defining Stream ST4(15)'''
    FU_ST4=Sensor('FU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST4=Sensor('TU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST4=Sensor('PU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST4=FixedConcStream('StrmST4',FU_ST4,TU_ST4,PU_ST4,2,T1,CTag,'xfrac')
    
    '''Defining the splitter that splits the boiler feed water into two streams one for RG boiler and the other for FG boiler or steam drum'''
    SPL3=Splitter('SPL3',StrmW3,[StrmW1,StrmW4])
    
    
    '''Defining Energy Stream E7'''
    E7=Energy_Stream('E7',200000)
    
    '''Defining Heater3 (Steam Drum)'''
    HEAT3=Heater('HEAT3',StrmW4,StrmST4,E7,1)
    
    '''Defining Stream ST5 (16) Export steam'''
    FI3106=Sensor('FI3106',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST5=Sensor('TU_ST5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3114=Sensor('PIC3114',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST5=FixedConcStream('StrmST5',FI3106,TU_ST5,PIC3114,2,T1,CTag,'xfrac')
    
    '''Defining Stream ST6(17)'''
    FU_ST6=Sensor('FU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST6=Sensor('TU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST6=Sensor('PU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST6=FixedConcStream('StrmST6',FU_ST6,TU_ST6,PU_ST6,2,T1,CTag,'xfrac')
    
    '''Defining Combined steam Stream from FG and RG boilers'''
    FU_ST8=Sensor('FU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST8=Sensor('TU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST8=Sensor('PU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST8=FixedConcStream('StrmST8',FU_ST8,TU_ST8,PU_ST8,2,T1,CTag,'xfrac')
    
    '''Defining splitter that splits the steam from combined steam from both boilers into two streams one sent to super heater and the other sent as export steam'''
    SPL4=Splitter('SPL4',StrmST8,[StrmST6,StrmST5])
    
    
    '''Defining Mixer that mixes Steam from RG boiler and FG boiler'''
    MIX4=Mixer('MIX4',[StrmST3,StrmST4],StrmST8)
                    
    #'''Defining Splitter SPL2'''
    #SPL2=Splitter('SPL2',StrmST4,[StrmST5,StrmST6])
    
    '''Defining Superheated steam ST7'''
    FU_ST7=Sensor('FU_ST7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3126=Sensor('TI3126',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST7=Sensor('PU_ST7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7=FixedConcStream('StrmST7',FU_ST7,TI3126,PU_ST7,2,T1,CTag,'xfrac')
    
    '''Defining Energy Stream E8'''
    E8=Energy_Stream('E8',200000)
    
    '''Defining Heater HEAT4 (SuperHeater) E-6-1'''
    HEAT4=Heater('HEAT4',StrmST6,StrmST7,E8,1)
    
    '''Defining Splitter SPL5 (Splitting the super heated steam into two streams, one being fed to the pre-reformer and the other to steam-reformer)'''
    SPL5=Splitter('SPL5',StrmST7,[StrmST1,StrmST2])
    
    '''Defining Air Stream AR1 (13)'''
    FU_AR1=Sensor('FU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AR1=Sensor('TU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR1=Sensor('PU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR1=FixedConcStream('StrmAR1',FU_AR1,TU_AR1,PU_AR1,2,T1,CTag,'xfrac')
    
    '''Defining Air Stream AR2 (14)'''
    FU_AR2=Sensor('FU_AR2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AR2=Sensor('TU_AR2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR2=Sensor('PU_AR2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR2=FixedConcStream('StrmAR2',FU_AR2,TU_AR2,PU_AR2,2,T1,CTag,'xfrac')
    
    '''Defining Energy Stream E9''' 
    E9=Energy_Stream('E9',200000)
    
    '''Defining HEAT5 (Air Preheater) (E-9)'''
    HEAT5=Heater('HEAT5',StrmAR1,StrmAR2,E9,1)
    
    '''Defining Stream Air-Natural Gas Mixture'''
    FU_AN1=Sensor('FU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AN1=Sensor('TU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AN1=Sensor('PU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_AN1=Sensor('CH4_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_AN1=Sensor('N2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_AN1=Sensor('C2H6_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_AN1=Sensor('C3H8_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    O2_AN1=Sensor('O2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:CH4_AN1,N2:N2_AN1,C2H6:C2H6_AN1,C3H8:C3H8_AN1,O2:O2_AN1}
    StrmAN1=Material_Stream('StrmAN1',FU_AN1,TU_AN1,PU_AN1,2,T1,CTag)
        
    '''Defining MIX5 (Air fuel mixing)'''
    MIX5=Mixer('MIX5',[StrmAR2,StrmNG2],StrmAN1)
    
    '''Defining Flue gas Stream (20)'''
    FU_FG1=Sensor('FU_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3121=Sensor('TI3121',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3137=Sensor('PIC3137',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_FG1=Sensor('CO2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_FG1=Sensor('H2O_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_FG1=Sensor('N2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    O2_FG1=Sensor('O2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CO2:CO2_FG1,H2O:H2O_FG1,N2:N2_FG1,O2:O2_FG1}
    StrmFG1=Material_Stream('StrmFG1',FU_FG1,TI3121,PIC3137,2,T1,CTag)
    
    '''Defining Furnace'''
    REX5=ElementBalanceReactor('REX5',StrmAN1,StrmFG1,[E1,E3,E4,E7,E8,E9],ExoEndoFlag=-1)   
    
    ListUints=[MIX1,SPL1,HEX1,MIX2,HEAT1,REX1,MIX3,HEAT2,REX2,HEX2,REX3,HEX3,REX4,HEAT3,HEAT4,HEAT5,MIX4,REX5,SPL3,SPL4,SPL5,MIX5]
    ListStreams=[StrmNG1,StrmNG2,StrmNG3,StrmH1,StrmNG4,StrmNG5,StrmHT1,StrmHT2,StrmST1,StrmNS1,E1,StrmNS2,StrmNS3,E2,StrmNS4,StrmST2,StrmNS5,E3,E4,StrmNS6,StrmNS7,StrmST3,StrmW1,E5,StrmHT3,StrmW2,StrmW3,StrmLT1,E6,StrmST4,E7,StrmST5,StrmST6,StrmST7,E8,StrmAR1,StrmAR2,E9,StrmAN1,StrmFG1,StrmW4,StrmST8]#,B,B1]
#     ListUints=[MIX1]
#     ListStreams=[StrmNG3,StrmH1,StrmNG4]#,B,B1]
#     for i in StrmHT1.CTag.keys():
#         print i.Name
    ToInternalUnits(ListStreams)
    opt1=ipopt(ListStreams,ListUints,7,6,1e-4)
    #ToExternalUnits(ListStreams)
     
    for i in ListUints:
        print i.MaterialBalRes(),i.ComponentBalRes(),i.EnergyBalRes(),i.PressureBalRes()
    for i in ListStreams:
        if (isinstance(i,Energy_Stream)):
            print i.Q.Meas,'\t',i.Q.Est
        else:
            print i.FTag.Tag,'\t', i.FTag.Meas,'\t', i.FTag.Est
            print i.TTag.Tag, '\t',i.TTag.Meas,'\t', i.TTag.Est
            print i.PTag.Tag,'\t', i.PTag.Meas, '\t',i.PTag.Est
            for j in i.CTag.keys():
                print i.CTag[j].Tag,'\t', i.CTag[j].Meas,'\t', i.CTag[j].Est
    Report(ListUints)
#     print '============================='
#     for i in range(len(R1.Name)):
#         print R1.Name[i],R1.Meas[i],R1.Sigma[i],R1.Flag[i],R1.Unit[i]