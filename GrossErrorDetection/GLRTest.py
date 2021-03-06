from numpy import zeros
from numpy import shape
from numpy import asarray
from numpy.linalg import qr
from numpy.linalg import pinv
from numpy.linalg import matrix_rank
from numpy import dot
from scipy.stats import chi2

from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
class GLR():
    def __init__(self,opt):
        self.opt=opt
        rc=self.opt.ConstructJaco(self.opt.Xopt,True)
        val=self.opt.ConstructJaco(self.opt.Xopt,False)
        self.Jac=self.ConstructMatrix(rc,val)
        
        self.Acol,self.Bcol=self.DetermineSizeOfAB(self.opt.XFlag)
        self.A,self.B=self.ExtractAB(self.opt.Glen,self.Acol,self.Bcol,self.Jac,self.opt.XFlag)
        self.Xm,self.Xu,self.XmIndex = self.ExtractXmXu(self.Acol,self.Bcol,self.opt.XFlag,self.opt.Xopt)
        self.Xmeas=self.ExtractXmeas(self.opt.Xmeas, self.XmIndex)
        
        self.P=self.ComputeProjectionMatrix(self.B,self.Bcol,self.opt.Glen)
        self.Abar,self.bbar=self.ComputeAbarbbar(self.A,self.B,self.Xm,self.Xu,self.P)
        self.Sigma=self.ExtractSigma(self.opt.Sigma,self.XmIndex)
        
        self.GLRFlag=zeros((len(self.opt.Xopt)))
        self.r,self.Vinv=self.ComputeRVinv(self.Abar,self.bbar,self.Xmeas,self.Sigma)
        self.Detectable,self.NotDetectable=self.MakeList(self.Abar)
        self.n=matrix_rank(self.Abar)
        self.T0=self.ComputeGlobalStatistic(self.r,self.Vinv,0.0)
        
        self.Ti=self.T0
        self.Detected=[]
        self.ToBeTested=self.Detectable
        Result=True
        while(Result):
            Result=self.GlobalTest(self.Ti,self.n)
            if (Result):
                ErrPos,Tk=self.DetectGEPosition(self.r,self.Vinv,self.Abar,self.Detected,self.ToBeTested)
                self.Detected,self.ToBeTested=self.UpdateList(self.Detected,self.ToBeTested,ErrPos)
                self.Ti=self.ComputeGlobalStatistic(self.r,self.Vinv,Tk)
                self.n=self.n-1
            else:
                break
        self.WriteGLRFlag2Sensors(self.Detected,self.XmIndex)
        self.XmIndex=asarray(self.XmIndex)
    
    def ConstructMatrix(self,rc,val):
        J=zeros((self.opt.Glen,self.opt.Xlen))
        Jrow=rc[0]
        Jcol=rc[1]
        for i in range(len(Jrow)):
            J[Jrow[i]][Jcol[i]]=val[i]
        return J
    
    def DetermineSizeOfAB(self,XFlag):
        Acol=0
        Bcol=0
        for ind,i in enumerate(XFlag):
            if (i==1):
                Acol=Acol+1
            else: 
                Bcol=Bcol+1
        return Acol,Bcol
    
    def ExtractAB(self,Glen,Acol,Bcol,Jac,XFlag):
        A=zeros((Glen,Acol))
        B=zeros((Glen,Bcol))
        Aind=0
        Bind=0
        for ind,i in enumerate(XFlag):
            if (i==1):
                A[:,Aind]=Jac[:,ind]
                Aind=Aind+1
            else:
                B[:,Bind]=Jac[:,ind]
                Bind=Bind+1
        return A,B
    
    def ExtractXmXu(self,Acol,Bcol,XFlag,Xopt):
        Xm=zeros((Acol))
        Xu=zeros((Bcol))
        XmIndex=[0]*Acol
        Aind=0
        Bind=0
        for ind,i in enumerate(XFlag):
            if (i==1):
                Xm[Aind]=Xopt[ind]
                XmIndex[Aind]=ind
                Aind=Aind+1
            else:
                Xu[Bind]=Xopt[ind]
                Bind=Bind+1
        return Xm,Xu,XmIndex
    
    def ExtractXmeas(self,Y,XmIndex):
        Xmeas=zeros((len(XmIndex)))
        for ind,i in enumerate(XmIndex):
            Xmeas[ind]=Y[i]
        return Xmeas
    
    def ExtractSigma(self,YSigma,XmIndex):
        Sigma=zeros((len(XmIndex),len(XmIndex)))
        for ind,i in enumerate(XmIndex):
            Sigma[ind,ind]=YSigma[i]
        return Sigma
        
    def ComputeProjectionMatrix(self,B,Bcol,Glen):
        q,r=qr(B,mode='complete')
        P=q[:,Bcol:Glen]
#         if (not P):
#             print 'Projection matrix is empty'
#             exit()
        return P.T
    
    def ComputeAbarbbar(self,A,B,Xm,Xu,P):
        b=dot(A,Xm)+dot(B,Xu)
        Abar=dot(P,A)
        bbar=dot(P,b)
        return Abar,bbar
    
    def ComputeRVinv(self,Abar,bbar,Xmeas,Sigma):
        r=dot(Abar,Xmeas)-bbar
        V=dot(dot(Abar,Sigma),Abar.T)
        Vinv=pinv(V)
        return r,Vinv
    
    def MakeList(self,Abar):
        s=shape(Abar)
        Detectable=[]
        NotDetectable=[]
        for i in range(s[1]):
            fi=Abar[:,i]
            if (sum(fi)==0.0):
                NotDetectable.append(i)
            else:
                Detectable.append(i)
        return Detectable,NotDetectable
    
