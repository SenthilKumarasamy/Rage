from fpdf import FPDF
from numpy import inf
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import asarray
from scipy.optimize import minimize
import pyipopt
from optim.myslsqp import myslsqp
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
from Units.HeaterVaporizer import HeaterVaporizer
from Units.Mixer import Mixer
from Units.Reactor import Reactor
from Units.EquilibriumReactor import EquilibriumReactor
from Units.EquilibriumReactor2 import EquilibriumReactor2
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Splitter import Splitter
from Units.ElementBalanceReactor import ElementBalanceReactor
from Units.HeatExchangerVaporizer import HeatExchangerVaporizer
from optim.ipopt import ipopt
from CommonFunctions.Report import Report
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from Thermo.Refprop import Refprop

if __name__=="__main__":
    
    '------------------ Reading the Measurement file--------------------'
    #str1="C:\\Users\\admin\\workspace\\RAGE//NPLMeas1.dat"
    str1="D:\\Gyandata\\PythonRage\\RAGE2\\RAGE\\NPL_all_Meas.dat"
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
    
    '''Defining Thermo object '''
    
    T1=Refprop([H2,O2,CH4,CO,CO2,H2O,N2])
#     T1=IdealGas([N2,H2,CH4,C2H6,C3H8],'Refprop.dat')

    ListStreams=[]
    ListUnits=[]
    
    '''Stream NG1(1) Natural gas from GAIL'''
    FI4130=Sensor('FI4130',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4140=Sensor('TI4140',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4107=Sensor('PI4107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:1}
    StrmNG1=FixedConcStream('StrmNG1',FI4130,TI4140,PI4107,2,T1,CTag,'xfrac')
    ListStreams.append(StrmNG1)
                         
    '''Defining Stream NG2(11) Fuel to Furnace'''
    FI4131=Sensor('FI4131',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG2=Sensor('TU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG2=Sensor('PU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:1}
    StrmNG2=FixedConcStream('StrmNG2',FI4131,TU_NG2,PU_NG2,2,T1,CTag,'xfrac')
    ListStreams.append(StrmNG2)
                       
    ''' Defining Stream NG3 (3) NG to Desulphurization uint'''
    FI4132=Sensor('FI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG3=Sensor('TU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG3=Sensor('PU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:1}
    StrmNG3=FixedConcStream('StrmNG3',FI4132,TU_NG3,PU_NG3,2,T1,CTag,'xfrac')
    ListStreams.append(StrmNG3)
                        
    ''' Defining Splitter SPL1'''
    SPL1=Splitter('SPL1',StrmNG1,[StrmNG2,StrmNG3])
    ListUnits.append(SPL1)
             
    '''Defining Stream NG2a(11) Fuel to Furnace'''
    FU_NG2a=Sensor('FU_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG2a=Sensor('TU_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC4116=Sensor('PIC4116',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:1}
    StrmNG2a=FixedConcStream('StrmNG2a',FU_NG2a,TU_NG2a,PIC4116,2,T1,CTag,'xfrac')
    ListStreams.append(StrmNG2a)
               
    ''' Defining Splitter SPL1'''
    SPL1a=Splitter('SPL1a',StrmNG2,[StrmNG2a],dp=[3100])
    ListUnits.append(SPL1a)
              
              
                        
    '''Defining Stream H1 (12)'''
    FIC3103=Sensor('FIC3103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3156=Sensor('TI3156',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3150=Sensor('PIC3150',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_H1=Sensor('H2_H1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_H1=Sensor('CH4_H1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_H1=Sensor('CO_H1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_H1=Sensor('CO2_H1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_H1,CH4:CH4_H1,CO:CO_H1,CO2:CO2_H1}
    StrmH1=Material_Stream('StrmH1',FIC3103,TI3156,PIC3150,2,T1,CTag2)
#     CTag={H2:1}
#     StrmH1=FixedConcStream('StrmH1',FIC3103,TI3156,PIC3150,2,T1,CTag,'xfrac')
    ListStreams.append(StrmH1)
                             
    ''' Defining Stream NG4 (4) Cold side inlet of heat exchanger E-2'''
    FU_NG4=Sensor('FU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG4=Sensor('TU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG4=Sensor('PU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG4=Sensor('CH4_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG4=Sensor('H2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NG4=Sensor('CO_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG4=Sensor('CO2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NG4,CH4:CH4_NG4,CO:CO_NG4,CO2:CO2_NG4}
    StrmNG4=Material_Stream('StrmNG4',FU_NG4,TU_NG4,PU_NG4,2,T1,CTag)
    ListStreams.append(StrmNG4)
                             
    '''Defining Mix1'''
    MIX1=Mixer('MIX1',[StrmNG3,StrmH1],StrmNG4)
    ListUnits.append(MIX1)
                           
    ''' Defining a Stream NG5 (5) Cold side outlet of heat exchanger E-2'''
    FIC3105=Sensor('FIC3105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC4101=Sensor('TIC4101',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3112=Sensor('PIC3112',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG5=Sensor('CH4_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG5=Sensor('H2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NG5=Sensor('CO_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG5=Sensor('CO2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NG5,CH4:CH4_NG5,CO:CO_NG5,CO2:CO2_NG5}
    StrmNG5=Material_Stream('StrmNG5',FIC3105,TIC4101,PIC3112,2,T1,CTag)
    ListStreams.append(StrmNG5)
                            
    '''Defining Stream HT1 (23) Hot side inlet of heat exchanger E-2'''
    FU_HT1=Sensor('FU_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4181=Sensor('TI4181',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT1=Sensor('PU_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT1=Sensor('H2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT1=Sensor('CH4_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT1=Sensor('CO_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT1=Sensor('CO2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT1=Sensor('H2O_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_HT1,CH4:CH4_HT1,CO:CO_HT1,CO2:CO2_HT1,H2O:H2O_HT1}
    StrmHT1=Material_Stream('StrmHT1',FU_HT1,TI4181,PU_HT1,2,T1,CTag)
    ListStreams.append(StrmHT1)
                            
    '''Defining Stream HT2(24) Hotside outlet of heat exchanger E-2 and hotside inlet of Exchanger E-16'''
    FU_HT2=Sensor('FU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_HT2=Sensor('TU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT2=Sensor('PU_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT2=Sensor('H2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT2=Sensor('CH4_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT2=Sensor('CO_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT2=Sensor('CO2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT2=Sensor('H2O_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_HT2,CH4:CH4_HT2,CO:CO_HT2,CO2:CO2_HT2,H2O:H2O_HT2}
    StrmHT2=Material_Stream('StrmHT2',FU_HT2,TU_HT2,PU_HT2,2,T1,CTag)
    ListStreams.append(StrmHT2)
                             
    '''Defining Heat Exchanger HEX1'''
    HEX1=HeatExchanger('HEX1',StrmHT1,StrmHT2,StrmNG4,StrmNG5,Type=0)
    ListUnits.append(HEX1)
                        
    '''Defining Stream ST1 (19) steam mixed with NG before pre-reformer'''
    FIC3104=Sensor('FIC3104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123a=Sensor('TIC3123a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116a=Sensor('PI3116a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST1=FixedConcStream('StrmST1',FIC3104,TIC3123a,PI3116a,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST1)
                          
    '''Defining Stream NS1 (6-I) inlet to the Heater1 which is before pre-reformer'''
    FU_NS1=Sensor('FU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4169=Sensor('TI4169',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS1=Sensor('PU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS1=Sensor('H2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS1=Sensor('CH4_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS1=Sensor('H2O_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS1=Sensor('CO_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS1=Sensor('CO2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS1,CH4:CH4_NS1,H2O:H2O_NS1,CO:CO_NS1,CO2:CO2_NS1}
    StrmNS1=Material_Stream('StrmNS1',FU_NS1,TI4169,PU_NS1,2,T1,CTag)
    ListStreams.append(StrmNS1)
                          
    ''' Defining MIX2 (D-10)'''
    MIX2=Mixer('MIX2',[StrmNG5,StrmST1],StrmNS1)
    ListUnits.append(MIX2)
                     
    '''Defining Energy Stream E1'''
    E1=Energy_Stream('E1',14766496)
    ListStreams.append(E1)
                    
    ''' Defining Stream NS2(6) (PreReformer Inlet)'''
    FU_NS2=Sensor('FU_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TRC4167=Sensor('TRC4167',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4103=Sensor('PI4103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2=Sensor('H2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2=Sensor('CH4_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2=Sensor('H2O_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS2=Sensor('CO_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2=Sensor('CO2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS2,CH4:CH4_NS2,H2O:H2O_NS2,CO:CO_NS2,CO2:CO2_NS2}
    StrmNS2=Material_Stream('StrmNS2',FU_NS2,TRC4167,PI4103,2,T1,CTag)
    ListStreams.append(StrmNS2)
                    
    ''' Defining Heat1'''
    HEAT1=Heater('HEAT1',StrmNS1,StrmNS2,E1,1,Dp=300)
    ListUnits.append(HEAT1)
                 
    '''Defining Stream NS3(7) (PreReformer outlet)'''
    FU_NS3=Sensor('FU_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3119=Sensor('TI3119',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4132=Sensor('PI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS3=Sensor('H2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS3=Sensor('CH4_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS3=Sensor('H2O_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS3=Sensor('CO_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS3=Sensor('CO2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS3,CH4:CH4_NS3,H2O:H2O_NS3,CO:CO_NS3,CO2:CO2_NS3}
    StrmNS3=Material_Stream('StrmNS3',FU_NS3,TI3119,PI4132,2,T1,CTag)
    ListStreams.append(StrmNS3)
                 
    ''' Defining Energy Stream E2. E2 is not included in the list of streams as E2.Q not to be part of X'''
    E2=Energy_Stream('E2',0)
    E2.Q.Flag=2
    ListStreams.append(E2)
             
    '''Defining reactions'''
    RE1=Reaction('RE1',[CH4,H2O,CO,H2],[-1,-1,1,3])
    RE2=Reaction('RE2',[CH4,H2O,CO2,H2],[-1,-2,1,4])
    RE3=Reaction('RE3',[CO,H2O,CO2,H2],[-1,-1,1,1])
    RE4=Reaction('RE4',[CH4,O2,CO2,H2O],[-1,-2,1,2])
                 
    '''Definig REX1 (PreReformer)'''
    #REX1=EquilibriumReactor('REX1',StrmNS2,StrmNS3,[E2],[RE1,RE2],ExoEndoFlag=1)
    #REX1=Reactor('REX1',StrmNS2,StrmNS3,[E2],[RE1,RE2],ExoEndoFlag=1)
    REX1=ElementBalanceReactor('REX1',StrmNS2,StrmNS3,[E2],ExoEndoFlag=1)
    ListUnits.append(REX1)
                 
    '''Defining Streams ST2(18) Steam being mixed with pre reformer outlet'''
    FIC3107=Sensor('FIC3107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123b=Sensor('TIC3123b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116b=Sensor('PI3116b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST2=FixedConcStream('StrmST2',FIC3107,TIC3123b,PI3116b,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST2)
                      
    ''' Defining Stream NS4 (8) Feed to heater2'''
    FU_NS4=Sensor('FU_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS4=Sensor('TU_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS4=Sensor('PU_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS4=Sensor('H2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS4=Sensor('CH4_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS4=Sensor('H2O_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS4=Sensor('CO_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS4=Sensor('CO2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS4,CH4:CH4_NS4,H2O:H2O_NS4,CO:CO_NS4,CO2:CO2_NS4}
    StrmNS4=Material_Stream('StrmNS4',FU_NS4,TU_NS4,PU_NS4,2,T1,CTag)
    ListStreams.append(StrmNS4)
                      
    ''' Defining Mixer MIX3'''
    MIX3=Mixer('MIX3',[StrmNS3,StrmST2],StrmNS4)
    ListUnits.append(MIX3)
                      
    '''Defining Stream NS5 (9) Feed to Steam Reformer'''
    FU_NS5=Sensor('FU_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3124=Sensor('TIC3124',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3117=Sensor('PI3117',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5=Sensor('H2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5=Sensor('CH4_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5=Sensor('H2O_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5=Sensor('CO_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5=Sensor('CO2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5,CH4:CH4_NS5,H2O:H2O_NS5,CO:CO_NS5,CO2:CO2_NS5}
    StrmNS5=Material_Stream('StrmNS5',FU_NS5,TIC3124,PI3117,2,T1,CTag)
    ListStreams.append(StrmNS5)
                      
    '''Defining Energy Stream E3'''
    E3=Energy_Stream('E3',600000)
    ListStreams.append(E3)
                      
    '''Defining Heater HEAT2'''
    HEAT2=Heater('HEAT2',StrmNS4,StrmNS5,E3,1)
    ListUnits.append(HEAT2)
                      
    '''Defining Stream NS6 (10) Outlet of Stream Reformer'''
    FU_NS6=Sensor('FU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3132=Sensor('TI3132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS6=Sensor('PU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS6=Sensor('H2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS6=Sensor('CH4_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS6=Sensor('H2O_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS6=Sensor('CO_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS6=Sensor('CO2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS6,CH4:CH4_NS6,H2O:H2O_NS6,CO:CO_NS6,CO2:CO2_NS6}
    StrmNS6=Material_Stream('StrmNS6',FU_NS6,TI3132,PU_NS6,2,T1,CTag)
    ListStreams.append(StrmNS6)
                      
    '''Defining Energy Stream E4'''
    E4=Energy_Stream('E4',600000)
    ListStreams.append(E4)
                      
    '''Defining REX2 (Steam Reformer) '''
    REX2=ElementBalanceReactor('REX2',StrmNS5,StrmNS6,[E4],ExoEndoFlag=1)
    #REX2=EquilibriumReactor('REX2',StrmNS5,StrmNS6,[E4],[RE1],ExoEndoFlag=1)
    #REX2=Reactor('REX2',StrmNS5,StrmNS6,[E4],[RE1],ExoEndoFlag=1)
    ListUnits.append(REX2)
                   
    '''Defining Stream NS7 (22) Inlet to HT shift Reactor'''
    FU_NS7=Sensor('FU_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS7=Sensor('TU_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3129=Sensor('PI3129',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS7=Sensor('H2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS7=Sensor('CH4_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS7=Sensor('H2O_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS7=Sensor('CO_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS7=Sensor('CO2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS7,CH4:CH4_NS7,H2O:H2O_NS7,CO:CO_NS7,CO2:CO2_NS7}
    StrmNS7=Material_Stream('StrmNS7',FU_NS7,TU_NS7,PI3129,2,T1,CTag)
    ListStreams.append(StrmNS7)
                       
    ''' Defining Stream W1 (Feed water to RG Boiler)'''
    FI4110=Sensor('FI4110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W1=Sensor('TU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W1=Sensor('PU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW1=FixedConcStream('StrmW1',FI4110,TU_W1,PU_W1,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW1)
                         
    '''Defining Stream ST3 (Steam from RG Boiler)'''
    FU_ST3=Sensor('FU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST3=Sensor('TU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST3=Sensor('PU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST3=FixedConcStream('StrmST3',FU_ST3,TU_ST3,PU_ST3,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST3)
                         
    '''Defining Heat Exchanger HEX2 (E-1) RG Boiler'''
    HEX2=HeatExchanger('HEX2',StrmNS6,StrmNS7,StrmW1,StrmST3,Type=0)
#     HEX2=HeatExchangerVaporizer('HEX2',StrmNS6,StrmNS7,StrmW1,StrmST3,Type=0)
    ListUnits.append(HEX2)
                    
    '''Defining Energy Stream E5'''
    E5=Energy_Stream('E5',0)
    E5.Q.Flag=2
    ListStreams.append(E5)
                    
    '''Defining REX3 (Adiabatic Reactor) (High Temperature Shift Reactor)'''
    REX3=ElementBalanceReactor('REX3',StrmNS7,StrmHT1,[E5],ExoEndoFlag=-1)
    #REX3=Reactor('REX3',StrmNS7,StrmHT1,[E5],[RE3],ExoEndoFlag=-1)
    #REX3=EquilibriumReactor('REX3',StrmNS7,StrmHT1,[E5],[RE2],ExoEndoFlag=-1)
    ListUnits.append(REX3)
                   
    '''Defining Stream HT3 (24A)'''
    FU_HT3=Sensor('FU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4172=Sensor('TI4172',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT3=Sensor('PU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT3=Sensor('H2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT3=Sensor('CH4_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT3=Sensor('CO_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT3=Sensor('CO2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT3=Sensor('H2O_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_HT3,CH4:CH4_HT3,CO:CO_HT3,CO2:CO2_HT3,H2O:H2O_HT3}
    StrmHT3=Material_Stream('StrmHT3',FU_HT3,TI4172,PU_HT3,2,T1,CTag2)
    ListStreams.append(StrmHT3)
                     
    ''' Defining Stream W2'''
    FU_W2=Sensor('FU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W2=Sensor('TU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W2=Sensor('PU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW2=FixedConcStream('StrmW2',FU_W2,TU_W2,PU_W2,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW2)
                     
    ''' Defining Stream W3 (34)'''
    FU_W3=Sensor('FU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W3=Sensor('TU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W3=Sensor('PU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW3=FixedConcStream('StrmW3',FU_W3,TU_W3,PU_W3,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW3)
                     
    ''' Defining HEX3 (E16)'''
    HEX3=HeatExchanger('HEX3',StrmHT2,StrmHT3,StrmW2,StrmW3,Type=0)
    ListUnits.append(HEX3)
                    
    '''Defining Stream LT1 (24b)'''
    FU_LT1=Sensor('FU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT1=Sensor('TU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT1=Sensor('PU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT1=Sensor('H2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT1=Sensor('CH4_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT1=Sensor('CO_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT1=Sensor('CO2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_LT1=Sensor('H2O_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT1,CH4:CH4_LT1,CO:CO_LT1,CO2:CO2_LT1,H2O:H2O_LT1}
    StrmLT1=Material_Stream('StrmLT1',FU_LT1,TU_LT1,PU_LT1,2,T1,CTag2)
    ListStreams.append(StrmLT1)
                      
    '''Defining Energy Stream E5'''
    E6=Energy_Stream('E6',0)
    E6.Q.Flag=2
    ListStreams.append(E6)
                      
    '''Defining REX4 (Low Temp Shift Reactor) '''
    REX4=ElementBalanceReactor('REX4',StrmHT3,StrmLT1,[E6],ExoEndoFlag=-1)
    #REX4=EquilibriumReactor('REX4',StrmHT3,StrmLT1,[E6],[RE3],ExoEndoFlag=-1)
    #REX4=Reactor('REX4',StrmHT3,StrmLT1,[E6],[RE3],ExoEndoFlag=-1)
    ListUnits.append(REX4)
                     
    '''Steam Circuit Starts'''
                     
    ''' Defining Stream W4 (feed to steam drum or FG boiler)'''
    FI3110=Sensor('FI3110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W4=Sensor('TU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W4=Sensor('PU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW4=FixedConcStream('StrmW4',FI3110,TU_W4,PU_W4,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW4)
                       
    '''Defining Stream ST4(15)'''
    FU_ST4=Sensor('FU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST4=Sensor('TU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST4=Sensor('PU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST4=FixedConcStream('StrmST4',FU_ST4,TU_ST4,PU_ST4,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST4)
                     
    '''Defining the splitter that splits the boiler feed water into two streams one for RG boiler and the other for FG boiler or steam drum'''
    SPL3=Splitter('SPL3',StrmW3,[StrmW1,StrmW4])
    ListUnits.append(SPL3)
                     
                     
    '''Defining Energy Stream E7'''
    E7=Energy_Stream('E7',200000)
    ListStreams.append(E7)
                       
    '''Defining Heater3 (Steam Drum)'''
    HEAT3=Heater('HEAT3',StrmW4,StrmST4,E7,1)
#     HEAT3=HeaterVaporizer('HEAT3',StrmW4,StrmST4,E7,1)
    ListUnits.append(HEAT3)
                     
    '''Defining Stream ST5 (16) Export steam'''
    FI3106=Sensor('FI3106',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST5=Sensor('TU_ST5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3114=Sensor('PIC3114',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST5=FixedConcStream('StrmST5',FI3106,TU_ST5,PIC3114,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST5)
                     
    '''Defining Stream ST6(17)'''
    FU_ST6=Sensor('FU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST6=Sensor('TU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST6=Sensor('PU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST6=FixedConcStream('StrmST6',FU_ST6,TU_ST6,PU_ST6,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST6)
                     
    '''Defining Combined steam Stream from FG and RG boilers'''
    FU_ST8=Sensor('FU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST8=Sensor('TU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST8=Sensor('PU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST8=FixedConcStream('StrmST8',FU_ST8,TU_ST8,PU_ST8,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST8)
                     
    '''Defining splitter that splits the steam from combined steam from both boilers into two streams one sent to super heater and the other sent as export steam'''
    SPL4=Splitter('SPL4',StrmST8,[StrmST6,StrmST5])
    ListUnits.append(SPL4)
                     
                     
    '''Defining Mixer that mixes Steam from RG boiler and FG boiler'''
    MIX4=Mixer('MIX4',[StrmST3,StrmST4],StrmST8)
    ListUnits.append(MIX4)
                                     
    #'''Defining Splitter SPL2'''
    #SPL2=Splitter('SPL2',StrmST4,[StrmST5,StrmST6])
                     
    '''Defining Superheated steam ST7'''
    FU_ST7=Sensor('FU_ST7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123=Sensor('TIC3123',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116=Sensor('PI3116',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7=FixedConcStream('StrmST7',FU_ST7,TIC3123,PI3116,2,T1,CTag,'xfrac')
    ListStreams.append(StrmST7)
                     
    '''Defining Energy Stream E8'''
    E8=Energy_Stream('E8',200000)
    ListStreams.append(E8)
                     
    '''Defining Heater HEAT4 (SuperHeater) E-6-1'''
    HEAT4=Heater('HEAT4',StrmST6,StrmST7,E8,1)
    ListUnits.append(HEAT4)
                     
    '''Defining Splitter SPL5 (Splitting the super heated steam into two streams, one being fed to the pre-reformer and the other to steam-reformer)'''
    SPL5=Splitter('SPL5',StrmST7,[StrmST1,StrmST2])
    ListUnits.append(SPL5)
                     
    '''Defining Air Stream AR1 (13)'''
    FU_AR1=Sensor('FU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AR1=Sensor('TU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR1=Sensor('PU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR1=FixedConcStream('StrmAR1',FU_AR1,TU_AR1,PU_AR1,2,T1,CTag,'xfrac')
    ListStreams.append(StrmAR1)
                     
    '''Defining Air Stream AR2 (14)'''
    FIC3109=Sensor('FIC3109',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3131=Sensor('TI3131',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR2=Sensor('PU_AR2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR2=FixedConcStream('StrmAR2',FIC3109,TI3131,PU_AR2,2,T1,CTag,'xfrac')
    ListStreams.append(StrmAR2)
                     
    '''Defining Energy Stream E9''' 
    E9=Energy_Stream('E9',200000)
    ListStreams.append(E9)
                     
    '''Defining HEAT5 (Air Preheater) (E-9)'''
    HEAT5=Heater('HEAT5',StrmAR1,StrmAR2,E9,1)
    ListUnits.append(HEAT5)
                     
    '''Defining Stream Air-Natural Gas Mixture'''
    FU_AN1=Sensor('FU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AN1=Sensor('TU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AN1=Sensor('PU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_AN1=Sensor('H2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_AN1=Sensor('CO_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_AN1=Sensor('CO2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_AN1=Sensor('CH4_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_AN1=Sensor('N2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    O2_AN1=Sensor('O2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_AN1,CH4:CH4_AN1,N2:N2_AN1,O2:O2_AN1,CO:CO_AN1,CO2:CO2_AN1}
    StrmAN1=Material_Stream('StrmAN1',FU_AN1,TU_AN1,PU_AN1,2,T1,CTag)
    ListStreams.append(StrmAN1)
     
    '''Defining Stream LT4 (Recycle to furnace)'''
    FI3113=Sensor('FI3113',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT4=Sensor('TU_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3156=Sensor('PIC3156',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3103B=Sensor('AI3103B',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT4=Sensor('CH4_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT4=Sensor('CO_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT4=Sensor('CO2_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:AI3103B,CH4:CH4_LT4,CO:CO_LT4,CO2:CO2_LT4}
    StrmLT4=Material_Stream('StrmLT4',FI3113,TU_LT4,PIC3156,2,T1,CTag2)
    ListStreams.append(StrmLT4)
     
    '''Defining Stream LT4a (Recycle to furnace)'''
    FU_LT4a=Sensor('FU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT4a=Sensor('TU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT4a=Sensor('PU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT4a=Sensor('H2_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT4a=Sensor('CH4_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT4a=Sensor('CO_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT4a=Sensor('CO2_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT4a,CH4:CH4_LT4a,CO:CO_LT4a,CO2:CO2_LT4a}
    StrmLT4a=Material_Stream('StrmLT4a',FU_LT4a,TU_LT4a,PU_LT4a,2,T1,CTag2)
    ListStreams.append(StrmLT4a)
     
    '''defining splitter SPL6 for handling pressure drop'''
    SPL5a=Splitter('SPL5a',StrmLT4,[StrmLT4a],dp=[3100])
    ListUnits.append(SPL5a)
                         
    '''Defining MIX5 (Air fuel mixing)'''
    MIX5=Mixer('MIX5',[StrmAR2,StrmNG2a,StrmLT4a],StrmAN1)
    ListUnits.append(MIX5)
                   
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
    ListStreams.append(StrmFG1)
                  
    '''Defining combustion reaction'''
    #RE3=Reaction('RE3',[CH4,O2,CO2,H2O],[-1,-2,1,2])
                      
    '''Defining Furnace'''
    REX5=Reactor('REX5',StrmAN1,StrmFG1,[E1,E3,E4,E7,E8,E9],[RE4],ExoEndoFlag=-1)
    ListUnits.append(REX5)
     
    ''' Defining Stream W5 ()'''
    FU_W5=Sensor('FU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W5=Sensor('TU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W5=Sensor('PU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW5=FixedConcStream('StrmW5',FU_W5,TU_W5,PU_W5,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW5)
     
    '''Defining Stream LT2 ()'''
    FU_LT2=Sensor('FU_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT2=Sensor('TU_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT2=Sensor('PU_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT2=Sensor('H2_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT2=Sensor('CH4_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT2=Sensor('CO_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT2=Sensor('CO2_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_LT2=Sensor('H2O_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT2,CH4:CH4_LT2,CO:CO_LT2,CO2:CO2_LT2,H2O:H2O_LT2}
    StrmLT2=Material_Stream('StrmLT2',FU_LT2,TU_LT2,PU_LT2,2,T1,CTag2)
    ListStreams.append(StrmLT2)
     
    ''' Defining HEX4 (E3)'''
    HEX4=HeatExchanger('HEX4',StrmLT1,StrmLT2,StrmW5,StrmW2,Type=0)
    ListUnits.append(HEX4)
     
    ''' Defining Stream W6 (water from seperator)'''
    FU_W6=Sensor('FU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W6=Sensor('TU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W6=Sensor('PU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW6=FixedConcStream('StrmW6',FU_W6,TU_W6,PU_W6,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW6)
     
    '''Defining Stream LT3 (To be redefined)'''
    FI3112=Sensor('FI3112',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3142=Sensor('TI3142',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT3=Sensor('PU_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3103A=Sensor('AI3103A',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT3=Sensor('CH4_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT3=Sensor('CO_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT3=Sensor('CO2_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:AI3103A,CH4:CH4_LT3,CO:CO_LT3,CO2:CO2_LT3}
    StrmLT3=Material_Stream('StrmLT3',FI3112,TI3142,PU_LT3,2,T1,CTag2)
    ListStreams.append(StrmLT3)
     
    '''Defining Seperator SEP1'''
    SEP1=Seperator('SEP1',StrmLT2,[StrmLT3,StrmW6])
    ListUnits.append(SEP1)
     
    ''' Defining Stream W7 (fresh water makeup)'''
    FI4119=Sensor('FI4119',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W7=Sensor('TU_W7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W7=Sensor('PU_W7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW7=FixedConcStream('StrmW7',FI4119,TU_W7,PU_W7,1,T1,CTag,'xfrac')
    ListStreams.append(StrmW7)
     
    '''Defining Mixer MIX6'''
    MIX6=Mixer('MIX6',[StrmW6,StrmW7],StrmW5)
    ListUnits.append(MIX6)
     
     
     
    '''Defining Stream LT5 (Hydrogen rich stream)'''
    FI3114=Sensor('FI3114',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3142=Sensor('TI3142',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3160=Sensor('PIC3160',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT5=Sensor('H2_LT5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3104CH4=Sensor('AI3104CH4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3104CO=Sensor('AI3104CO',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3104CO2=Sensor('AI3104CO2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT5,CH4:AI3104CH4,CO:AI3104CO,CO2:AI3104CO2}
    StrmLT5=Material_Stream('StrmLT5',FI3114,TI3142,PIC3160,2,T1,CTag2)
#     CTag2={H2:1}
#     StrmLT5=FixedConcStream('StrmLT5',FI3114,TI3142,PIC3160,2,T1,CTag2,'xfrac')
    ListStreams.append(StrmLT5)
     
    '''Defining Seperator SEP2'''
    SEP2=Seperator('SEP2',StrmLT3,[StrmLT4,StrmLT5])
    ListUnits.append(SEP2)
     
    '''Defining Stream H2 (Hydrogen stream)'''
    FIC3216=Sensor('FIC3216',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_H2=Sensor('TU_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_H2=Sensor('PU_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_H2=Sensor('H2_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_H2=Sensor('CH4_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_H2=Sensor('CO_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_H2=Sensor('CO2_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_H2,CH4:CH4_H2,CO:CO_H2,CO2:CO2_H2}
    StrmH2=Material_Stream('StrmH2',FIC3216,TU_H2,PU_H2,2,T1,CTag2)
#     CTag2={H2:1}
#     StrmH2=FixedConcStream('StrmH2',FIC3216,TU_H2,PU_H2,2,T1,CTag2,'xfrac')
    ListStreams.append(StrmH2)
     
    '''Defining Splitter SPL6'''
    SPL6=Splitter('SPL6',StrmLT5,[StrmH2,StrmH1])
    ListUnits.append(SPL6)
    
    
      
   
      
    ToInternalUnits(ListStreams)
    #myslsqp(ListStreams,ListUnits,7)
    opt1=ipopt(ListStreams,ListUnits,5,5,1e-4,iter=1000)
#     opt1.CopyEst2Meas()
#     del opt1
#     opt2=ipopt(ListStreams,ListUnits,7,5,1e-4,iter=500)
#     opt2.CopyEst2Meas()
#     del opt2
#     opt3=ipopt(ListStreams,ListUnits,7,5,1e-5,iter=10000)

    
    ToExternalUnits(ListStreams)
    f=open('Output','w') 
    for i in ListUnits:
        print i.MaterialBalRes(),i.ComponentBalRes(),i.EnergyBalRes(),i.PressureBalRes()
    for i in ListStreams:
        if (isinstance(i,Energy_Stream)):
            print i.Q.Meas,'\t',i.Q.Est
        else:
            print i.FTag.Xindex,'\t',i.FTag.Tag,'\t', i.FTag.Meas,'\t', i.FTag.Est
            print i.TTag.Xindex,'\t',i.TTag.Tag, '\t',i.TTag.Meas,'\t', i.TTag.Est
            print i.PTag.Xindex,'\t',i.PTag.Tag,'\t', i.PTag.Meas, '\t',i.PTag.Est
            
            f.write(str(i.FTag.Tag))
            f.write(',')
            f.write(str(i.FTag.Flag))
            f.write(',')
            f.write(str(i.FTag.Meas))
            f.write(',')
            f.write(str(i.FTag.Est))
            f.write(',')
            f.write(str(i.FTag.Unit))
            f.write('\n')
            
            f.write(str(i.TTag.Tag))
            f.write(',')
            f.write(str(i.TTag.Flag))
            f.write(',')
            f.write(str(i.TTag.Meas))
            f.write(',')
            f.write(str(i.TTag.Est))
            f.write(',')
            f.write(str(i.TTag.Unit))
            f.write('\n')
            
            f.write(str(i.PTag.Tag))
            f.write(',')
            f.write(str(i.PTag.Flag))
            f.write(',')
            f.write(str(i.PTag.Meas))
            f.write(',')
            f.write(str(i.PTag.Est))
            f.write(',')
            f.write(str(i.PTag.Unit))
            f.write('\n')
            if (isinstance(i,Material_Stream)):
                for j in i.CTag.keys():
                    print i.CTag[j].Xindex,'\t',i.CTag[j].Tag,'\t', i.CTag[j].Meas,'\t', i.CTag[j].Est
                    f.writelines(str(i.CTag[j].Tag)+','+str(i.CTag[j].Flag)+','+str(i.CTag[j].Meas)+','+str(i.CTag[j].Est)+','+str(i.CTag[j].Unit)+'\n')
    f.close()
    #Report(ListUnits)
