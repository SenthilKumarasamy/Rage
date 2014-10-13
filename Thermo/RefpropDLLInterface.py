## REFPROP8 library
## Bruce Wernick
## info@coolit.co.za
## Last updated: 6 August 2010

#-------------------------------------------------------------------------------
#  temperature                         K
#  pressure, fugacity                  kPa
#  density                             mol/L
#  composition                         mole fraction
#  quality                             mole basis
#  enthalpy, internal energy           J/mol
#  Gibbs, Helmholtz free energy        J/mol
#  entropy, heat capacity              J/(mol-K)
#  speed of sound                      m/s
#  Joule-Thompson coefficient          K/kPa
#  d(p)/d(rho)                         kPa-L/mol
#  d2(p)/d(rho)2                       kPa-(L/mol)2
#  viscosity                           uPa-s
#  thermal conductivity                W/(m-K)
#  dipole moment                       debye
#  surface tension                     N/m
#-------------------------------------------------------------------------------

from ctypes import *
rp = windll.LoadLibrary("C:\\Program Files\\REFPROP\\refprop.dll")
#rp = windll.LoadLibrary("C:\\Program Files (x86)\\REFPROP\\refprop.dll")
k0 = 273.15

MaxComps = 20
#fpath = 'C:/Program Files (x86)/REFPROP/'
fpath = 'c:/program files/refprop/'
fldpath = fpath + 'fluids/'
mixpath = fpath + 'mixtures/'
hfld = create_string_buffer('', 10000)
hfm = create_string_buffer(fpath + 'fluids/hmx.bnc', 255)
hrf = create_string_buffer('DEF', 3)
hfile = create_string_buffer('', 10000)
htype = create_string_buffer('NBS', 3)
hmix = create_string_buffer('NBS', 3)
hcomp = create_string_buffer('NBS', 3)
ierr = c_long(0)
herr = create_string_buffer('', 255)
hname = create_string_buffer('', 12)
hn80 = create_string_buffer('', 80)
hcas = create_string_buffer('', 12)
nc = c_long(1)
wm = c_double()
x = (c_double * MaxComps)(1)
xl = (c_double * MaxComps)()
xv = (c_double * MaxComps)()
xlkg = (c_double * MaxComps)()
xvkg = (c_double * MaxComps)()


# -- INITIALIZATION SUBROUTINES --

def SETPATH(value=fpath):
  '''set path to refprop root containing fluids and mixtures'''
  global fpath, fldpath, mixpath
  fpath = value
  fldpath = fpath + 'fluids/'
  mixpath = fpath + 'mixtures/'

def SETUP(FluidName, FluidRef='DEF'):
    '''define models and initialize arrays'''
    global ierr, herr
    global nc, hfld, hfm, hrf, wm
    nc.value = len(FluidName)
    hfld.value=""
    for i in range(len(FluidName)-1):
        hfld.value=hfld.value + fldpath + FluidName[i] + '|'
    hfld.value=hfld.value + fldpath + FluidName[len(FluidName)-1]
    hrf.value = FluidRef
    rp.SETUPdll(byref(nc), byref(hfld), byref(hfm), byref(hrf), byref(ierr), byref(herr), c_long(10000), c_long(255), c_long(3), c_long(255))
    if ierr.value == 0:
        ixflag = c_long(1)
        h0, s0, t0, p0 = c_double(0), c_double(0), c_double(0), c_double(0)
        rp.SETREFdll(byref(hrf), byref(ixflag), x, byref(h0), byref(s0), byref(t0), byref(p0), byref(ierr), byref(herr), c_long(3), c_long(255))

def PUREFLD(icomp=0):
  '''Change the standard mixture setup so that the properties of one fluid can
  be calculated as if SETUP had been called for a pure fluid'''
  icomp = c_long(icomp)
  rp.PUREFLDdll(byref(icomp))
  return
  
def WMOL(xfrac):
    '''molecular weight of mixture'''
    global wm, x
    for i in range(len(xfrac)):
        x[i]=xfrac[i]
    rp.WMOLdll(x, byref(wm))
    return wm.value

def PREOS(i):
    temp=c_long(i)
    rp.PREOSdll(byref(temp))

