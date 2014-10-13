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
    #str1="C:\\Users\\admin\\workspace\\RAGE2\\src//NPLMeas1.dat"
    str1="D:\\Gyandata\\PythonRage\\RAGE2\\RAGE\\NPLMeas1.dat"
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

    ''' Defining Stream NG3 (3) NG to Desulphurization uint'''
    FI4132=Sensor('FI4132',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    TU_NG3=Sensor('TU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    PU_NG3=Sensor('PU_NG3',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    CTag={CH4:1}
    StrmNG3=FixedConcStream('StrmNG3',FI4132,TU_NG3,PU_NG3,2,T1,CTag,'xfrac')
    ListStreams.append(StrmNG3)
