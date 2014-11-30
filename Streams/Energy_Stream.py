'''
Created on Jun 19, 2014

@author: Senthil
'''
from Streams.Sensor import Sensor
class Energy_Stream:
    #Xindex=0
    def __init__(self,Name,Q1,Describe=''):
        self.Name=Name
        self.Describe=Describe
        self.Q=Sensor(Q1)
        #self.Q.Flag=0
        #self.Q.Sigma=1
#----------------------------------------------------------------------------------------------