#     def ComputeTcritical(self,alpha,n):
#         beta=1-(1-alpha)**(1.0/n)
#         Tcritical=chi2.ppf((1-beta),1)
#         return Tcritical
    
    def ComputeGlobalStatistic(self,r,Vinv,Ti):
        T=dot(dot(r.T,Vinv),r)-Ti
        return T
    
    def GlobalTest(self,T,n):
        Tcrit=chi2.ppf(0.05,n)
        if (T>Tcrit):
            GTResult=True
        else:
            GTResult=False
        return GTResult
        
            
    def DetectGEPosition(self,r,Vinv,Abar,Detected,ToBeTested):
        Fk=Abar[:,Detected]
        s=shape(Fk)
        Fki=zeros((s[0],s[1]+1))
        Fki[:,range(s[1])]=Fk
        GLRStatistic=[0]*len(ToBeTested)
        for ind,i in enumerate(ToBeTested):
            Fki[:,s[1]]=Abar[:,i]
            FTemp=dot(dot(Fki.T,Vinv),r)
            FTemp1=pinv(dot(dot(Fki.T,Vinv),Fki))
            GLRStatistic[ind]=dot(dot(FTemp.T,FTemp1),FTemp)
            ErrPos=GLRStatistic.index(max(GLRStatistic))
        return ErrPos,GLRStatistic[ErrPos]
    
    def UpdateList(self,Detected,ToBeTested,PresentError):
        Detected.append(ToBeTested[PresentError])
        ToBeTested.pop(PresentError)
        return Detected,ToBeTested
    
    def WriteGLRFlag2Sensors(self,Detected,XmIndex):
        XmIndex=asarray(XmIndex)
        for i in self.opt.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag ==1):
                    if (i.FTag.Xindex in XmIndex[Detected]):
                        i.FTag.GLRFlag=1
                    else:
                        i.FTag.GLRFlag=0
                else:
                    i.FTag.GLRFlag=2
                    
                if (i.TTag.Flag ==1):
                    if (i.TTag.Xindex in XmIndex[Detected]):
                        i.TTag.GLRFlag=1
                    else:
                        i.TTag.GLRFlag=0
                else:
                    i.TTag.GLRFlag=2
                    
                if (i.PTag.Flag ==1):
                    if (i.PTag.Xindex in XmIndex[Detected]):
                        i.PTag.GLRFlag=1
                    else:
                        i.PTag.GLRFlag=0
                else:
                    i.PTag.GLRFlag=2
                    
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag ==1):
                        if (i.CTag[j].Xindex in XmIndex[Detected]):
                            i.CTag[j].GLRFlag=1
                        else:
                            i.CTag[j].GLRFlag=0
                    else:
                        i.CTag[j].GLRFlag=2
                        
            elif (isinstance(i,Energy_Stream)):
                if (i.Q.Flag ==1):
                    if (i.Q.Xindex in XmIndex[Detected]):
                        i.Q.GLRFlag=1
                    else:
                        i.Q.GLRFlag=0
                else:
                    i.Q.GLRFlag=2
    
    def MakeDetectedFlagUnmeasured(self,Detected,XmIndex):
        for i in self.opt.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag ==1):
                    if (i.FTag.Xindex in XmIndex[Detected]):
                        i.FTag.Flag=0
                        i.FTag.GLRFlag=-1
                    
                if (i.TTag.Flag ==1):
                    if (i.TTag.Xindex in XmIndex[Detected]):
                        i.TTag.Flag=0
                        i.TTag.GLRFlag=-1
                    
                if (i.PTag.Flag ==1):
                    if (i.PTag.Xindex in XmIndex[Detected]):
                        i.PTag.Flag=0
                        i.PTag.GLRFlag=-1
                    
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag ==1):
                        if (i.CTag[j].Xindex in XmIndex[Detected]):
                            i.CTag[j].Flag=0
                            i.CTag[j].GLRFlag=-1
                        
            elif (isinstance(i,Energy_Stream)):
                if (i.Q.Flag ==1):
                    if (i.Q.Xindex in XmIndex[Detected]):
                        i.Q.Flag=0
                        i.Q.GLRFlag=-1
                        
    def RestoreDetectedFlag(self,Detected,XmIndex):
        for i in self.opt.ListStreams:
            if (isinstance(i,Material_Stream) or isinstance(i,FixedConcStream)):
                if (i.FTag.Flag ==0):
                    if (i.FTag.Xindex in XmIndex[Detected]):
                        i.FTag.Flag=1
                    
                if (i.TTag.Flag ==0):
                    if (i.TTag.Xindex in XmIndex[Detected]):
                        i.TTag.Flag=1
                    
                if (i.PTag.Flag ==0):
                    if (i.PTag.Xindex in XmIndex[Detected]):
                        i.PTag.Flag=1
                    
                for j in i.CTag.keys():
                    if (i.CTag[j].Flag ==0):
                        if (i.CTag[j].Xindex in XmIndex[Detected]):
                            i.CTag[j].Flag=1
                        
#             elif (isinstance(i,Energy_Stream)):
#                 if (i.Q.Flag ==0):
#                     if (i.Q.Xindex in XmIndex[Detected]):
#                         i.Q.Flag=1