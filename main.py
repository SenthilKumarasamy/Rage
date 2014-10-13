"""
Created on Jul 3, 2014

@author: Senthil

Description:

What are we testing here?
    7 streams with heat exchanger along with optimisation
"""

'standard modules'
import unittest

' third party modules'
from scipy.optimize import minimize
from numpy import inf
from numpy import array

' adding the locatin of project specific modules'
import os
import sys

basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ".."))
if filepath not in sys.path:
   sys.path.append(filepath)

' project specific modules'
from CommonFunctions import Constraints as Con
from Streams.Readfile import Readfile
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Streams.Therm import Therm
from Streams.Reaction import Reaction
from Streams.Material_Stream import Material_Stream
from Streams.Energy_Stream import Energy_Stream
from Units.Splitter import Splitter
from Units.Heater import Heater
from Units.EquilibriumReactor import EquilibriumReactor
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator


class Test(unittest.TestCase):

    def setUp(self):
        file_name = "Meas.dat"
        file_path = os.path.join(basepath,file_name)
        R1=Readfile(file_path)
        
        S1F=Sensor('FT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S1T=Sensor('TT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S1P=Sensor('PT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S1C1=Sensor('CT100',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S1C2=Sensor('CT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        
        S2F=Sensor('FT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S2T=Sensor('TT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S2P=Sensor('PT101',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S2C1=Sensor('CT102',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S2C2=Sensor('CT103',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        
        S3F=Sensor('FT102',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S3T=Sensor('TT102',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S3P=Sensor('PT102',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S3C1=Sensor('CT104',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        S3C2=Sensor('CT105',R1.Name,R1.Meas,R1.Sigma,R1.Flag)
        
        
        C1=Comp(110)
        C2=Comp(10)
        #Rxn1=Reaction([C1,C2],[-1,1],23,23)
        T1=Therm([C1,C2],0,0,298,101.325)
        
        F=Material_Stream(S1F,S1T,S1P,1,T1,[C1,C2],[S1C1,S1C2])
        T=Material_Stream(S2F,S2T,S2P,1,T1,[C1,C2],[S2C1,S2C2])
        B=Material_Stream(S3F,S3T,S3P,1,T1,[C1,C2],[S3C1,S3C2])
        
        SPL=Seperator(F,[T,B])
        SPL.Residual()
        
        #=======================================================================
        # print SPL.Resid
        #=======================================================================
        
        ListUnits=[SPL]
        ListStreams=[F,T,B]
        Xmeas=Con.ConstructX(ListUnits, ListStreams)
        [XFlag,LUB]=Con.ConstructXFlag(ListUnits, ListStreams)
        Con.Constraints(Xmeas,ListUnits,ListStreams)
        Con.DeconstructX(Xmeas,ListUnits,ListStreams)
        constraint_list = [{"type":"eq", "fun":Con.Constraints, "args":(ListUnits,ListStreams)}]
         
        self.python_result = minimize(Con.Objective, Xmeas, args=(Xmeas,XFlag),method='SLSQP', bounds=LUB, 
                               constraints=constraint_list,options={'disp':True})
        #print self.python_result        

    def testName(self):
        matlab_solution = [1052.5233130216445, 50.0, 101.325, 0.4805881463332304, 0.5194118536667696, 521.3466961132588, 50.0, 101.325, 0.9463956193401194, 0.053604380659880636, 531.1766169083859, 50.0, 101.325, 0.02340087689304514, 0.9765991231069548]
        if self.python_result.success:
            self.assertAlmostEqual(self.python_result.x.tolist(), matlab_solution, places=2)
        else:
            print "optimisation failed"


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()