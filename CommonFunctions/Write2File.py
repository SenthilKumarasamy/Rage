from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
def Write2File(ListStreams,FileName,):
	f=open(FileName,'w')
	for i in ListStreams:
		if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
			f.write(i.Describe +'\n')
			f.write(str(i.FTag.Tag))
			f.write(',')
			f.write(str(i.FTag.Flag))
			f.write(',')
			f.write(str(i.FTag.Meas))
			f.write(',')
			f.write(str(i.FTag.Est))
			f.write(',')
			f.write(str(i.FTag.Sigma))
			f.write(',')
			f.write(str(i.FTag.GLRFlag))
			f.write(',')
			f.write(str(i.FTag.Unit))
			f.write('\n')
			  
			f.write(str(i.TTag.Tag))
			f.write(',')
			f.write(str(i.TTag.Flag))
			f.write(',')
			f.write(str(i.TTag.Meas))
			f.write(',')
			f.write(str(i.TTag.Est))
			f.write(',')
			f.write(str(i.TTag.Sigma))
			f.write(',')
			f.write(str(i.TTag.GLRFlag))
			f.write(',')
			f.write(str(i.TTag.Unit))
			f.write('\n')
			  
			f.write(str(i.PTag.Tag))
			f.write(',')
			f.write(str(i.PTag.Flag))
			f.write(',')
			f.write(str(i.PTag.Meas))
			f.write(',')
			f.write(str(i.PTag.Est))
			f.write(',')
			f.write(str(i.PTag.Sigma))
			f.write(',')
			f.write(str(i.PTag.GLRFlag))
			f.write(',')
			f.write(str(i.PTag.Unit))
			f.write('\n')
			if (isinstance(i,Material_Stream)):
				for j in i.CTag.keys():
					f.writelines(str(i.CTag[j].Tag)+','+str(i.CTag[j].Flag)+','+str(i.CTag[j].Meas)+','+str(i.CTag[j].Est)+','+str(i.CTag[j].Sigma)+','+str(i.CTag[j].GLRFlag)+','+str(i.CTag[j].Unit)+'\n')
	f.close()
    
	