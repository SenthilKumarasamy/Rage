import networkx as nx
from networkx.readwrite import json_graph
import collections as Con
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
class GenerateGraph():
    def __init__(self,ListStreams,ListUints):
        ListStreamsName=[]
        ListUintsName=[]
        G=nx.MultiDiGraph()
        
        for i in ListStreams:
            ListStreamsName.append(i.Name)
        
        for i in ListUints:
            G.add_node(i.Name,Name=i.Name,Description=i.Describe)
            ListUintsName.append(i.Name)
        
        if (len(set(ListStreamsName)) != len(ListStreamsName)):
            print ' Name of the streams are not Uqique'
            Dic=Con.Counter(ListStreamsName)
            for i in Dic.keys():
                    if (Dic[i]>1):
                        print i,'repeated', Dic[i], ' times'
            exit()
        
        if (len(set(ListUintsName)) != len(ListUintsName)):
            print 'Name of the uints are not unique'
            Dic=Con.Counter(ListUintsName)
            for i in Dic.keys():
                    if (Dic[i]>1):
                        print i,'repeated', Dic[i], ' times'
            exit()
        
        ListStart=[]
        ListEnd=[]
        ListConnected=[]
        ListFree=[]
        ListEnergy=[]
        for i in ListStreams:
            InUint=[]
            OutUint=[]
            if (not isinstance(i,Energy_Stream)):
                for j in ListUints:
                    if (isinstance(j,Reactor) or isinstance(j,PreReformer) or isinstance(j,SteamReformer) or isinstance(j,ShiftReactor)):
                        if (i is j.Rstrm):
                            InUint=j.Name
                    elif (isinstance(j,Mixer)):
                        if (i in j.output):
                            InUint=j.Name
                    elif (isinstance(j,Seperator) or isinstance(j,Splitter) or isinstance(j,PSA)):
                        if (i in j.input):
                            InUint=j.Name
                    elif (isinstance(j,Heater)):
                        if (i is j.input):
                            InUint=j.Name
                    elif (isinstance(j,HeatExchanger)):
                        if (i is j.Shellin or i is j.Tubein):
                            InUint=j.Name
                
                for j in ListUints:   
                    if (isinstance(j,Reactor)):
                        if (i is j.Pstrm):
                            OutUint=j.Name
                    elif (isinstance(j,Mixer)):
                        if (i in j.input):
                            OutUint=j.Name
                    elif (isinstance(j,Seperator) or isinstance(j,Splitter) or isinstance(j,PSA)):
                        if (i in j.output):
                            OutUint=j.Name
                    elif (isinstance(j,Heater)):
                        if (i is j.output):
                            OutUint=j.Name
                    elif (isinstance(j,HeatExchanger)):
                        if (i is j.Shellout or i is j.Tubeout):
                            OutUint=j.Name
                            
                if (InUint !=[] and OutUint ==[]):
                    Str1='Start'+str(len(ListStart))
                    G.add_node(Str1,Name=i.Name)
                    G.add_edge(Str1,InUint,Name=i.Name,Description=i.Describe)
                    G[Str1][InUint][0]['Flow']='Est: '+str(round(i.FTag.Est,3))+self.MeasFlag(i.FTag)+str(round(i.FTag.Meas,3))+ ' | Units :'+i.FTag.Unit+self.GEFlag(i.FTag)
                    for j in i.CTag.keys():
                        a=j.MFStr
                        #G[Str1][InUint][0][a]=str(round(i.CTag[j].Est,2))+' ' + i.CTag[j].Unit
                        G[Str1][InUint][0][a]='Est: '+str(round(i.CTag[j].Est,4))+self.MeasFlag(i.CTag[j])+str(round(i.CTag[j].Meas,4))+ ' | Units :'+i.CTag[j].Unit+self.GEFlag(i.CTag[j])
                    ListStart.append(i)
                elif (InUint ==[] and OutUint != []):
                    Str1='End'+str(len(ListEnd))
                    G.add_node(Str1,Name=i.Name)
                    G.add_edge(OutUint,Str1,Name=i.Name,Description=i.Describe)
                    G[OutUint][Str1][0]['Flow']='Est: '+str(round(i.FTag.Est,3))+self.MeasFlag(i.FTag)+str(round(i.FTag.Meas,3))+ ' | Units :'+i.FTag.Unit+self.GEFlag(i.FTag)
                    for j in i.CTag.keys():
                        a=j.MFStr
                        #G[OutUint][Str1][0][a]=str(round(i.CTag[j].Est,2))+' ' + i.CTag[j].Unit
                        G[OutUint][Str1][0][a]='Est: '+str(round(i.CTag[j].Est,4))+self.MeasFlag(i.CTag[j])+str(round(i.CTag[j].Meas,4))+ ' | Units :'+i.CTag[j].Unit+self.GEFlag(i.CTag[j])
                    ListEnd.append(i)
                elif (InUint !=[] and OutUint !=[]):
                    G.add_edge(OutUint,InUint,Name=i.Name,Description=i.Describe)
                    G[OutUint][InUint][0]['Flow']='Est: '+str(round(i.FTag.Est,3))+self.MeasFlag(i.FTag)+str(round(i.FTag.Meas,3))+ ' | Units :'+i.FTag.Unit+self.GEFlag(i.FTag)
                    for j in i.CTag.keys():
                        a=j.MFStr
                        #G[OutUint][InUint][0][a]=str(round(i.CTag[j].Est,2))+' ' + i.CTag[j].Unit
                        G[OutUint][InUint][0][a]='Est: '+str(round(i.CTag[j].Est,4))+self.MeasFlag(i.CTag[j])+str(round(i.CTag[j].Meas,4))+ ' | Units :'+i.CTag[j].Unit+self.GEFlag(i.CTag[j])
                    ListConnected.append(i)
                else:
                    ListFree.append(i)
            else:
                ListEnergy.append(i)
        if (G.number_of_edges()==(len(ListConnected)+len(ListEnd)+len(ListStart))):
            if (G.number_of_nodes()==(len(ListUints)+len(ListEnd)+len(ListStart))): 
                #nx.write_gml(G,'graph1.graphml')
                nx.freeze(G)
                nx.readwrite.write_graphml(G,"Graph1.graphml")
                #S=json_graph.node_link_data(G)
                print 'Successfully built the gml file.'
            else:
                print 'Number of Uints in the flow sheet and number of nodes in the graph do not match'
        else:
            print 'Number of Streams in the flow sheet and Edges in the graph do not match'
        self.G=G
        #return G
    def MeasFlag(self,Sensor1):
        if (Sensor1.Flag==0):
            S=' | Guess: '
        elif (Sensor1.Flag==1):
            S=' | Meas: '
        elif (Sensor1.Flag==2):
            S=' |Const: '
        return S
    def GEFlag(self,Sensor1):
        if (Sensor1.GLRFlag==0):
            S=' |GE: Absent.'
        elif (Sensor1.GLRFlag in [-1,1]):
            S=' |GE: Corrected.'
        elif (Sensor1.GLRFlag==2):
            S=' |GE: Cannot be detected.'
        return S
                