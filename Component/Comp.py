'''
Created on Jun 19, 2014

@author: Senthil
'''
class Comp:
    Id=[]
    Name=[]
    abcd=[0]*4
    Hos=0
    Sos=0
    StdState=0
    CompIndex=0
    MF={}   #Molecular Formula
    MolWt=0
    def __init__(self, Compid,StdState):
        self.Id = Compid
        self.StdState=StdState
