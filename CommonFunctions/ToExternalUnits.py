from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
def ToExternalUnits(ListStreams):
    for i in ListStreams:
        if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
        
            if (i.FTag.Unit.upper() == 'NM3/HR'):
                Rho= i.Therm.RhoStreamAtNTP(i)
                i.FTag.Est=i.FTag.Est/Rho
                i.FTag.Meas=i.FTag.Meas/Rho
                i.FTag.Sigma=i.FTag.Sigma/Rho
            elif (i.FTag.Unit.upper() == 'SM3/HR'):
                Rho= i.Therm.RhoStreamAtSTP(i)
                i.FTag.Est=i.FTag.Est/Rho
                i.FTag.Meas=i.FTag.Meas/Rho
                i.FTag.Sigma=i.FTag.Sigma/Rho
            elif (i.FTag.Unit.upper()=='KG/HR'):
                AvgMWEst=0.0
                AvgMWMeas=0.0
                key=i.CTag.keys()
                for j in key:
                    AvgMWEst=AvgMWEst+j.MolWt*i.CTag[j].Est
                    AvgMWMeas=AvgMWMeas+j.MolWt*i.CTag[j].Meas
                if (i.FTag.Flag==2):
                    i.FTag.Est=i.FTag.Est*AvgMWMeas
                else:
                    i.FTag.Est=i.FTag.Est*AvgMWEst
                i.FTag.Meas=i.FTag.Meas*AvgMWMeas
                i.FTag.Sigma=i.FTag.Sigma*AvgMWMeas
            CUnit=[]
            sumMW=0.0
            sumMW1=0.0
            for j in i.CTag.keys():
                CUnit.append(i.CTag[j].Unit.upper())
                sumMW=sumMW+i.CTag[j].Est*j.MolWt#i.Therm.MolWtComp(j)
                sumMW1=sumMW1+i.CTag[j].Meas*j.MolWt#i.Therm.MolWtComp(j)
            if (len(set(CUnit))==1):
                if (CUnit[0].upper()=='WFRAC'):
                    for j in i.CTag.keys():
                        i.CTag[j].Est=(i.CTag[j].Est*j.MolWt)/sumMW #i.Therm.MolWtComp(j)
                        i.CTag[j].Meas=(i.CTag[j].Meas*j.MolWt)/sumMW1 #i.Therm.MolWtComp(j)
                        i.CTag[j].Sigma=(i.CTag[j].Sigma*j.MolWt)/sumMW #i.Therm.MolWtComp(j)
            else:
                print 'Error in Stream: '+i.Name+' Units of the Concentration of the components of the Stream are different'
            
            if (i.PTag.Unit.upper() == 'KG/CM2'):
                i.PTag.Est=i.PTag.Est/98.0665-1.03
                i.PTag.Meas=i.PTag.Meas/98.0665-1.03
                i.PTag.Sigma=i.PTag.Sigma/98.0665-1.03
                
            if (isinstance(i,Material_Stream)):
                if (i.FreeBasis !=[]):
                    # Wet to Dry basis
                    for j in i.CTag.keys():
                        if (i.FreeBasis[0]!=j):
                            i.CTag[j].Est=i.CTag[j].Est/(1.0-i.CTag[i.FreeBasis[0]].Est)
            
