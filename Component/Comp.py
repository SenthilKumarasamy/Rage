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
    
    ## This function converts a string representing a molecular formula to a dictionary.
    #  \param str is a string representing the molecular formula of the component such as 'H2O', '(NH4)2CO3'
    #  \returns a dictionary with keys being the symbols of the elements present in the component and
    #   the values being the number of atoms of the respective element present in the component.
    def Str2Dic(self,str):
        ## \var ElementList has to be updated to include all the elements.
        ElementList=['C','H','O','S','N','He','Ar','Cl','Br','Ca','P'] 
        start=[]
        end=[]
        val=[]
        strlen=len(str)
        DigitCount=0
        for i in range(strlen):
            if (i==0):
                start.append(i)
            elif (str[i].isupper()):
                if (DigitCount==0): 
                    end.append(i-1)
                    val.append(1)
                    start.append(i)
                else:
                    end.append(i-DigitCount -1)
                    val.append(int(str[i-DigitCount:i]))
                    start.append(i)
                    DigitCount=0
            elif (str[i].isdigit()):
                DigitCount=DigitCount+1
            if (i==(strlen-1)):
                if (DigitCount==0):
                    end.append(i)
                    val.append(1)
                else:
                    end.append(i-DigitCount)
                    val.append(int(str[i-DigitCount+1:i+1]))
                    DigitCount=0
        '''Extracting the Symbols from the string '''            
        Temp=[]
        for i in range(len(start)):
            Temp.append(str[start[i]:end[i]+1])
        '''Validation of the symbols and creating a unique list of symbol '''
        Element=[]
        ElementIndex=[]
        for ind,i in enumerate(Temp):
            if (i not in ElementList):
                print 'Invalid Symbol for an element of a Component'
                exit()
            if (i not in Element):
                Element.append(i)
                ElementIndex.append(val[ind])
            else:
                ElementIndex[Element.index(i)]=ElementIndex[Element.index(i)]+val[ind]
        ''' Creating a dictionary'''
        Dic={}
        for ind,i in enumerate(Element):
            Dic[i]=ElementIndex[ind]
        return Dic