def TPRHO(t, p, xfrac, kph=2, kguess=0, D=0):
    '''iterate for density as a function of temperature, pressure, and composition for a specified phase
     kph--phase flag: 1=liquid 2=vapor
     NB: 0 = stable phase--NOT ALLOWED (use TPFLSH) (unless an initial guess is supplied for D)
        -1 = force the search in the liquid phase
        -2 = force the search in the vapor phase
     kguess--input flag:
         1 = first guess for D provided
         0 = no first guess provided
     D--first guess for molar density [mol/L], only if kguess=1'''
    global ierr, herr
    for i in range(len(xfrac)):
        x[i]=xfrac[i]
    t = c_double(t)
    p = c_double(p)
    kph = c_long(kph)
    kguess = c_long(kguess)
    D = c_double(D)  
    rp.TPRHOdll(byref(t), byref(p), x, byref(kph), byref(kguess), byref(D), byref(ierr), byref(herr), c_long(255))
    return D.value,ierr.value

def SATT(t, xfrac, kph=2):
    '''iterate for saturated liquid and vapor states given temperature
     kph--phase flag: 1=bubblepoint, 2=dewpoint, 3=freezingpoint, 4=sublimationpoint'''
    global ierr, herr
    global xl, xv
    t = c_double(t)
    kph = c_long(kph)
    p = c_double()
    Dl, Dv = c_double(), c_double()
    for i in range(len(xfrac)):
        x[i]=xfrac[i]
    rp.SATTdll(byref(t), x, byref(kph), byref(p), byref(Dl), byref(Dv), xl, xv, byref(ierr), byref(herr), c_long(255))
    #return p.value, Dl.value, Dv.value
    return p.value,ierr.value

def ENTHAL(t, xfrac, D):
    '''enthalpy as a function of temperature and density'''
    for i in range(len(xfrac)):
        x[i]=xfrac[i]  
    t = c_double(t)
    D = c_double(D)
    h = c_double()
    rp.ENTHALdll(byref(t), byref(D), x, byref(h))
    return h.value

def ENTRO(t, xfrac, D):
    '''entropy as a function of temperature and density'''
    for i in range(len(xfrac)):
        x[i]=xfrac[i]  
    t = c_double(t)
    D = c_double(D)
    s = c_double()
    rp.ENTROdll(byref(t), byref(D), x, byref(s))
    return s.value

def FGCTY(t, xfrac, D):
    '''fugacity for each of the nc components of a mixture by numerical
    differentiation (using central differences) of the dimensionless residual
    Helmholtz energy'''
    for i in range(len(xfrac)):
        x[i]=xfrac[i]  
    t = c_double(t)
    D = c_double(D)
    f = (c_double * len(xfrac))()
    rp.FGCTYdll(byref(t), byref(D), x, byref(f))
    return f

def FUGCOF(t,xfrac,D):
    ''' Fugacity Coefficient of the species in a mixture'''
    global ierr,herr
    for i in range(len(xfrac)):
        x[i]=xfrac[i]  
    t = c_double(t)
    D = c_double(D)
    f = (c_double * len(xfrac))()
    rp.FUGCOFdll(byref(t),byref(D),x,byref(f),byref(ierr), byref(herr), c_long(255))
    return f,ierr.value

def SETREF(FluidRef,ixflag, h0, s0, t0, p0, xfrac=[]):
    '''set reference state enthalpy and entropy'''
    global ierr, herr
    global hrf
    if (xfrac is not None):
        for i in range(len(xfrac)):
            x[i]=xfrac[i]
    else:
        x[0]=1  
    hrf.value = FluidRef
    ixflag = c_long(ixflag)
    h0, s0, t0, p0 = c_double(h0), c_double(s0), c_double(t0), c_double(p0)
    rp.SETREFdll(byref(hrf), byref(ixflag), x, byref(h0), byref(s0), byref(t0), byref(p0), byref(ierr), byref(herr), c_long(3), c_long(255))
    return
def SETAGA():
    rp.SETAGAdll(byref(ierr),byref(herr),c_long(255))
    return ierr

# def TPFLSH(t, p, xfrac):
#     '''flash calculation given temperature and pressure'''
#     global ierr, herr
#     global xl, xv
#     for i in range(len(xfrac)):
#         x[i]=xfrac[i]  
#     t = c_double(t)
#     p = c_double(p)
#     D, Dl, Dv = c_double(), c_double(), c_double()
#     q, e, h, s = c_double(), c_double(), c_double(), c_double()
#     cv, cp = c_double(), c_double()
#     w = c_double()
#     rp.TPFLSHdll(byref(t), byref(p), x, byref(D), byref(Dl), byref(Dv), xl, xv, byref(q), byref(e), byref(h), byref(s), byref(cv), byref(cp), byref(w), byref(ierr), byref(herr), c_long(255))
#     #return D.value, Dl.value, Dv.value, q.value, e.value, h.value, s.value, cv.value, cp.value, w.value
#     return q.value

#SETUP(Ls,'DEF')
#print WMOL([0.5,0.25,0.25])
#print TPRHO(400,101.325,[0.5,0.25,0.25],2,0,0)