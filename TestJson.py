from Streams.Readfile import Readfile
from Streams.Sensor import Sensor
from Streams.Comp import Comp
from Streams.Material_Stream import Material_Stream
from Thermo.IdealGas import IdealGas
from Units.Splitter import Splitter
from Units.Seperator import Seperator 
from optim.ipopt import ipopt

a={"Comp": [1, 2], "Sensor": ["FT101", "TT101", "PT101", "CT101a", "CT101b", "FT103", "TT103", "PT103", "CT103a", "CT103b", "FT104", "TT104", "PT104", "CT104a", "CT104b"], "Uints": [{"Input": 0, "Type": "Splitter", "Name": "Mix", "Output": [1,2]}], "Stream": [{"TTag": "TT101", "CTag": [[1,2],["CT101a","CT101b"]], "FTag": "FT101", "PTag": "PT101"}, {"TTag": "TT103", "CTag": [[1,2],["CT103a","CT103b"]], "FTag": "FT103", "PTag": "PT103"}, {"TTag": "TT104", "CTag": [[1,2],["CT104a","CT104b"]], "FTag": "FT104", "PTag": "PT104"}]}

C=a["Comp"]
Sen=a["Sensor"]
St=a["Stream"]
U=a["Uints"]
str1="D:\\Gyandata\\PythonRage\\RAGE2\\src//Meas.dat"
R1=Readfile(str1)

Comp1=[]
for i in C:
    Comp1.append(Comp(i))

Sen1=[]
for i in Sen:
    Sen1.append(Sensor(i,R1.Name,R1.Meas,R1.Sigma,R1.Flag))


T1=IdealGas(Comp1,'database.csv')


    
Stream=[]
for i in St:
    Cmp=[]
    Ct=[]
    for j in i['CTag'][0]:
        for k in Comp1:
            if (k.Id==j):
                Cmp.append(k)
    for j in i['CTag'][1]:
        for k in Sen1:
            if (k.Tag==j):
                Ct.append(k)
    for j in Sen1:
        if (j.Tag==i['FTag']):
            S1F=j
        elif (j.Tag==i['TTag']):
            S1T=j
        elif (j.Tag==i['PTag']):
            S1P=j
    Stream.append(Material_Stream(S1F,S1T,S1P,1,T1,Cmp,Ct))

Ut=[]
for i in U:
    if (i['Type']=='Splitter'):
        inp=i['Input']
        inpst=[]
        inpst=Stream[inp]
        out=i['Output']
        outst=[]
        for j in out:
            outst.append(Stream[j])
        Ut.append(Seperator(inpst,outst)) 

opt1=ipopt(Stream,Ut,5,6,1e-6)