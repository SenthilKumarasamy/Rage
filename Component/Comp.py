## This class is used to create a component object.
class Comp:
    ## \param Compid It is the  identiciation number of the component.
    #  \param StdState It is the physical state of the component at standard conditions (25 deg C and 1 atm).
    #  \arg \c 1 refers to liquid state.
    #  \arg \c 2 refers to vapour state.
    def __init__(self, Compid,StdState):
        ## Stores the Identiciation number of the component.
        #  There is a unique \a Id for each component which can be found from the database file.
        self.Id = Compid
        ## Stores the physical state of the component at standard conditions (25 deg C and 1 atm).
        #  \arg \c 1 refers to liquid state.
        #  \arg \c 2 refers to vapour state.
        self.StdState=StdState
        ## Stores the Refprop file name of the component.
        #  This is stored while creating the thermodynamic object such as Refprop.
        self.Name=''
        ## Stores the coefficients of the Cp correlation polynomial.
        #  This is stored while creating the thermodynamic object such as Refprop.
        self.abcd=[0]*4
        ## Stores the Enthalpy offset that need to be added to the enthalpy of the component computed using Refprop.
        #  This is computed while creating the thermodynamic object such as Refprop.
        self.Hos=0
        ## Stores the Entropy offset that need to be added to the entropy of the component computed using Refprop.
        #  This is computed while creating the thermodynamic object such as Refprop.
        self.Sos=0
        ## Stores index of the component in the component list of the thermodynamic object such as Refprop.
        #  This is stored while creating the thermodynamic object such as Refprop.
        self.CompIndex=0
        ## Stores the molecular formula of the component as  a dictionary.
        #  The keys of the dictionary are the symbols of the elements present in the component.
        #  The values of the dictionary refer to the number of atoms of the respective element, present in the component.
        #  This is stored while creating the thermodynamic object such as Refprop.
        self.MF={}
        ## Stores the molecular weight of the component.
        #  This is stored while creating the thermodynamic object such as Refprop.
        self.MolWt=0
