import collections as Con
from xlrd import *

from Component.Comp import Comp
from Thermo.Refprop import Refprop
from Reaction.Reaction import Reaction
from Sensor.Sensor import Sensor
from Streams.FixedConcStream import FixedConcStream
from Streams.Material_Stream import Material_Stream
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
class ReadFlowSheet():
    def __init__(self,File):
        self.ListComp=self.GetComponents(File)
        self.Thermo=Refprop(self.ListComp)
        self.ListRxn=self.GetReactions(File)
        self.ListSensors=self.GetSensors(File)
        self.ListStrm=self.GetStreams(File)
        self.ListUnit=self.GetUnits(File)
        
        
    def GetComponents(self,File):
        book=open_workbook(File)
        sheet=book.sheet_by_index(0)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.CompNameStr=[]
        Id=[]
        StdState=[]
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.CompNameStr.append(sheet.cell(i,0).value)
                Id.append(int(sheet.cell(i,1).value))
                StdState.append(int(sheet.cell(i,2).value))
        if (len(self.CompNameStr)!=len(set(self.CompNameStr))):
            print ('Some of the Component Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.CompNameStr)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        elif (len(Id)!=len(set(Id))):
            print ('Some of the Component Ids are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(Id)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        else:
            ListComp=[]
            for ind,i in enumerate(Id):
                C1=Comp(i,StdState=StdState[ind])
                ListComp.append(C1)
            return ListComp
        
    def GetReactions(self,File):
        book=open_workbook(File)
        sheet=book.sheet_by_index(1)
        nrow=sheet.nrows
        ncol=sheet.ncols
        if (nrow != 0):
            self.RxnName=[]
            ListCompRxn=[]
            ListCoefRxn=[]
            EquTempAppFlag=[]
            EquTempApp=[]
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.RxnName.append(sheet.cell(i,0).value)
                ListCompRxn.append(self.ProcessCompStrForRxn(sheet.cell(i,1).value))
                ListCoefRxn.append(self.ProcessCoefStrForRxn(sheet.cell(i,2).value))
                EquTempAppFlag.append(int(sheet.cell(i,3).value))
                EquTempApp.append(float(sheet.cell(i,4).value))
        if (len(self.RxnName)!=len(set(self.RxnName))):
            print ('Some of the Component Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.RxnName)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        else:
            ListRxn=[]
            for ind,i in enumerate(self.RxnName):
                ListRxn.append(Reaction(i,ListCompRxn[ind],ListCoefRxn[ind],EquTempAppFlag=EquTempAppFlag[ind],EquTempApp=EquTempApp[ind]))
            return ListRxn
    
    def ProcessCompStrForRxn(self,CompStr):
        CompStr=CompStr.replace('(','')
        CompStr=CompStr.replace(')','')
        ListMFStr=CompStr.split(',')
        ListCompRxn=[]
        for i in ListMFStr:
            if (i in self.CompNameStr):
                for j in self.ListComp:
                    if (i==j.MFStr):
                        ListCompRxn.append(j)
                        break
            else:
                print 'Components for some of the reaction is not defined.'
                exit()
        return ListCompRxn
    
    def ProcessCoefStrForRxn(self,CoefStr):
        CoefStr=CoefStr.replace('(','')
        CoefStr=CoefStr.replace(')','')
        ListCoefStr=CoefStr.split(',')
        ListCoefInt=[]
        for i in ListCoefStr:
            ListCoefInt.append(int(i))
        return ListCoefInt
    
    def GetSensors(self,File):
        book=open_workbook(File)
        sheet=book.sheet_by_index(2)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.SensorName=[]
        Meas=[]
        Sigma=[]
        MFlag=[]
        Units=[]
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.SensorName.append(sheet.cell(i,0).value)
                Meas.append(float(sheet.cell(i,1).value))
                Sigma.append(float(sheet.cell(i,2).value))
                MFlag.append(int(sheet.cell(i,3).value))
                Units.append(sheet.cell(i,4).value)
        
        if (len(self.SensorName)!=len(set(self.SensorName))):
            print ('Some of the Component Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.SensorName)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        else:
            ListSensor=[]
            for i in self.SensorName:
                ListSensor.append(Sensor(i,self.SensorName,Meas,Sigma,MFlag,Units))
            return ListSensor
        
    def GetStreams(self,File):
        book=open_workbook(File)
        sheet=book.sheet_by_index(3)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.StrmName=[]
        Description=[]
        Type=[]
        FTag=[]
        TTag=[]
        PTag=[]
        CTag=[]
        CTagUnit=[]
        FreeBasis=[]
        State=[]
        print nrow,ncol
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.StrmName.append(sheet.cell(i,0).value)
                Description.append(sheet.cell(i,1).value)
                Type.append(sheet.cell(i,2).value)
                FTag.append(self.ProcessFTag(sheet.cell(i,3).value,Type[-1]))
                TTag.append(self.ProcessTTag(sheet.cell(i,4).value,Type[-1]))
                PTag.append(self.ProcessPTag(sheet.cell(i,5).value,Type[-1]))
                CTag.append(self.ProcessCTag(sheet.cell(i,6).value,Type[-1]))
                CTagUnit.append(sheet.cell(i,7).value)
                FreeBasis.append(self.ProcessFB(sheet.cell(i,8).value,Type[-1],CTag[-1]))
                State.append(int(sheet.cell(i,9).value))
        
        if (len(self.StrmName)!=len(set(self.StrmName))):
            print ('Some of the Component Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.StrmName)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        else:
            ListStrm=[]
            for ind,i in enumerate(self.StrmName):
                if (Type[ind]=='FixedComp'):
                    ListStrm.append(FixedConcStream(i,FTag[ind],TTag[ind],PTag[ind],State[ind],self.Thermo,CTag[ind],CTagUnit[ind],Describe=Description[ind]))
                elif (Type[ind]=='MultiComp'):
                    if (isinstance(FreeBasis[ind],Comp)):
                        ListStrm.append(Material_Stream(i,FTag[ind],TTag[ind],PTag[ind],State[ind],self.Thermo,CTag[ind],[FreeBasis[ind]],Describe=Description[ind]))
                    else:
                        ListStrm.append(Material_Stream(i,FTag[ind],TTag[ind],PTag[ind],State[ind],self.Thermo,CTag[ind],Describe=Description[ind]))
                elif (Type[ind]=='Energy'):
                    ListStrm.append(Energy_Stream(i,FTag[ind],Describe=Description[ind]))
                else:
                    print 'Stream type undefined for the stream ', i
            return ListStrm
        
    def ProcessFTag(self,FTag,Type):
        if (Type=='Energy'):
            return float(FTag)
        else:
            if (FTag in self.SensorName):
                for i in self.ListSensors:
                    if (FTag==i.Tag):
                        return i
                        break
            else:
                print 'The flow sensor is not defined ', FTag
    
    def ProcessTTag(self,TTag,Type):
        if (Type=='Energy'):
            return []
        elif (TTag in self.SensorName):
                for i in self.ListSensors:
                    if (TTag==i.Tag):
                        return i
                        break
        else:
            print 'The Temperature sensor is not defined ', TTag
            
    def ProcessPTag(self,PTag,Type):
        if (Type=='Energy'):
            return []
        elif (PTag in self.SensorName):
                for i in self.ListSensors:
                    if (PTag==i.Tag):
                        return i
                        break
        else:
            print 'The Pressure sensor is not defined ', PTag
    
    def ProcessCTag(self,CTag,Type):
        if (Type=='Energy'):
            return []
        elif (Type=='FixedComp'):
            CTag=CTag.replace('[','')
            CTag=CTag.replace(']','')
            CTagList=CTag.split(',')
            Dic={}
            for i in CTagList:
                T1=i.replace('(','')
                T1=T1.replace(')','')
                Tsplit=T1.split(':')
                if (Tsplit[0] in self.CompNameStr):
                    for j in self.ListComp:
                        if (Tsplit[0]==j.MFStr):
                            Comp=j
                            break
                else:
                    print 'Component is not defined'
                    exit()
                Dic[Comp]=float(Tsplit[1])
            return Dic
        elif (Type=='MultiComp'):
            CTag=CTag.replace('[','')
            CTag=CTag.replace(']','')
            CTagList=CTag.split(',')
            Dic={}
            for i in CTagList:
                T1=i.replace('(','')
                T1=T1.replace(')','')
                Tsplit=T1.split(':')
                if (Tsplit[0] in self.CompNameStr):
                    for j in self.ListComp:
                        if (Tsplit[0]==j.MFStr):
                            Comp=j
                            break
                else:
                    print 'Component is not defined'
                    exit()
                if (Tsplit[1] in self.SensorName):
                    for j in self.ListSensors:
                        if (Tsplit[1]==j.Tag):
                            Sen=j
                            break
                else:
                    print 'Sensor not defined'
                    print Tsplit[1]
                    exit()
                Dic[Comp]=Sen
            return Dic
    def ProcessFB(self,FB,Type,CTag):
        if (FB !='[]' and Type=='MultiComp'):
            if (FB in self.CompNameStr):
                for i in CTag.keys():
                    if (FB==i.MFStr):
                        return i
            else:
                print 'Free basis component is not present in the stream'
        else:
            return []
    
    def GetUnits(self,File):        
        book=open_workbook(File)
        sheet=book.sheet_by_index(4)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.UnitName=[]
        Type=[]
        Inlet=[]
        Outlet=[]
        Energy=[]
        Rxn=[]
        ExoEndoFlag=[]
        CTagUnit=[]
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.UnitName.append(sheet.cell(i,0).value)
                Type.append(sheet.cell(i,1).value)
                Inlet.append(self.ProcessStrm(sheet.cell(i,2).value))
                Outlet.append(self.ProcessStrm(sheet.cell(i,3).value))
                Energy.append(self.ProcessStrm(sheet.cell(i,4).value))
                Rxn.append(self.ProcessRxn(sheet.cell(i,5).value,Type[-1]))
                ExoEndoFlag.append(sheet.cell(i,6).value)
        if (len(self.UnitName)!=len(set(self.UnitName))):
            print ('Some of the Component Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.UnitName)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()
        else:
            ListUnit=[]
            for ind,i in enumerate(self.UnitName):
                if (Type[ind]=='Separator'):
                    ListUnit.append(Seperator(i,Inlet[ind][0],Outlet[ind]))
                elif (Type[ind]=='Splitter'):
                    ListUnit.append(Splitter(i,Inlet[ind][0],Outlet[ind]))
                elif (Type[ind]=='Mixer'):
                    ListUnit.append(Mixer(i,Inlet[ind],Outlet[ind][0]))
                elif (Type[ind]=='PSA'):
                    ListUnit.append(PSA(i,Inlet[ind][0],Outlet[ind],Rxn[ind]))
                elif (Type[ind]=='Heater'):
                    ListUnit.append(Heater(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='HeatExchanger'):
                    ListUnit.append(HeatExchanger(i,Inlet[ind][0],Inlet[ind][1],Outlet[ind][0],Outlet[ind][1]))
                elif (Type[ind]=='SteamReformer'):
                    ListUnit.append(SteamReformer(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],Rxn[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='PreReformer'):
                    ListUnit.append(PreReformer(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],Rxn[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='ShiftReactor'):
                    ListUnit.append(ShiftReactor(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],Rxn[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='EquilibriumReactor'):
                    ListUnit.append(EqulibriumReactor(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],Rxn[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='ElementBalanceReactor'):
                    ListUnit.append(ShiftReactor(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],ExoEndoFlag[ind]))
                elif (Type[ind]=='Reactor'):
                    ListUnit.append(Reactor(i,Inlet[ind][0],Outlet[ind][0],Energy[ind],Rxn[ind],ExoEndoFlag[ind]))
                else:
                    print 'Unit type undefined for the stream ', i
            return ListUnit
        
    def ProcessStrm(self,Strm):
        S1=Strm.replace('(','')
        S1=S1.replace(')','')
        S1=S1.split(',')
        StrmList=[]
        for i in S1:
            if (i in self.StrmName):
                for j in self.ListStrm:
                    if (i==j.Name):
                        StrmList.append(j)
                        break
            elif (i=='[]'):
                return []
            else:
                print 'Specified Stream is not defined ', i
                exit()
        return StrmList
    
    def ProcessRxn(self,Rxn,Type):
        if (Type in ['SteamReformer','PreReformer','ShiftReactor','EquilibriumReactor','ElementBalanceReactor','Reactor']):
            S1=Rxn.replace('(','')
            S1=Rxn.replace(')','')
            S1=S1.split(',')
            RxnList=[]
            for i in S1:
                if (i in self.RxnName):
                    for j in self.ListRxn:
                        if (i==j.Name):
                            RxnList.append(j)
                            break
                else:
                    print 'Specified reaction is not defined ', i
                    exit()
            return RxnList
        elif (Type == 'PSA'):
            S1=Rxn.replace('[','')
            S1=S1.replace(']','')
            S1=S1.split(',')
            RxnList=[]
            Dic={}
            for i in S1:
                S2=i.split(':')
                S3=S2[0].replace('(','')
                S3=S3.replace(')','')
                StrmComp=S3.split('#')
                if (StrmComp[0] in self.StrmName):
                    for j in self.ListStrm:
                        if (StrmComp[0]==j.Name):
                            Strm=j
                            break
                else:
                    print 'Specified stream is not defined ',StrmComp[0]
                if (StrmComp[1] in self.CompNameStr):
                    for j in self.ListComp:
                        if (StrmComp[1]==j.MFStr):
                            Comp=j
                            break
                else:
                    print 'Specified Component is not present'
                    exit()
                Dic[(Strm,Comp)]=float(S2[1])
            return Dic
        else:
            return []