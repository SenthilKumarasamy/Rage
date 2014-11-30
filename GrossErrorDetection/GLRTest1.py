# from numpy import zeros
# from numpy import shape
# from numpy import asarray
# from numpy.linalg import inv
# from numpy.linalg import *
# from numpy.linalg import svd
# from numpy import dot
# from numpy import bmat
# from numpy import mat
# from numpy import eye
# from scipy.stats import chi2
import numpy
import scipy.stats as st


from Streams.Material_Stream import Material_Stream
from Streams.FixedConcStream import FixedConcStream
from Streams.Energy_Stream import Energy_Stream
## This class is used to create Generalizied Likelihood Ratio (GLR) object that is used to detect Gross Errors (GE).
class GLR():
    ## \param opt is an ipopt object.
    def __init__(self,opt,alpha):
        ## Stores the ipopt object.
        self.opt=opt
        self.alpha=alpha
        
        ## \var rc stores the non zero positions of the Jacobian.
        rc=self.opt.ConstructJaco(self.opt.Xopt,True)
        
        ## \var val stores the values of the non zero positions of the Jacobian evaluated at the optimum.
        val=self.opt.ConstructJaco(self.opt.Xopt,False)
        
        ## Stores the complete Jacobian matrix evaluated at optimum.
        self.Jac=self.ConstructMatrix(rc,val)
        
        ## \b Acol and \b Bcol stores the no. of columns of \b A and \b B matrices.
        #  \b A and \b B are the submatrices of the \b Jac jacobian evaluated at the optimum.
        self.Acol,self.Bcol=self.DetermineSizeOfAB(self.opt.XFlag)
        
        ## \b A and \b B are the submatrices of the \b Jac jacobian evaluated at the optimum.
        self.A,self.B=self.ExtractAB(self.opt.Glen,self.Acol,self.Bcol,self.Jac,self.opt.XFlag)
        
        ## \b Xm and \b Xu are the subvectors of \b Xopt, the optimal vector.
        #  \b XmIndex contains the indices of the elements of \b Xm in \b Xopt.
        self.Xm,self.Xu,self.XmIndex = self.ExtractXmXu(self.Acol,self.Bcol,self.opt.XFlag,self.opt.Xopt)
        
        ## \b Xmeas contains the measurements corresconding to the elements of \b Xm, the estimates of the measurements.
        self.Xmeas=self.ExtractXmeas(self.opt.Xmeas, self.XmIndex)
        
        ## \b G is function of \b Xm.
        self.G=self.FunctionG(self.Xm, self.XmIndex, self.opt.FBFlag)
        
        ## \b J is the Jacobian of \b G.
        self.J=self.GradientG(self.Xm, self.XmIndex, self.opt.FBFlag)
        
        ## \b Abar and \b bbar are the transformed \b A and \b b respectively, where AX=b is the constraint.
        #  In case of non-linear constraints, AX=b represents the linearized form.
        self.Abar,self.bbar=self.ComputeMatrixM(self.A, self.B, self.G,self.J,self.Xm,self.Xu)
        
        #self.P=self.ComputeProjectionMatrix(self.B,self.Bcol,self.opt.Glen)
        #self.Abar,self.bbar=self.ComputeAbarbbar(self.A,self.B,self.Xm,self.Xu,self.P)
        
        ## Stores the standard deviation of measurement noise.
        self.Sigma=self.ExtractSigma(self.opt.Sigma,self.XmIndex)
        
        ## Stors the Gross Error (GE) flag about the measurement.
        #  \arg \c 0 meaning no gross error is present in the particular measurement.
        #  \arg \c 1 or -1 meaning gross error is present in the particular measurement.
        #  \arg \c 2 meaning gross error can not be detected in the particular measurement. 
        self.GLRFlag=numpy.zeros((len(self.opt.Xopt)))
        
        ## \b r is the residual vector and \b Vinv is the \f$\frac{1}{Cov(r)}\f$.
        self.r,self.Vinv=self.ComputeRVinv(self.Abar,self.bbar,self.Xmeas,self.Sigma)
        
        #self.r,self.Vinv=self.ComputeRVinv(self.Abar,self.bbar,self.Xm,self.Sigma)
        
        ## \b Detectable and \b NotDetectable are the list of sensors having and not having gross error.
        self.Detectable,self.NotDetectable=self.MakeList(self.Abar)
        
        ## \b n is the rank of the matrix \b Abar.
        self.n=numpy.linalg.matrix_rank(self.Abar)
        
        ## Test Statistic of the first sensor in the list.
        self.T0=self.ComputeGlobalStatistic(self.r,self.Vinv,0.0)
        
        ## Test Statistic of the current sensor. 
        self.Ti=self.T0
        self.Detected=[]
        
        ## List of sensors to be tested.
        self.ToBeTested=self.Detectable
        
        Result=True
        while(Result and self.n!=0):
            Result=self.GlobalTest(self.Ti,self.n)
            if (Result):
                ErrPos,Tk=self.DetectGEPosition(self.r,self.Vinv,self.Abar,self.Detected,self.ToBeTested)
                self.Detected,self.ToBeTested=self.UpdateList(self.Detected,self.ToBeTested,ErrPos)
                self.Ti=self.ComputeGlobalStatistic(self.r,self.Vinv,Tk)
                self.n=self.n-1
            else:
                break
        self.WriteGLRFlag2Sensors(self.Detected,self.XmIndex)
        self.XmIndex=numpy.asarray(self.XmIndex)
    
    ##  Constructs the full matrix from it's non zero positions and their respective value.
    #   \param rc is the list containing two list. The first one is the list of row indices of non zero entries in the matrix.
    #   The second one is the list of column indices of non zero enteries in the matrix.
    #  \param val is the list of non zero values that corresponds to the positions given in \b rc.
    #  \return J is the full matrix
    def ConstructMatrix(self,rc,val):
        J=numpy.zeros((self.opt.Glen,self.opt.Xlen))
        Jrow=rc[0]
        Jcol=rc[1]
        for i in range(len(Jrow)):
            J[Jrow[i]][Jcol[i]]=val[i]
        return J
    
    ##  Determines the no. of columns in matrix \b A and \b B where \b A and \b B are the submatrices of the matrix \b M 
    #   where MX=b are linearizied constraints. 
    #   \param XFlag is a list containing the measurement flags whose elements may be 0 or 1 or 2 meaning unmeasured,measured, and constant.
    #   \return integers \b Acol and \b Bcol which are the no.of columns in A and B respectively.
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
        A=numpy.zeros((Glen,Acol))
        B=numpy.zeros((Glen,Bcol))
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
        Xm=numpy.zeros((Acol))
        Xu=numpy.zeros((Bcol))
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
        Xmeas=numpy.zeros((len(XmIndex)))
        for ind,i in enumerate(XmIndex):
            Xmeas[ind]=Y[i]
        return Xmeas
    
    def ExtractSigma(self,YSigma,XmIndex):
        Sigma=numpy.mat(numpy.zeros((len(XmIndex),len(XmIndex))))
        for ind,i in enumerate(XmIndex):
            Sigma[ind,ind]=YSigma[i]
        return Sigma
    
    def FunctionG(self,Xm,XmIndex,FBFlag):
        G=numpy.zeros((len(XmIndex),1))
        for ind,i in enumerate(XmIndex):
            if (FBFlag[i]==0):
                G[ind]=Xm[ind]
            else:
                G[ind]=Xm[ind]/(1.0-FBFlag[i].Est)
        return G
    
    def GradientG(self,Xm,XmIndex,FBFlag):
        J=numpy.zeros((len(Xm),len(Xm)))
        for ind,i in enumerate(XmIndex):
            if (FBFlag[XmIndex[ind]]==0):
                J[ind][ind]=1.0
            else:
                J[ind][ind]=1.0/(1.0-FBFlag[XmIndex[ind]].Est)
                ''' The following three lines of is effective if the Free Basis component is measured. 
                    Presently, it is forced to be unmeasured while declarine the concerned stream'''
                if (FBFlag[XmIndex[ind]].Flag==1):
                    ind1=XmIndex.index(FBFlag[XmIndex[ind]])
                    J[ind][ind1]=Xm[ind]/(1.0-FBFlag[XmIndex[ind]].Est)**2
        return J
    
    def ComputeMatrixM(self,A,B,G,J,Xm,Xu):
        SizeA=A.shape
        SizeB=B.shape
        SizeD=J.shape
        NrowZ=SizeD[0]
        NcolZ=SizeB[1]
        Z=numpy.mat(numpy.zeros((NrowZ,NcolZ)))
        BM=numpy.bmat([[A,B],[-J,Z]])
        U,S,VT=numpy.linalg.svd(BM.T,full_matrices=True)
        IndStart=S.shape[0]
        IndEnd=VT.shape[0]
        self.P=VT[IndStart:IndEnd,:]
        Z1=numpy.mat(numpy.zeros((SizeA[0],SizeD[0])))
        E1=numpy.mat(numpy.eye(SizeD[0]))
        M1=numpy.bmat([[Z1],[E1]])
        Abar=numpy.dot(self.P,M1)
        c=numpy.dot(A,numpy.mat(Xm).T)+numpy.dot(B,numpy.mat(Xu).T)
        d=G-numpy.dot(J,numpy.mat(Xm).T)
        bbar=numpy.dot(self.P,numpy.bmat([[c],[d]]))
        return Abar,bbar
       
    
    def ComputeRVinv(self,Abar,bbar,Xmeas,Sigma):
        r=numpy.dot(Abar,numpy.mat([Xmeas]).T)-bbar
        V=numpy.dot(numpy.dot(Abar,Sigma),Abar.T)
        Vinv=numpy.linalg.inv(V)
        return r,Vinv
    
    def MakeList(self,Abar):
        s=numpy.shape(Abar)
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
#         #Tcritical=scipy.stats.chi2.ppf((1-beta),1)
#         return Tcritical
    
    def ComputeGlobalStatistic(self,r,Vinv,Ti):
        T=numpy.dot(numpy.dot(r.T,Vinv),r)-Ti
        return T
    
    def GlobalTest(self,T,n):
        Tcrit=st.chi2.ppf((1-self.alpha),n)
        if (T>Tcrit):
            GTResult=True
        else:
            GTResult=False
        return GTResult
        
            
    def DetectGEPosition(self,r,Vinv,Abar,Detected,ToBeTested):
        Fk=Abar[:,Detected]
        s=numpy.shape(Fk)
        Fki=numpy.mat(numpy.zeros((s[0],s[1]+1)))
        Fki[:,range(s[1])]=Fk
        GLRStatistic=[0]*len(ToBeTested)
        for ind,i in enumerate(ToBeTested):
            Fki[:,s[1]]=Abar[:,i]
            FTemp=numpy.dot(numpy.dot(Fki.T,Vinv),r)
            FTempa=numpy.dot(numpy.dot(Fki.T,Vinv),Fki)
            if (numpy.linalg.matrix_rank(FTempa)==min(numpy.shape(FTempa))):
                FTemp1=numpy.linalg.inv(FTempa)
                #FTemp1=numpy.linalg.inv(numpy.dot(numpy.dot(Fki.T,Vinv),Fki))
                GLRStatistic[ind]=numpy.dot(numpy.dot(FTemp.T,FTemp1),FTemp)
        ErrPos=GLRStatistic.index(max(GLRStatistic))# modified
        return ErrPos,GLRStatistic[ErrPos]
    
    def UpdateList(self,Detected,ToBeTested,PresentError):
        Detected.append(ToBeTested[PresentError])
        ToBeTested.pop(PresentError)
#         Fk=self.Abar[:,Detected]
#         s=numpy.shape(Fk)
#         print numpy.linalg.matrix_rank(Fk),min(s)
#         if (numpy.linalg.matrix_rank(Fk)<min(s)):
#             Detected.pop(len(Detected)-1)
        return Detected,ToBeTested
    
    def WriteGLRFlag2Sensors(self,Detected,XmIndex):
        XmIndex=numpy.asarray(XmIndex)
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