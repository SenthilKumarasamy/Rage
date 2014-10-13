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
from optim.ipopt import ipopt
from CommonFunctions.Report import Report
from CommonFunctions.ToInternalUnits import ToInternalUnits
from CommonFunctions.ToExternalUnits import ToExternalUnits
from Thermo.Refprop import Refprop

'------------------------------------------------------------------------'


'----------------------------------------------------------------------------------------'
if __name__=="__main__":
    
    '------------------ Reading the Measurement file--------------------'
    str1="D:\\Gyandata\\PythonRage\\RAGE3\\src//Meas.dat"
    R1=Readfile(str1)
    '-----------------------Creating Objects--------------------------------------------'       
    S3F=Sensor('FT103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S3T=Sensor('TT103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S3P=Sensor('PT103',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S3C1=Sensor('CT103a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S3C2=Sensor('CT103b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    # S3C3=Sensor('CT103c',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
    
    S4F=Sensor('FT104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S4T=Sensor('TT104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S4P=Sensor('PT104',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    
    S5F=Sensor('FT105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S5T=Sensor('TT105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S5P=Sensor('PT105',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S5C1=Sensor('CT105a',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S5C2=Sensor('CT105b',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    S5C3=Sensor('CT105c',R1.Name,R1.Meas,R1.Sigma,R1.Flag,R1.Unit)
    
    global ListUnits
    global ListStreams

    N2=Comp(8,StdState=2)
    H2=Comp(4,StdState=2)
    CO=Comp(1,StdState=2)
 
#     T1=IdealGas([N2,H2,CO],'Refprop.dat')#'database.csv')
    T1=Refprop([N2,H2,CO])
    
    
    CTag2={H2:S3C1,N2:S3C2}
    S3=Material_Stream('Inlet1',S3F,S3T,S3P,2,T1,CTag2)#[C1,C2],[S3C1,S3C2])

    CTag={CO:1}
    S4=FixedConcStream('outlet1',S4F,S4T,S4P,2,T1,CTag,'xfrac')
    CTag={H2:S5C1,N2:S5C2,CO:S5C3}
    S5=Material_Stream('S5',S5F,S5T,S5P,2,T1,CTag)

    MIX=Mixer('MiX',[S3,S4],S5)
    ListUints=[MIX]
    ListStreams=[S3,S4,S5]#,B,B1]
#    ToInternalUnits(ListStreams)
    opt1=ipopt(ListStreams,ListUints,7,6,1e-7)

    print MIX.MaterialBalRes(), MIX.EnergyBalRes(), MIX.ComponentBalRes(), MIX.PressureBalRes()
    print S3.Therm.EnthalpyStream(S3)

    for i in ListStreams:
        print i.FTag.Tag,'\t', i.FTag.Meas,'\t', i.FTag.Est
        print i.TTag.Tag, '\t',i.TTag.Meas,'\t', i.TTag.Est
        print i.PTag.Tag,'\t', i.PTag.Meas, '\t',i.PTag.Est
        for j in i.CTag.keys():
            print i.CTag[j].Tag,'\t', i.CTag[j].Meas,'\t', i.CTag[j].Est
    print 'Residuals'

    Report(ListUints)