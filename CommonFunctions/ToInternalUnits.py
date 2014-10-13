'''
Created on 30-Jul-2014

@author: admin
'''
#from CommonFunctions import REFPROP as Rp
from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
def ToInternalUnits(ListStreams):
    for i in ListStreams:
        if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
            CUnit=[]
            sumMW=0.0
            for j in i.CTag.keys():
                CUnit.append(i.CTag[j].Unit)
                sumMW=sumMW+i.CTag[j].Est/j.MolWt #i.Therm.MolWtComp(j)
            if (len(set(CUnit))==1):
                if (CUnit[0].upper()=='WFRAC'):
                    for j in i.CTag.keys():
                        i.CTag[j].Est=(i.CTag[j].Est/j.MolWt)/sumMW #i.Therm.MolWtComp(j)
                        i.CTag[j].Meas=(i.CTag[j].Meas/j.MolWt)/sumMW #i.Therm.MolWtComp(j)
                        i.CTag[j].Sigma=(i.CTag[j].Sigma/j.MolWt)/sumMW #i.Therm.MolWtComp(j)
            else:
                print 'Error in Stream: '+i.Name+' Units of the Concentration of the components of the Stream are different'
            
            if (i.PTag.Unit.upper() == 'KG/CM2'):
                i.PTag.Est=(i.PTag.Est+1.03)*98.0665
                i.PTag.Meas=(i.PTag.Meas+1.03)*98.0665
                i.PTag.Sigma=(i.PTag.Sigma+1.03)*98.0665
            
            if (i.FTag.Unit.upper() == 'NM3/HR'):
                Rho= i.Therm.RhoStreamAtNTP(i)
                i.FTag.Est=i.FTag.Est*Rho
                i.FTag.Meas=i.FTag.Meas*Rho
                i.FTag.Sigma=i.FTag.Sigma*Rho
            
            if (i.FTag.Unit.upper() == 'SM3/HR'):
                Rho= i.Therm.RhoStreamAtSTP(i)
                i.FTag.Est=i.FTag.Est*Rho
                i.FTag.Meas=i.FTag.Meas*Rho
                i.FTag.Sigma=i.FTag.Sigma*Rho
            
            if (i.FTag.Unit.upper()=='KG/HR'):
                AvgMW=0.0
                key=i.CTag.keys()
                for j in key:
                    AvgMW=AvgMW+j.MolWt*i.CTag[j].Est
                i.FTag.Est=i.FTag.Est/AvgMW
                i.FTag.Meas=i.FTag.Meas/AvgMW
                i.FTag.Sigma=i.FTag.Sigma/AvgMW
            
            if (isinstance(i,Material_Stream)):
                if (i.FreeBasis !=[]):
                    for j in i.CTag.keys():
                        # Dry to wet basis
                        if (i.FreeBasis[0]!=j):
                            i.CTag[j].Est=i.CTag[j].Est*(1.0-i.CTag[i.FreeBasis[0]].Est)
                

