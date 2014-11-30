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
def GenerateGraph(ListStreams,ListUints):
    ListStreamsName=[]
    ListUintsName=[]
    G=nx.DiGraph()
    
    for i in ListStreams:
        ListStreamsName.append(i.Name)
    
    for i in ListUints:
        G.add_node(i.Name)
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
                G.add_node(Str1)
                #Dic={'Name':i.Name}
                if (not G.has_edge(Str1,InUint)):
                    G.add_edge(Str1,InUint,Name=i.Name)
                else:
                    print 'The Edge is present', Str1, InUnit, '. The stream is ',i.Name
                    print 'The Stream that is alredy present is ',G[Str1][InUint]
                    exit()
                ListStart.append(i)
            elif (InUint ==[] and OutUint != []):
                Str1='End'+str(len(ListEnd))
                G.add_node(Str1)
                #Dic={'Name':i.Name}
                if (not G.has_edge(OutUint,Str1)):
                    G.add_edge(OutUint,Str1,Name=i.Name)
                else:
                    print 'The Edge is already present', OutUint,Str1, '. The stream that is being added is ',i.Name
                    print 'The Stream that is alredy present is ',G[OutUint][Str1]
                    exit()
                ListEnd.append(i)
            elif (InUint !=[] and OutUint !=[]):
                #Dic={'Name':i.Name}
                if (not G.has_edge(OutUint,InUint)):
                    G.add_edge(OutUint,InUint,Name=i.Name)
                else:
                    print 'The Edge is already present',OutUint,InUint, '. The stream is ',i.Name
                    print 'The Stream that is alredy present is ',G[OutUint][InUint]
                    exit()
                ListConnected.append(i)
            else:
                ListFree.append(i)
        else:
            ListEnergy.append(i)
    
    print G.number_of_edges()
    print len(ListConnected)+len(ListEnd)+len(ListStart)
    print len(ListEnergy)
    if (G.number_of_edges()==(len(ListConnected)+len(ListEnd)+len(ListStart))):
        if (G.number_of_nodes()==(len(ListUints)+len(ListEnd)+len(ListStart))): 
            nx.write_gml(G,'graph.gml')
            S=json_graph.node_link_data(G)
            print S
            print 'Successfully built the gml file.'
        else:
            print 'Number of Uints in the flow sheet and number of nodes in the graph do not match'
    else:
        print 'Number of Streams in the flow sheet and Edges in the graph do not match'        