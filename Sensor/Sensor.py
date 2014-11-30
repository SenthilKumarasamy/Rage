#from test.test_binop import isnum
class Sensor:
    Tag=[]
    Meas=[]
    Est=[]
    Sigma=[]
    Flag=[]
    Xindex=0
    def __init__(self,Tag,ListTag=[],ListMeas=[],ListSigma=[],ListFlag=[],ListUnit=[]):
        if (not isinstance(Tag,int) and not  isinstance(Tag,float) and (len(ListTag)!=0) and (len(ListMeas)!=0) and (len(ListSigma)) and (len(ListFlag)!=0)):
            if (Tag in ListTag):
                self.Tag=ListTag[ListTag.index(Tag)]
                self.Meas=float(ListMeas[ListTag.index(Tag)])
                self.Sigma=float(ListSigma[ListTag.index(Tag)])
                self.Flag=int(ListFlag[ListTag.index(Tag)])
                self.Est=self.Meas
                self.Sol=self.Meas
                self.Unit=ListUnit[ListTag.index(Tag)]
            else:
                print "Error : in ", Tag," Sensor Tag not found in the Measurement file"
        elif ((isinstance(Tag,int) or isinstance(Tag,float)) and(len(ListTag)==0) and (len(ListMeas)==0) and (len(ListSigma)==0) and (len(ListFlag)==0) and (len(ListUnit)==0)):
            ''' You are expected to give the concentration in mole fraction  '''
            self.Tag=[]
            self.Meas=Tag
            self.Est=Tag
            self.Sigma=1#0.01*Tag
            self.Flag=1.0
            self.Sol=Tag
        elif ((isinstance(Tag,int) or isinstance(Tag,float)) and len(ListFlag)==1):
            self.Tag=[]
            self.Meas=Tag
            self.Est=Tag
            self.Sigma=1#0.01*Tag
            self.Flag=ListFlag[0]
            self.Sol=Tag
            