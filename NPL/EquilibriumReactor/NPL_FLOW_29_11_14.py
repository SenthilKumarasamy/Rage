import sys
import os
basepath = os.path.dirname('__file__')
filepath = os.path.abspath(os.path.join(basepath, "..",".."))
if filepath not in sys.path:
    sys.path.append(filepath)
    
import Tkinter
import tkFileDialog

from numpy import *
from CommonFunctions.Readfile import Readfile
from CommonFunctions.ReadConfigfile import ReadConfigfile
from CommonFunctions.GenerateGraph import GenerateGraph
from Sensor.Sensor import Sensor
from Component.Comp import Comp
from Reaction.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.Mixer import Mixer
from Units.Reactor import Reactor
from Units.EquilibriumReactor import EquilibriumReactor
from Units.SteamReformer import SteamReformer
from Units.PreReformer import PreReformer
from Units.ShiftReactor import ShiftReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.PSA import PSA
from Units.Splitter import Splitter
from Units.ElementBalanceReactor import ElementBalanceReactor
from optim.ipopt import ipopt
from CommonFunctions.Report import Report
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from CommonFunctions.Write2File import Write2File
from Thermo.Refprop import Refprop
from GrossErrorDetection.GLRTest1 import GLR


if __name__=="__main__":
    
    '------------------ Reading the Measurement file--------------------'
     
    Tkinter.Tk().withdraw() # Close the root window
    ftypes=(("Excel files", "*.xls"),("All files", "*.*"))
    str1 = tkFileDialog.askopenfilename(filetypes=ftypes,title="Select the file Containing measurements")    

    
    R1=Readfile(str1)
    R2=ReadConfigfile("Config.xls")
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
    H2O=Comp(7,StdState=1)
    C4H10=Comp(10,StdState=2)
    C5H12=Comp(11,StdState=2)
    C6H14=Comp(12,StdState=2)
    '''Defining Thermo object '''
    
    ListComp=[H2,O2,CH4,CO,CO2,H2O,N2,C2H6,C3H8,C4H10,C5H12,C6H14]
    
    T1=Refprop([H2,O2,CH4,CO,CO2,H2O,N2,C2H6,C3H8,C4H10,C5H12,C6H14])

    ListStreams=[]
    ListUnits=[]
    
    '''Stream NG1a(1) Natural gas from GAIL'''
    FI4133=Sensor('FI4133',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4140a=Sensor('TI4140a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4106a=Sensor('PI4106a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG1a=Sensor('N2_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG1a=Sensor('CH4_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG1a=Sensor('C2H6_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG1a=Sensor('C3H8_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG1a=Sensor('C4H10_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG1a=Sensor('C5H12_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG1a=Sensor('C6H14_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG1a=Sensor('CO2_NG1a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:CH4_NG1a,N2:N2_NG1a,C2H6:C2H6_NG1a,C3H8:C3H8_NG1a,C4H10:C4H10_NG1a,CO2:CO2_NG1a,C5H12:C5H12_NG1a,C6H14:C6H14_NG1a}
    StrmNG1a=Material_Stream('StrmNG1a',FI4133,TI4140a,PI4106a,2,T1,CTag)
    StrmNG1a.Describe='Natural Gas from GAIL'
    ListStreams.append(StrmNG1a)
    
    '''Stream NG1(1) Natural gas from GAIL'''
    FI4130=Sensor('FI4130',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4140=Sensor('TI4140',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4106=Sensor('PI4106',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG1=Sensor('N2_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG1=Sensor('CH4_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG1=Sensor('C2H6_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG1=Sensor('C3H8_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG1=Sensor('C4H10_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG1=Sensor('C5H12_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG1=Sensor('C6H14_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG1=Sensor('CO2_NG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:CH4_NG1,N2:N2_NG1,C2H6:C2H6_NG1,C3H8:C3H8_NG1,C4H10:C4H10_NG1,CO2:CO2_NG1,C5H12:C5H12_NG1,C6H14:C6H14_NG1,}
    StrmNG1=Material_Stream('StrmNG1',FI4130,TI4140,PI4106,2,T1,CTag)
    StrmNG1.Describe='Natural Gas from GAIL'
    ListStreams.append(StrmNG1)
    
    ''' Defining Splitter SPL1a'''
    SPL1a=Splitter('SPL1a',StrmNG1a,[StrmNG1])
    SPL1a.Describe='Splitter that splits the NG from GAIL into one  stream in order to handle multiple flow sensors'
    ListUnits.append(SPL1a)       
                             
    '''Defining Stream NG2(11) Fuel to Furnace'''
    FI4131=Sensor('FI4131',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG2=Sensor('TU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG2=Sensor('PU_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG2=Sensor('N2_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG2=Sensor('CH4_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG2=Sensor('C2H6_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG2=Sensor('C3H8_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG2=Sensor('C4H10_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG2=Sensor('C5H12_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG2=Sensor('C6H14_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG2=Sensor('CO2_NG2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NG2,CH4:CH4_NG2,C2H6:C2H6_NG2,C3H8:C3H8_NG2,C4H10:C4H10_NG2,CO2:CO2_NG2,C5H12:C5H12_NG2,C6H14:C6H14_NG2}
    StrmNG2=Material_Stream('StrmNG2',FI4131,TU_NG2,PU_NG2,2,T1,CTag)
    StrmNG2.Describe='Natural Gas sent to furnace as fuel'
    ListStreams.append(StrmNG2)
                           
    ''' Defining Stream NG3 (3) NG to Desulphurization uint'''
    FI4132=Sensor('FI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG3=Sensor('TU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4107=Sensor('PI4107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG3=Sensor('N2_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG3=Sensor('CH4_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG3=Sensor('C2H6_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG3=Sensor('C3H8_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG3=Sensor('C4H10_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG3=Sensor('C5H12_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG3=Sensor('C6H14_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG3=Sensor('CO2_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NG3,CH4:CH4_NG3,C2H6:C2H6_NG3,C3H8:C3H8_NG3,C4H10:C4H10_NG3,CO2:CO2_NG3,C5H12:C5H12_NG3,C6H14:C6H14_NG3}
    StrmNG3=Material_Stream('StrmNG3',FI4132,TU_NG3,PI4107,2,T1,CTag)
    StrmNG3.Describe='Natural Gas to be mixed with Hydrogen for desulpurisation'
    ListStreams.append(StrmNG3)
                            
    ''' Defining Splitter SPL1'''
    SPL1=Splitter('SPL1',StrmNG1,[StrmNG2,StrmNG3])
    SPL1.Describe='Splitter that splits the NG from GAIL into two streams'
    ListUnits.append(SPL1)
                 
    '''Defining Stream NG2a(11) Fuel to Furnace'''
    FU_NG2a=Sensor('FU_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG2a=Sensor('TU_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4116=Sensor('PI4116',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG2a=Sensor('N2_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG2a=Sensor('CH4_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG2a=Sensor('C2H6_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG2a=Sensor('C3H8_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG2a=Sensor('C4H10_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG2a=Sensor('C5H12_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG2a=Sensor('C6H14_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG2a=Sensor('CO2_NG2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NG2a,CH4:CH4_NG2a,C2H6:C2H6_NG2a,C3H8:C3H8_NG2a,C4H10:C4H10_NG2a,CO2:CO2_NG2a,C5H12:C5H12_NG2a,C6H14:C6H14_NG2a}
    StrmNG2a=Material_Stream('StrmNG2a',FU_NG2a,TU_NG2a,PI4116,2,T1,CTag)
    StrmNG2a.Describe='Natural Gas sent to furnace as fuel (Pseudo-Stream to handle Pressure Drop)'
    ListStreams.append(StrmNG2a)
                      
    ''' Defining Splitter SPL1b'''
    SPL1b=Splitter('SPL1b',StrmNG2,[StrmNG2a],dp=[3100])
    SPL1b.Describe='Pseudo Splitter to handle pressure drop across the fuel line'
    ListUnits.append(SPL1b)                    
                               
    '''Defining Stream H1 (12)'''
    FIC3103=Sensor('FIC3103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3156=Sensor('TI3156',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3150=Sensor('PIC3150',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:1}
    StrmH1=FixedConcStream('StrmH1',FIC3103,TI3156,PIC3150,2,T1,CTag,'xfrac')
    StrmH1.Describe='Hydrogen from PSA unit to be mixed with NG for desulphurisation'
    ListStreams.append(StrmH1)
                                     
    ''' Defining Stream NG4 (4) Cold side inlet of heat exchanger E-2'''
    FU_NG4=Sensor('FU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG4=Sensor('TU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG4=Sensor('PU_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG4=Sensor('N2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG4=Sensor('CH4_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG4=Sensor('C2H6_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG4=Sensor('C3H8_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG4=Sensor('C4H10_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG4=Sensor('C5H12_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG4=Sensor('C6H14_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG4=Sensor('CO2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG4=Sensor('H2_NG4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NG4,CH4:CH4_NG4,H2:H2_NG4,C2H6:C2H6_NG4,C3H8:C3H8_NG4,C4H10:C4H10_NG4,CO2:CO2_NG4,C5H12:C5H12_NG4,C6H14:C6H14_NG4}
    StrmNG4=Material_Stream('StrmNG4',FU_NG4,TU_NG4,PU_NG4,2,T1,CTag)
    StrmNG4.Describe='Cold-side inlet of Heat Exchanger E-2'
    ListStreams.append(StrmNG4)
                                     
    '''Defining Mix1'''
    MIX1=Mixer('MIX1',[StrmNG3,StrmH1],StrmNG4)
    MIX1.Describe='Mixer that mixes Process NG with a part of Hydrogen obtained from PSA'
    ListUnits.append(MIX1)
                                   
    ''' Defining a Stream NG5 (5) Cold side outlet of heat exchanger E-2'''
    FIC3105=Sensor('FIC3105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC4101=Sensor('TIC4101',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3112=Sensor('PIC3112',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NG5=Sensor('N2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NG5=Sensor('CH4_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NG5=Sensor('C2H6_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NG5=Sensor('C3H8_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NG5=Sensor('C4H10_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NG5=Sensor('C5H12_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NG5=Sensor('C6H14_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NG5=Sensor('CO2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NG5=Sensor('H2_NG5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NG5,CH4:CH4_NG5,H2:H2_NG5,C2H6:C2H6_NG5,C3H8:C3H8_NG5,C4H10:C4H10_NG5,CO2:CO2_NG5,C5H12:C5H12_NG5,C6H14:C6H14_NG5}
    StrmNG5=Material_Stream('StrmNG5',FIC3105,TIC4101,PIC3112,2,T1,CTag)
    StrmNG5.Describe='Cold-side outlet of Heat Exchanger E-2'
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
    N2_HT1=Sensor('N2_HT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_HT1,CH4:CH4_HT1,CO:CO_HT1,CO2:CO2_HT1,H2O:H2O_HT1,N2:N2_HT1}
    StrmHT1=Material_Stream('StrmHT1',FU_HT1,TI4181,PU_HT1,2,T1,CTag,[H2O])
    StrmHT1.Describe='Outlet of HT Shift Reactor or Hot-side inlet of Exchanger E-2'
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
    N2_HT2=Sensor('N2_HT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_HT2,CH4:CH4_HT2,CO:CO_HT2,CO2:CO2_HT2,H2O:H2O_HT2,N2:N2_HT2}
    StrmHT2=Material_Stream('StrmHT2',FU_HT2,TU_HT2,PU_HT2,2,T1,CTag)#,[H2O])
    StrmHT2.Describe='Hot-side outlet of Exchanger E-2'
    ListStreams.append(StrmHT2)
                                       
    '''Defining Heat Exchanger HEX1'''
    E2=HeatExchanger('E2',StrmHT1,StrmHT2,StrmNG4,StrmNG5,Type=0)
    E2.Describe='Heat Exchanger E-2, which pre-heats the feed before mixing with steam'
    ListUnits.append(E2)
                                
    '''Defining Stream ST1 (19) steam mixed with NG before pre-reformer'''
    FIC3104=Sensor('FIC3104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST1=Sensor('TU_ST1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST1=Sensor('PU_ST1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST1=FixedConcStream('StrmST1',FIC3104,TU_ST1,PU_ST1,2,T1,CTag,'xfrac')
    StrmST1.Describe='Steam to be mixed with Pre-Reformer feed'
    ListStreams.append(StrmST1)
                                     
    '''Defining Stream NS1 (6-I) inlet to the Heater1 which is before pre-reformer'''
    FU_NS1=Sensor('FU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4169=Sensor('TI4169',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS1=Sensor('PU_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS1=Sensor('N2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS1=Sensor('CH4_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS1=Sensor('C2H6_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS1=Sensor('C3H8_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS1=Sensor('C4H10_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS1=Sensor('C5H12_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS1=Sensor('C6H14_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS1=Sensor('CO2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS1=Sensor('H2_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS1=Sensor('H2O_NS1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS1,CH4:CH4_NS1,H2:H2_NS1,H2O:H2O_NS1,C2H6:C2H6_NS1,C3H8:C3H8_NS1,C4H10:C4H10_NS1,CO2:CO2_NS1,C5H12:C5H12_NS1,C6H14:C6H14_NS1}
    StrmNS1=Material_Stream('StrmNS1',FU_NS1,TI4169,PU_NS1,2,T1,CTag)
    StrmNS1.Describe='Pre-Reformer feed before getting heated in the furnace'
    ListStreams.append(StrmNS1)
                                     
    ''' Defining MIX2 (D-10)'''
    D10=Mixer('D10',[StrmNG5,StrmST1],StrmNS1)
    D10.Describe='Mixer that mixes steam with the feed to pre-reformer'
    ListUnits.append(D10)
                                
    '''Defining Energy Stream E1'''
    E1=Energy_Stream('E1',14766496)
    ListStreams.append(E1)
    
    ''' Defining Stream NS2a (Sub-Cooler By-Pass)'''
    FU_NS2a=Sensor('FU_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS2a=Sensor('TU_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS2a=Sensor('PU_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2a=Sensor('N2_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2a=Sensor('CH4_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2a=Sensor('C2H6_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2a=Sensor('C3H8_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS2a=Sensor('C4H10_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS2a=Sensor('C5H12_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS2a=Sensor('C6H14_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2a=Sensor('CO2_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2a=Sensor('H2_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2a=Sensor('H2O_NS2a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS2a,CH4:CH4_NS2a,H2:H2_NS2a,H2O:H2O_NS2a,C2H6:C2H6_NS2a,C3H8:C3H8_NS2a,C4H10:C4H10_NS2a,CO2:CO2_NS2a,C5H12:C5H12_NS2a,C6H14:C6H14_NS2a}
    StrmNS2a=Material_Stream('StrmNS2a',FU_NS2a,TU_NS2a,PU_NS2a,2,T1,CTag)
    StrmNS2a.Describe='E-7-3 ByPass Line'
    ListStreams.append(StrmNS2a)
    
    ''' Defining Stream NS2b (Sub-Cooler E-7-3 inlet)'''
    FU_NS2b=Sensor('FU_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS2b=Sensor('TU_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS2b=Sensor('PU_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2b=Sensor('N2_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2b=Sensor('CH4_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2b=Sensor('C2H6_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2b=Sensor('C3H8_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS2b=Sensor('C4H10_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS2b=Sensor('C5H12_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS2b=Sensor('C6H14_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2b=Sensor('CO2_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2b=Sensor('H2_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2b=Sensor('H2O_NS2b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS2b,CH4:CH4_NS2b,H2:H2_NS2b,H2O:H2O_NS2b,C2H6:C2H6_NS2b,C3H8:C3H8_NS2b,C4H10:C4H10_NS2b,CO2:CO2_NS2b,C5H12:C5H12_NS2b,C6H14:C6H14_NS2b}
    StrmNS2b=Material_Stream('StrmNS2b',FU_NS2b,TU_NS2b,PU_NS2b,2,T1,CTag)
    StrmNS2b.Describe='E-7-3 Inlet'
    ListStreams.append(StrmNS2b)
    
    ''' Defining Splitter SPL2'''
    SPL2=Splitter('SPL2',StrmNS1,[StrmNS2a,StrmNS2b])
    SPL2.Describe='Splitter that splits the NG and steam to E-7-3 inlet and bypass'
    ListUnits.append(SPL2)
    
    ''' Defining Stream NS2c (E-7-3 outlet)'''
    FU_NS2c=Sensor('FU_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS2c=Sensor('TU_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS2c=Sensor('PU_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2c=Sensor('N2_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2c=Sensor('CH4_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2c=Sensor('C2H6_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2c=Sensor('C3H8_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS2c=Sensor('C4H10_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS2c=Sensor('C5H12_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS2c=Sensor('C6H14_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2c=Sensor('CO2_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2c=Sensor('H2_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2c=Sensor('H2O_NS2c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS2c,CH4:CH4_NS2c,H2:H2_NS2c,H2O:H2O_NS2c,C2H6:C2H6_NS2c,C3H8:C3H8_NS2c,C4H10:C4H10_NS2c,CO2:CO2_NS2c,C5H12:C5H12_NS2c,C6H14:C6H14_NS2c}
    StrmNS2c=Material_Stream('StrmNS2c',FU_NS2c,TU_NS2c,PU_NS2c,2,T1,CTag)
    StrmNS2c.Describe='E-7-3 outlet'
    ListStreams.append(StrmNS2c)
    
    ''' Defining Energy Stream E2a. E2 is not included in the list of streams as E2.Q not to be part of X'''
    E2a=Energy_Stream('E2a',0)
    E2a.Q.Flag=2
    ListStreams.append(E2a)
   
    
    ''' Defining Cooler'''
    E73=Heater('E-7-3',StrmNS2b,StrmNS2c,E2a,-1,Dp=0)
    E73.Describe='Heater that heats the feed to pre-reformer (Located inside the furnace)'
    ListUnits.append(E73)
    
    ''' Defining Stream NS2d (Inlet to E-6-3)'''
    FU_NS2d=Sensor('FU_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS2d=Sensor('TU_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS2d=Sensor('PU_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2d=Sensor('N2_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2d=Sensor('CH4_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2d=Sensor('C2H6_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2d=Sensor('C3H8_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS2d=Sensor('C4H10_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS2d=Sensor('C5H12_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS2d=Sensor('C6H14_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2d=Sensor('CO2_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2d=Sensor('H2_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2d=Sensor('H2O_NS2d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS2d,CH4:CH4_NS2d,H2:H2_NS2d,H2O:H2O_NS2d,C2H6:C2H6_NS2d,C3H8:C3H8_NS2d,C4H10:C4H10_NS2d,CO2:CO2_NS2d,C5H12:C5H12_NS2d,C6H14:C6H14_NS2d}
    StrmNS2d=Material_Stream('StrmNS2d',FU_NS2d,TU_NS2d,PU_NS2d,2,T1,CTag)
    StrmNS2d.Describe='Inlet to E-6-3'
    ListStreams.append(StrmNS2d)
    
    ''' Defining Mixer MIX2a'''
    MIX2a=Mixer('MIX2a',[StrmNS2a,StrmNS2c],StrmNS2d)
    MIX2a.Describe='Mixer that mixes E-7-3 outlet and its bypass lines'
    ListUnits.append(MIX2a)
    
                                
    ''' Defining Stream NS2(6) (PreReformer1 Inlet)'''
    FU_NS2=Sensor('FU_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TRC4167=Sensor('TRC4167',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4103=Sensor('PI4103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS2=Sensor('N2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS2=Sensor('CH4_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_NS2=Sensor('C2H6_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_NS2=Sensor('C3H8_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_NS2=Sensor('C4H10_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_NS2=Sensor('C5H12_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_NS2=Sensor('C6H14_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS2=Sensor('CO2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS2=Sensor('H2_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS2=Sensor('H2O_NS2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS2,CH4:CH4_NS2,H2:H2_NS2,H2O:H2O_NS2,C2H6:C2H6_NS2,C3H8:C3H8_NS2,C4H10:C4H10_NS2,CO2:CO2_NS2,C5H12:C5H12_NS2,C6H14:C6H14_NS2}
    StrmNS2=Material_Stream('StrmNS2',FU_NS2,TRC4167,PI4103,2,T1,CTag)
    StrmNS2.Describe='Pre-Reformer feed after getting heated in the furnace'
    ListStreams.append(StrmNS2)
    
    
                                
    ''' Defining Heat1'''
    E63=Heater('E-6-3',StrmNS2d,StrmNS2,E1,1,Dp=300)
    E63.Describe='Heater that heats the feed to pre-reformer (Located inside the furnace)'
    ListUnits.append(E63)
                            
    '''Defining Stream NS3(7) (PreReformer1 outlet)'''
    FU_NS3=Sensor('FU_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3119=Sensor('TI3119',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4132=Sensor('PI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS3=Sensor('N2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS3=Sensor('CH4_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit) 
    CO2_NS3=Sensor('CO2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS3=Sensor('H2_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS3=Sensor('H2O_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS3=Sensor('CO_NS3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_NS3,CH4:CH4_NS3,H2:H2_NS3,H2O:H2O_NS3,CO:CO_NS3,CO2:CO2_NS3}
    StrmNS3=Material_Stream('StrmNS3',FU_NS3,TI3119,PI4132,2,T1,CTag)
    StrmNS3.Describe='Pre-Reformer outlet1'
    ListStreams.append(StrmNS3)
                            
    ''' Defining Energy Stream E2. E2 is not included in the list of streams as E2.Q not to be part of X'''
    E2b=Energy_Stream('E2b',0)
    E2b.Q.Flag=2
    ListStreams.append(E2b)
                        
    '''Defining Non-Equilibrium reactions happening in Pre-reformer'''
    RE1=Reaction('RE1',[C2H6,H2O,CO,H2],[-1,-2,2,5])
    RE2=Reaction('RE2',[C3H8,H2O,CO,H2],[-1,-3,3,7])
    RE3=Reaction('RE3',[C4H10,H2O,CO,H2],[-1,-4,4,9])
    RE4=Reaction('RE4',[C5H12,H2O,CO,H2],[-1,-5,5,11])
    RE5=Reaction('RE5',[C6H14,H2O,CO,H2],[-1,-6,6,13])
     
     
                            
    '''Defining REX1 (PreReformer1)'''
    D8_I=Reactor('D8-I',StrmNS2,StrmNS3,[E2b],[RE1,RE2,RE3,RE4,RE5],ExoEndoFlag=1)
    D8_I.Describe='Pre-Reformer'
    ListUnits.append(D8_I)
     
    '''Defining Stream NS3a (PreReformer2 outlet)'''
    FU_NS3a=Sensor('FU_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3119a=Sensor('TI3119a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI4132a=Sensor('PI4132a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS3a=Sensor('H2_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS3a=Sensor('CH4_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS3a=Sensor('H2O_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS3a=Sensor('CO_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS3a=Sensor('CO2_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS3a=Sensor('N2_NS3a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS3a,CH4:CH4_NS3a,H2O:H2O_NS3a,CO:CO_NS3a,CO2:CO2_NS3a,N2:N2_NS3a}
    StrmNS3a=Material_Stream('StrmNS3a',FU_NS3a,TI3119a,PI4132a,2,T1,CTag)
    StrmNS3a.Describe='Pre-Reformer outlet2'
    ListStreams.append(StrmNS3a)

    RE6=Reaction('RE6',[CO,H2,CH4,H2O],[-1,-3,1,1],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[0])#10.1)
    RE7=Reaction('RE7',[CO,H2O,CO2,H2],[-1,-1,1,1],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[1])#0.0)
      
    '''Defining Energy Stream E2aa'''
    E2aa=Energy_Stream('E2aa',0)
    E2aa.Q.Flag=2
    ListStreams.append(E2aa)
      
    '''Definig REX1 (PreReformer2)'''
    D8_II=PreReformer('D8-II',StrmNS3,StrmNS3a,[E2aa],[RE6,RE7],ExoEndoFlag=1)
    D8_II.Describe='Pre-Reformer'
    ListUnits.append(D8_II)
                          
    '''Defining Streams ST2(18) Steam being mixed with pre reformer outlet'''
    FIC3107=Sensor('FIC3107',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST2=Sensor('TU_ST2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST2=Sensor('PU_ST2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST2=FixedConcStream('StrmST2',FIC3107,TU_ST2,PU_ST2,2,T1,CTag,'xfrac')
    StrmST2.Describe='Steam to be mixed with the Pre-Reformer outlet'
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
    N2_NS4=Sensor('N2_NS4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS4,CH4:CH4_NS4,H2O:H2O_NS4,CO:CO_NS4,CO2:CO2_NS4,N2:N2_NS4}
    StrmNS4=Material_Stream('StrmNS4',FU_NS4,TU_NS4,PU_NS4,2,T1,CTag)
    StrmNS4.Describe='Feed to Steam Reformer before getting heated in the furnace'
    ListStreams.append(StrmNS4)
                                 
    ''' Defining Mixer MIX3'''
    D14=Mixer('D14',[StrmNS3a,StrmST2],StrmNS4)
    D14.Describe='Mixer that mixes steam with the pre-reformer outlet stream'
    ListUnits.append(D14)
                                 
    '''Defining Stream NS5 (9) Feed to Steam Reformer'''
    FU_NS5=Sensor('FU_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3124=Sensor('TIC3124',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3117=Sensor('PI3117',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5=Sensor('H2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5=Sensor('CH4_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5=Sensor('H2O_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5=Sensor('CO_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5=Sensor('CO2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5=Sensor('N2_NS5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5,CH4:CH4_NS5,H2O:H2O_NS5,CO:CO_NS5,CO2:CO2_NS5,N2:N2_NS5}
    StrmNS5=Material_Stream('StrmNS5',FU_NS5,TIC3124,PI3117,2,T1,CTag)
    StrmNS5.Describe='Feed to Steam Reformer after getting heated in the furnace'
    ListStreams.append(StrmNS5)
    
    '''Defining Stream NS5a (E-7-2 Bypass line)'''
    FU_NS5a=Sensor('FU_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS5a=Sensor('TU_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS5a=Sensor('PU_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5a=Sensor('H2_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5a=Sensor('CH4_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5a=Sensor('H2O_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5a=Sensor('CO_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5a=Sensor('CO2_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5a=Sensor('N2_NS5a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5a,CH4:CH4_NS5a,H2O:H2O_NS5a,CO:CO_NS5a,CO2:CO2_NS5a,N2:N2_NS5a}
    StrmNS5a=Material_Stream('StrmNS5a',FU_NS5a,TU_NS5a,PU_NS5a,2,T1,CTag)
    StrmNS5a.Describe=' E-7-2 ByPass line'
    ListStreams.append(StrmNS5a)
    
    '''Defining Stream NS5b (Inlet to E-7-2)'''
    FU_NS5b=Sensor('FU_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS5b=Sensor('TU_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS5b=Sensor('PU_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5b=Sensor('H2_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5b=Sensor('CH4_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5b=Sensor('H2O_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5b=Sensor('CO_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5b=Sensor('CO2_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5b=Sensor('N2_NS5b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5b,CH4:CH4_NS5b,H2O:H2O_NS5b,CO:CO_NS5b,CO2:CO2_NS5b,N2:N2_NS5b}
    StrmNS5b=Material_Stream('StrmNS5b',FU_NS5b,TU_NS5b,PU_NS5b,2,T1,CTag)
    StrmNS5b.Describe='Inlet to E-7-2'
    ListStreams.append(StrmNS5b)
    
    ''' Defining Splitter SPL3a'''
    SPL3a=Splitter('SPL3a',StrmNS4,[StrmNS5a,StrmNS5b])
    SPL3a.Describe='Splitter that splits the PreReformer outlet and steam  to E-7-2 inlet and bypass'
    ListUnits.append(SPL3a)
    
    '''Defining Stream NS5c (Outlet of E-7-2)'''
    FU_NS5c=Sensor('FU_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NS5c=Sensor('TU_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS5c=Sensor('PU_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5c=Sensor('H2_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5c=Sensor('CH4_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5c=Sensor('H2O_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5c=Sensor('CO_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5c=Sensor('CO2_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5c=Sensor('N2_NS5c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5c,CH4:CH4_NS5c,H2O:H2O_NS5c,CO:CO_NS5c,CO2:CO2_NS5c,N2:N2_NS5c}
    StrmNS5c=Material_Stream('StrmNS5c',FU_NS5c,TU_NS5c,PU_NS5c,2,T1,CTag)
    StrmNS5c.Describe='Outlet of E-7-2'
    ListStreams.append(StrmNS5c)
    
    
    ''' Defining Energy Stream E2a. E2 is not included in the list of streams as E2.Q not to be part of X'''
    E3a=Energy_Stream('E3a',0)
    E3a.Q.Flag=2
    ListStreams.append(E3a)
   
    
    ''' Defining Cooler'''
    E72=Heater('E-7-2',StrmNS5b,StrmNS5c,E3a,-1,Dp=0)
    E72.Describe='Heater that heats the feed to pre-reformer (Located inside the furnace)'
    ListUnits.append(E72)
    
    
    '''Defining Stream NS5d Inlet to E-6-2'''
    FU_NS5d=Sensor('FU_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3130=Sensor('TI3130',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS5d=Sensor('PU_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS5d=Sensor('H2_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS5d=Sensor('CH4_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS5d=Sensor('H2O_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS5d=Sensor('CO_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS5d=Sensor('CO2_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS5d=Sensor('N2_NS5d',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS5d,CH4:CH4_NS5d,H2O:H2O_NS5d,CO:CO_NS5d,CO2:CO2_NS5d,N2:N2_NS5d}
    StrmNS5d=Material_Stream('StrmNS5d',FU_NS5d,TI3130,PU_NS5d,2,T1,CTag)
    StrmNS5d.Describe='Inlet to E-6-2'
    ListStreams.append(StrmNS5d)
    
    ''' Defining Mixer MIX3a'''
    MIX3a=Mixer('MIX3a',[StrmNS5a,StrmNS5c],StrmNS5d)
    MIX3a.Describe='Mixer that mixes E-7-2 outlet and its bypass lines'
    ListUnits.append(MIX3a)
                                  
    '''Defining Energy Stream E3'''
    E3=Energy_Stream('E3',600000)
    ListStreams.append(E3)
                                  
    '''Defining Heater HEAT2'''
    E62=Heater('E-6-2',StrmNS5d,StrmNS5,E3,1)
    E62.Describe='Heater that heats the feed to the steam reformer (Located inside the furnace)'
    ListUnits.append(E62)
                                 
    '''Defining Stream NS6 (10) Outlet of Stream Reformer'''
    FU_NS6=Sensor('FU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3132=Sensor('TI3132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NS6=Sensor('PU_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS6=Sensor('H2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS6=Sensor('CH4_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS6=Sensor('H2O_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS6=Sensor('CO_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS6=Sensor('CO2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS6=Sensor('N2_NS6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS6,CH4:CH4_NS6,H2O:H2O_NS6,CO:CO_NS6,CO2:CO2_NS6,N2:N2_NS6}
    StrmNS6=Material_Stream('StrmNS6',FU_NS6,TI3132,PU_NS6,2,T1,CTag,FreeBasis=[H2O])
    StrmNS6.Describe='Outlet of  Steam Reformer or Hotside inlet of RG Boiler'
    ListStreams.append(StrmNS6)
                                 
    '''Defining Energy Stream E4'''
    E4=Energy_Stream('E4',600000)
    ListStreams.append(E4)
     
    '''Defining the Reactions happening in steam reformer'''
    RE7a=Reaction('RE7a',[CH4,H2O,CO,H2],[-1,-1,1,3],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[2])#3.6)
    RE8=Reaction('RE8',[CO,H2O,CO2,H2],[-1,-1,1,1],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[3])#0.0)
                                 
    '''Defining REX2 (Steam Reformer) '''
    D7=SteamReformer('D7',StrmNS5,StrmNS6,[E4],[RE7a,RE8],ExoEndoFlag=1)
    D7.Describe='Steam Reformer (Located inside the furnace)'
    ListUnits.append(D7)
                              
    '''Defining Stream NS7 (22) Inlet to HT shift Reactor'''
    FU_NS7=Sensor('FU_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3135=Sensor('TIC3135',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3129=Sensor('PI3129',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_NS7=Sensor('H2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_NS7=Sensor('CH4_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_NS7=Sensor('H2O_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_NS7=Sensor('CO_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_NS7=Sensor('CO2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_NS7=Sensor('N2_NS7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2:H2_NS7,CH4:CH4_NS7,H2O:H2O_NS7,CO:CO_NS7,CO2:CO2_NS7,N2:N2_NS7}
    StrmNS7=Material_Stream('StrmNS7',FU_NS7,TIC3135,PI3129,2,T1,CTag)
    StrmNS7.Describe='Inlet of HT shift Reactor or Hotside outlet of RG Boiler'
    ListStreams.append(StrmNS7)
                                 
    ''' Defining Stream W1 (Feed water to RG Boiler)'''
    FI4110=Sensor('FI4110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W1=Sensor('TU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W1=Sensor('PU_W1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW1=FixedConcStream('StrmW1',FI4110,TU_W1,PU_W1,1,T1,CTag,'xfrac')
    StrmW1.Describe='Coldside inlet of RG Boiler'
    ListStreams.append(StrmW1)
                                   
    '''Defining Stream ST3 (Steam from RG Boiler)'''
    FU_ST3=Sensor('FU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST3=Sensor('TU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST3=Sensor('PU_ST3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST3=FixedConcStream('StrmST3',FU_ST3,TU_ST3,PU_ST3,2,T1,CTag,'xfrac')
    StrmST3.Describe='Coldside outlet of RG Boiler'
    ListStreams.append(StrmST3)
                                   
    '''Defining Heat Exchanger HEX2 (E-1) RG Boiler'''
    E_1=HeatExchanger('E-1',StrmNS6,StrmNS7,StrmW1,StrmST3,Type=0)
    E_1.Describe='RG Boiler (E-1)'
    ListUnits.append(E_1)
                              
    '''Defining Energy Stream E5'''
    E5=Energy_Stream('E5',0)
    E5.Q.Flag=2
    ListStreams.append(E5)
     
    '''defining shift reaction'''
    RE8a=Reaction('RE8a',[CO,H2O,CO2,H2],[-1,-1,1,1],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[4])#0.1)
                               
    '''Defining REX3 (Adiabatic Reactor) (High Temperature Shift Reactor)'''
    D2=ShiftReactor('D2',StrmNS7,StrmHT1,[E5],[RE8a],ExoEndoFlag=-1)
    D2.Describe='HT Shift Reactor'
    ListUnits.append(D2)
                             
    '''Defining Stream HT3 (24A)'''
    FU_HT3=Sensor('FU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4174=Sensor('TI4174',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_HT3=Sensor('PU_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_HT3=Sensor('H2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_HT3=Sensor('CH4_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_HT3=Sensor('CO_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_HT3=Sensor('CO2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_HT3=Sensor('H2O_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_HT3=Sensor('N2_HT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_HT3,CH4:CH4_HT3,CO:CO_HT3,CO2:CO2_HT3,H2O:H2O_HT3,N2:N2_HT3}
    StrmHT3=Material_Stream('StrmHT3',FU_HT3,TI4174,PU_HT3,2,T1,CTag2)
    StrmHT3.Describe='Inlet of LT shift Reactor or Hotside outlet of E-16 Exchanger'
    ListStreams.append(StrmHT3)
                               
    ''' Defining Stream W2'''
    FU_W2=Sensor('FU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W2=Sensor('TU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W2=Sensor('PU_W2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW2=FixedConcStream('StrmW2',FU_W2,TU_W2,PU_W2,1,T1,CTag,'xfrac')
    StrmW2.Describe='Cold side inlet of E-16'
    ListStreams.append(StrmW2)
                               
    ''' Defining Stream W3 (34)'''
    FU_W3=Sensor('FU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W3=Sensor('TU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W3=Sensor('PU_W3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW3=FixedConcStream('StrmW3',FU_W3,TU_W3,PU_W3,1,T1,CTag,'xfrac')
    StrmW3.Describe='Cold side outlet of E-16'
    ListStreams.append(StrmW3)
                               
    ''' Defining HEX3 (E16)'''
    HEX3=HeatExchanger('E16',StrmHT2,StrmHT3,StrmW2,StrmW3,Type=0)
    HEX3.Describe='Boiler feed water preheater (E-16)'
    ListUnits.append(HEX3)
                              
    '''Defining Stream LT1 (24b)'''
    FU_LT1=Sensor('FU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI4180=Sensor('TI4180',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT1=Sensor('PU_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT1=Sensor('H2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT1=Sensor('CH4_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT1=Sensor('CO_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT1=Sensor('CO2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_LT1=Sensor('H2O_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_LT1=Sensor('N2_LT1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT1,CH4:CH4_LT1,CO2:CO2_LT1,H2O:H2O_LT1,N2:N2_LT1,CO:CO_LT1}
    StrmLT1=Material_Stream('StrmLT1',FU_LT1,TI4180,PU_LT1,2,T1,CTag2,[H2O])
    StrmLT1.Describe='Outlet of LT shift Reactor or Hotside inlet of E-3 '
    ListStreams.append(StrmLT1)
                                
    '''Defining Energy Stream E5'''
    E6=Energy_Stream('E6',0)
    E6.Q.Flag=2
    ListStreams.append(E6)
    
    '''defining shift reaction'''
    RE8b=Reaction('RE8b',[CO,H2O,CO2,H2],[-1,-1,1,1],EquTempAppFlag=2,EquTempApp=R2.EquTempApp[5])#19.3)
                                 
    '''Defining REX4 (Low Temp Shift Reactor) '''
    D20=ShiftReactor('D20',StrmHT3,StrmLT1,[E6],[RE8b],ExoEndoFlag=-1)
    D20.Describe='LT Shift Reactor'
    ListUnits.append(D20)
                               
    '''Steam Circuit Starts'''
                                
    ''' Defining Stream W4 (feed to steam drum or FG boiler)'''
    FI3110=Sensor('FI3110',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W4=Sensor('TU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W4=Sensor('PU_W4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW4=FixedConcStream('StrmW4',FI3110,TU_W4,PU_W4,1,T1,CTag,'xfrac')
    StrmW4.Describe='feed to steam drum or FG boiler'
    ListStreams.append(StrmW4)
                                  
    '''Defining Stream ST4(15)'''
    FU_ST4=Sensor('FU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST4=Sensor('TU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST4=Sensor('PU_ST4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST4=FixedConcStream('StrmST4',FU_ST4,TU_ST4,PU_ST4,2,T1,CTag,'xfrac')
    StrmST4.Describe='Steam from Steam Drum or FG boiler'
    ListStreams.append(StrmST4)
                                
    '''Defining the splitter that splits the boiler feed water into two streams one for RG boiler and the other for FG boiler or steam drum'''
    SPL3=Splitter('SPL3',StrmW3,[StrmW1,StrmW4])
    SPL3.Describe='splitter that splits the boiler feed water into two streams one for RG boiler and the other for FG boiler or steam drum'
    ListUnits.append(SPL3)
                                
                                
    '''Defining Energy Stream E7'''
    E7=Energy_Stream('E7',200000)
    ListStreams.append(E7)
                                  
    '''Defining Heater3 (Steam Drum)'''
    F4=Heater('F-4',StrmW4,StrmST4,E7,1)
    F4.Describe='Steam Drum or FG Boiler (Located inside the furnace)'
    ListUnits.append(F4)
                                
    '''Defining Stream ST5 (16) Export steam'''
    FI3106=Sensor('FI3106',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST5=Sensor('TU_ST5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3114=Sensor('PIC3114',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST5=FixedConcStream('StrmST5',FI3106,TU_ST5,PIC3114,2,T1,CTag,'xfrac')
    StrmST5.Describe='Export Steam'
    ListStreams.append(StrmST5)
                                
    '''Defining Stream ST6 (Inlet to E-6-1)'''
    FU_ST6=Sensor('FU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST6=Sensor('TU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST6=Sensor('PU_ST6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST6=FixedConcStream('StrmST6',FU_ST6,TU_ST6,PU_ST6,2,T1,CTag,'xfrac')
    StrmST6.Describe='Inlet to suher heater'
    ListStreams.append(StrmST6)
                                
    '''Defining Combined steam Stream from FG and RG boilers'''
    FU_ST8=Sensor('FU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST8=Sensor('TU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST8=Sensor('PU_ST8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST8=FixedConcStream('StrmST8',FU_ST8,TU_ST8,PU_ST8,2,T1,CTag,'xfrac')
    StrmST8.Describe='Combined Stream from Rg and FG Boilers'
    ListStreams.append(StrmST8)
              
              
    '''Defining Mixer that mixes Steam from RG boiler and FG boiler'''
    MIX4=Mixer('MIX4',[StrmST3,StrmST4],StrmST8)
    MIX4.Describe='Mixer that mixes stream from RG and FG Boilers'
    ListUnits.append(MIX4)
                                
    '''Defining splitter that splits the steam from combined steam from both boilers into two streams one sent to super heater and the other sent as export steam'''
    SPL4=Splitter('SPL4',StrmST8,[StrmST6,StrmST5])
    SPL4.Describe='splitter that splits the steam from combined steam from both boilers into two streams one sent to super heater and the other sent as export steam'
    ListUnits.append(SPL4)
                                                
                                
    '''Defining Superheated steam ST7'''
    FU_ST7=Sensor('FU_ST7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TIC3123=Sensor('TIC3123',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PI3116=Sensor('PI3116',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7=FixedConcStream('StrmST7',FU_ST7,TIC3123,PI3116,2,T1,CTag,'xfrac')
    StrmST7.Describe='Super heated steam from super heater'
    ListStreams.append(StrmST7)
    
    '''Defining Stream ST6a Outlet of E-6-1'''
    FU_ST6a=Sensor('FU_ST6a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3126=Sensor('TI3126',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST6a=Sensor('PU_ST6a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST6a=FixedConcStream('StrmST6a',FU_ST6a,TI3126,PU_ST6a,2,T1,CTag,'xfrac')
    StrmST6a.Describe='Outlet of E-6-1'
    ListStreams.append(StrmST6a)
                                
    '''Defining Energy Stream E8'''
    E8=Energy_Stream('E8',200000)
    ListStreams.append(E8)
                                
    '''Defining Heater HEAT4 (SuperHeater) E-6-1'''
    E61=Heater('E-6-1',StrmST6,StrmST6a,E8,1)
    E61.Describe='E-6-1'
    ListUnits.append(E61)
    
    '''Defining ST7a (ByPass to E-7-1)'''
    FU_ST7a=Sensor('FU_ST7a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST7a=Sensor('TU_ST7a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST7a=Sensor('PU_ST7a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7a=FixedConcStream('StrmST7a',FU_ST7a,TU_ST7a,PU_ST7a,2,T1,CTag,'xfrac')
    StrmST7a.Describe='ByPass to E-7-1'
    ListStreams.append(StrmST7a)
    
    '''Defining ST7b (Inlet to E-7-1)'''
    FU_ST7b=Sensor('FU_ST7b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST7b=Sensor('TU_ST7b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST7b=Sensor('PU_ST7b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7b=FixedConcStream('StrmST7b',FU_ST7b,TU_ST7b,PU_ST7b,2,T1,CTag,'xfrac')
    StrmST7b.Describe='Inlet to E-7-1'
    ListStreams.append(StrmST7b)
    
    '''Defining splitter that splits the steam from combined steam into bypass and inlet to E-7-1'''
    SPL4a=Splitter('SPL4a',StrmST6a,[StrmST7a,StrmST7b])
    SPL4a.Describe='splitter that splits the steam from combined steam from both boilers into two streams one sent to super heater and the other sent as export steam'
    ListUnits.append(SPL4a)
    
    '''Defining ST7c (Outlet of E-7-1)'''
    FU_ST7c=Sensor('FU_ST7c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_ST7c=Sensor('TU_ST7c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_ST7c=Sensor('PU_ST7c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmST7c=FixedConcStream('StrmST7c',FU_ST7c,TU_ST7c,PU_ST7c,2,T1,CTag,'xfrac')
    StrmST7c.Describe='Outlet of E-7-1'
    ListStreams.append(StrmST7c)
    
    '''Defining Energy Stream E8a'''
    E8a=Energy_Stream('E8a',200000)
    ListStreams.append(E8a)
                                
    '''Defining Heater sub-cooler E-7-1'''
    E71=Heater('E-7-1',StrmST7b,StrmST7c,E8a,1)
    E71.Describe='E-7-1'
    ListUnits.append(E71)
    
    '''Defining Mixer that mixes bypass and outlet of E-7-1'''
    MIX4a=Mixer('MIX4a',[StrmST7a,StrmST7c],StrmST7)
    MIX4a.Describe='Mixer that mixes stream from RG and FG Boilers'
    ListUnits.append(MIX4a)
    
                                
    '''Defining Splitter SPL5 (Splitting the super heated steam into two streams, one being fed to the pre-reformer and the other to steam-reformer)'''
    SPL5=Splitter('SPL5',StrmST7,[StrmST1,StrmST2])
    SPL5.Describe='Splitter, Splitting the super heated steam into two streams, one being fed to the pre-reformer and the other to steam-reformer'
    ListUnits.append(SPL5)
                                
    '''Defining Air Stream AR1 (13)'''
    FU_AR1=Sensor('FU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AR1=Sensor('TU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR1=Sensor('PU_AR1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR1=FixedConcStream('StrmAR1',FU_AR1,TU_AR1,PU_AR1,2,T1,CTag,'xfrac')
    StrmAR1.Describe='Atmospheric air to air pre-heater'
    ListStreams.append(StrmAR1)
                                   
    '''Defining Air Stream AR2 (14)'''
    FIC3109=Sensor('FIC3109',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3131=Sensor('TI3131',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AR2=Sensor('PU_AR2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:0.79,O2:0.21}
    StrmAR2=FixedConcStream('StrmAR2',FIC3109,TI3131,PU_AR2,2,T1,CTag,'xfrac')
    StrmAR2.Describe='Pre-heated air to the furnace'
    ListStreams.append(StrmAR2)
                                   
    '''Defining Energy Stream E9''' 
    E9=Energy_Stream('E9',200000)
    ListStreams.append(E9)
                                   
    '''Defining HEAT5 (Air Preheater) (E-9)'''
    HEAT5=Heater('E-9',StrmAR1,StrmAR2,E9,1)
    HEAT5.Describe='Air Pre-Heater (Located inside the furnace)'
    ListUnits.append(HEAT5)
                                 
    '''Defining Stream Air-Natural Gas Mixture'''
    FU_AN1=Sensor('FU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_AN1=Sensor('TU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_AN1=Sensor('PU_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_AN1=Sensor('N2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_AN1=Sensor('CH4_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C2H6_AN1=Sensor('C2H6_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C3H8_AN1=Sensor('C3H8_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C4H10_AN1=Sensor('C4H10_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C5H12_AN1=Sensor('C5H12_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    C6H14_AN1=Sensor('C6H14_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_AN1=Sensor('CO2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    O2_AN1=Sensor('O2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_AN1=Sensor('H2_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_AN1=Sensor('CO_AN1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={N2:N2_AN1,CH4:CH4_AN1,CO2:CO2_AN1,O2:O2_AN1,H2:H2_AN1,CO:CO_AN1,C2H6:C2H6_AN1,C3H8:C3H8_AN1,C4H10:C4H10_AN1,C5H12:C5H12_AN1,C6H14:C6H14_AN1}
    StrmAN1=Material_Stream('StrmAN1',FU_AN1,TU_AN1,PU_AN1,2,T1,CTag)
    StrmAN1.Describe='Air-Natural gas- off gas mixture to furnace for burning'
    ListStreams.append(StrmAN1)
                 
    '''Defining Stream LT4 (Recycle to furnace)'''
    FIC3113=Sensor('FIC3113',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT4=Sensor('TU_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3156=Sensor('PIC3156',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    AI3103B=Sensor('AI3103B',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT4=Sensor('CH4_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT4=Sensor('CO_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT4=Sensor('CO2_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_LT4=Sensor('N2_LT4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:AI3103B,CH4:CH4_LT4,CO2:CO2_LT4,N2:N2_LT4,CO:CO_LT4}
    StrmLT4=Material_Stream('StrmLT4',FIC3113,TU_LT4,PIC3156,2,T1,CTag2)
    StrmLT4.Describe='Off gas from PSA unit'
    ListStreams.append(StrmLT4)
                 
    '''Defining Stream LT4a (Recycle to furnace)'''
    FU_LT4a=Sensor('FU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_LT4a=Sensor('TU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_LT4a=Sensor('PU_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT4a=Sensor('H2_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT4a=Sensor('CH4_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT4a=Sensor('CO_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT4a=Sensor('CO2_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_LT4a=Sensor('N2_LT4a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT4a,CH4:CH4_LT4a,CO2:CO2_LT4a,N2:N2_LT4a,CO:CO_LT4a}
    StrmLT4a=Material_Stream('StrmLT4a',FU_LT4a,TU_LT4a,PU_LT4a,2,T1,CTag2)
    StrmLT4a.Describe='Off gas from PSA unit (Pseudo Stream to handle pressure drop)'
    ListStreams.append(StrmLT4a)
                 
    '''defining splitter SPL6 for handling pressure drop'''
    SPL5a=Splitter('SPL5a',StrmLT4,[StrmLT4a],dp=[3100])
    SPL5a.Describe='Pseudo Splitter to handle pressure drop in the off gas stream being recycled to the furnace'
    ListUnits.append(SPL5a)
                                     
    '''Defining MIX5 (Air fuel mixing)'''
    MIX5=Mixer('MIX5',[StrmAR2,StrmNG2a,StrmLT4a],StrmAN1)
    MIX5.Describe='Mixer that mixes air,fuel, and off gas from PSA'
    ListUnits.append(MIX5)
                                
    '''Defining Flue gas Stream (20)'''
    FU_FG1=Sensor('FU_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3129=Sensor('TI3129',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3127=Sensor('PIC3127',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_FG1=Sensor('CO2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2O_FG1=Sensor('H2O_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_FG1=Sensor('N2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    O2_FG1=Sensor('O2_FG1',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CO2:CO2_FG1,H2O:H2O_FG1,N2:N2_FG1,O2:O2_FG1}
    StrmFG1=Material_Stream('StrmFG1',FU_FG1,TI3129,PIC3127,2,T1,CTag)
    StrmFG1.Describe='Flue Gas from furnace'
    ListStreams.append(StrmFG1)
                               
    '''Defining combustion reaction'''
    RE9=Reaction('RE9',[CH4,O2,CO2,H2O],[-1,-2,1,2])
    RE10=Reaction('RE10',[C2H6,O2,CO2,H2O],[-2,-7,4,6])
    RE11=Reaction('RE11',[C3H8,O2,CO2,H2O],[-1,-5,3,4])
    RE12=Reaction('RE12',[C4H10,O2,CO2,H2O],[-2,-13,8,10])
    RE13=Reaction('RE13',[C5H12,O2,CO2,H2O],[-1,-8,5,6])
    RE14=Reaction('RE14',[C6H14,O2,CO2,H2O],[-2,-19,12,14])
    RE15=Reaction('RE15',[CO,O2,CO2],[-2,-1,2])
    RE16=Reaction('RE16',[H2,O2,H2O],[-2,-1,2])
                                   
    '''Defining Furnace'''
    REX5=Reactor('Fur',StrmAN1,StrmFG1,[E1,E3,E4,E7,E8,E9],[RE9,RE10,RE11,RE12,RE13,RE14,RE15,RE16],ExoEndoFlag=-1)
    REX5.Describe='Furnace'
    ListUnits.append(REX5)
                 
    ''' Defining Stream W5 ()'''
    FU_W5=Sensor('FU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W5=Sensor('TU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W5=Sensor('PU_W5',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW5=FixedConcStream('StrmW5',FU_W5,TU_W5,PU_W5,1,T1,CTag,'xfrac')
    StrmW5.Describe='Combined water from Separators and Fresh water make up'
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
    N2_LT2=Sensor('N2_LT2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT2,CH4:CH4_LT2,CO2:CO2_LT2,H2O:H2O_LT2,N2:N2_LT2,CO:CO_LT2}
    StrmLT2=Material_Stream('StrmLT2',FU_LT2,TU_LT2,PU_LT2,2,T1,CTag2)
    StrmLT2.Describe='Hotside outlet of E-3'
    ListStreams.append(StrmLT2)
     
    '''Defining water from de-aerator to Exchanger E3'''
    FU_W9=Sensor('FU_W9',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W9=Sensor('TU_W9',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W9=Sensor('PU_W9',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW9=FixedConcStream('StrmW9',FU_W9,TU_W9,PU_W9,1,T1,CTag,'xfrac')
    StrmW9.Describe='Water from De-Aerator to Exchanger E3'
    ListStreams.append(StrmW9)
                 
    ''' Defining HEX4 (E3)'''
    HEX4=HeatExchanger('E3',StrmLT1,StrmLT2,StrmW9,StrmW2,Type=0)
    HEX4.Describe='Boiler feed water heat exchanger E3'
    ListUnits.append(HEX4)
                 
    ''' Defining Stream W6 (water from seperator)'''
    FU_W6=Sensor('FU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W6=Sensor('TU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W6=Sensor('PU_W6',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW6=FixedConcStream('StrmW6',FU_W6,TU_W6,PU_W6,1,T1,CTag,'xfrac')
    StrmW6.Describe='Water obtained from all the separators'
    ListStreams.append(StrmW6)
                 
    '''Defining Stream LT3 (To be redefined)'''
    FI3112=Sensor('FI3112',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3142=Sensor('TI3142',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3135=Sensor('PIC3135',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    H2_LT3=Sensor('H2_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CH4_LT3=Sensor('CH4_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO_LT3=Sensor('CO_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CO2_LT3=Sensor('CO2_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    N2_LT3=Sensor('N2_LT3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:H2_LT3,CH4:CH4_LT3,CO2:CO2_LT3,N2:N2_LT3,CO:CO_LT3}
    StrmLT3=Material_Stream('StrmLT3',FI3112,TI3142,PIC3135,2,T1,CTag2)
    StrmLT3.Describe='Gas from LT shift and free from water or steam'
    ListStreams.append(StrmLT3)
                  
    '''Defining Seperator SEP1'''
    SEP1=Seperator('SEP1',StrmLT2,[StrmLT3,StrmW6])
    SEP1.Describe='Lumped Sharp Separator that separates water from the LT shift reactor outlet'
    ListUnits.append(SEP1)
                 
    ''' Defining Stream W7 (fresh water makeup)'''
    FI4119=Sensor('FI4119',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W7=Sensor('TU_W7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W7=Sensor('PU_W7',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW7=FixedConcStream('StrmW7',FI4119,TU_W7,PU_W7,1,T1,CTag,'xfrac')
    StrmW7.Describe='Fresh water make up'
    ListStreams.append(StrmW7)
                 
    '''Defining Mixer MIX6'''
    MIX6=Mixer('MIX6',[StrmW6,StrmW7],StrmW5)
    MIX6.Describe='Mixer that mixes fresh water make up and water from separators'
    ListUnits.append(MIX6)
     
    '''Defining Steam venting from De-aerator'''
    FU_W8=Sensor('FU_W8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_W8=Sensor('TU_W8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_W8=Sensor('PU_W8',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={H2O:1}
    StrmW8=FixedConcStream('StrmW8',FU_W8,TU_W8,PU_W8,1,T1,CTag,'xfrac')
    StrmW8.Describe='Steam from the vent of De-Aerator'
    ListStreams.append(StrmW8)
     
     
    '''Defining Splitter SPL8'''
    SPL8=Splitter('SPL8',StrmW5,[StrmW8,StrmW9])
    SPL8.Describe='Splitter that splits Hydrogen into two streams, one being sent to AO plant and the other to filling'
    ListUnits.append(SPL8)
     
                 
                 
    '''Defining Stream LT5 (Hydrogen rich stream)'''
    FI3114=Sensor('FI3114',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TI3142=Sensor('TI3142',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3160=Sensor('PIC3160',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:1}
    StrmLT5=FixedConcStream('StrmLT5',FI3114,TI3142,PIC3160,2,T1,CTag2,'xfrac')
    StrmLT5.Describe='Hydrogen obtained from PSA unit'
    ListStreams.append(StrmLT5)
                  
    '''Defining Seperator SEP2'''
    SEP2=PSA('PSA',StrmLT3,[StrmLT4,StrmLT5],{(StrmLT5,H2):0.845})
    SEP2.Describe='PSA Unit'
    ListUnits.append(SEP2)
                  
    '''Defining Stream H2 (Hydrogen stream)'''
    FI3122=Sensor('FI3122',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_H2=Sensor('TU_H2',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PIC3161=Sensor('PIC3161',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:1}
    StrmH2=FixedConcStream('StrmH2',FI3122,TU_H2,PIC3161,2,T1,CTag2,'xfrac')
    StrmH2.Describe='Hydrogen to Storage'
    ListStreams.append(StrmH2)
                  
    '''Defining Splitter SPL6'''
    SPL6=Splitter('SPL6',StrmLT5,[StrmH2,StrmH1])
    SPL6.Describe='Splitter that splits Hydrogen from PSA into two streams, one being sent to storage and the other mixed with the NG'
    ListUnits.append(SPL6)
      
    '''Defining Stream H2 (Hydrogen to AO Plant)'''
    FIC3216=Sensor('FIC3216',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_H3=Sensor('TU_H3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_H3=Sensor('PU_H3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:1}
    StrmH3=FixedConcStream('StrmH3',FIC3216,TU_H3,PU_H3,2,T1,CTag2,'xfrac')
    StrmH3.Describe='Hydrogen to AO plant'
    ListStreams.append(StrmH3)
      
    '''Defining Stream H2 (Hydrogen to Filling)'''
    FI1901A=Sensor('FI1901A',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_H4=Sensor('TU_H4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_H4=Sensor('PU_H4',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag2={H2:1}
    StrmH4=FixedConcStream('StrmH4',FI1901A,TU_H4,PU_H4,2,T1,CTag2,'xfrac')
    StrmH4.Describe='Hydrogen to Filling'
    ListStreams.append(StrmH4)
      
    '''Defining Splitter SPL7'''
    SPL7=Splitter('SPL7',StrmH2,[StrmH3,StrmH4])
    SPL7.Describe='Splitter that splits Hydrogen into two streams, one being sent to AO plant and the other to filling'
    ListUnits.append(SPL7)
    
       
     
    '''=============Optimization starts================================'''   
    ToInternalUnits(ListStreams)
    opt1=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=50000)
    GLR1=GLR(opt1,R2.alpha)
    Write2File(ListStreams,'GED.csv')
    GLR1.MakeDetectedFlagUnmeasured(GLR1.Detected,GLR1.XmIndex)
    opt1=ipopt(ListStreams,ListUnits,5,5,1e-8,iter=10000)
    GLR1.RestoreDetectedFlag(GLR1.Detected,GLR1.XmIndex)
#     
#     f1=open('Residuals.csv','w') 
#     Resid=[]
#     for i in ListUnits:
#         Resid.extend(i.MaterialBalRes())
#         Resid.extend(i.ComponentBalRes())
#         f1.write(i.Name +' :'+ i.Describe + '\n')
#         f1.write('Material Balance\n')
#         f1.write(str(i.MaterialBalRes())+'\n')
#         f1.write('Component Balance\n')
#         for j in i.ComponentBalRes():
#             f1.write(str(j)+',')
#         f1.write('\n')
#     f1.close()
        
    ToExternalUnits(ListStreams)
    ftypes=(("Comma separated variable files", "*.csv"),("All files", "*.*"))
    str1 = tkFileDialog.asksaveasfilename(filetypes=ftypes,defaultextension=".xls",initialfile="NPL_Reconciled.csv",title="Select the output file name")
    Write2File(ListStreams,str1)
    print 'here'      
   
    #print'The Maximum constraint violation is ',(max(asarray(Resid)))
    print 'Total no. of Units is ',len(ListUnits)
    print 'Total no. of Streams is ', len(ListStreams)
    print 'Total no. of variables is ',len(opt1.Xopt)
    print 'Total no of Constraints is ',opt1.Glen
    #============================================================
    #==================== Graph generation=======================
    GenerateGraph(ListStreams,ListUnits)