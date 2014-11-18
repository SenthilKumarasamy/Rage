## \class Reaction class is used to define chemical reaction objects. These reaction objects
#  are required to define an Extent of reaction reactor or Equilibrium reactor. 
class Reaction:
    ## \param Name refers to the name of the reaction.
    #  \param Comp is a list of components participating in the reaction. Thus prior to defining
    #   a reaction, the components taking part in the reaction have to be defined.
    #  \param Coef is list of integers that refer to the coefficients of the components in the reaction.
    #   The first integer in \b Coef refers to coefficient of the first component in the \b Comp and so on.
    #   In case of reactant components, the integers must be negative while they are positive for products.
    #   \param EquTempAppFlag is a flag which can take two values namely
    #    \arg \c 1 meaning the specified equilibrium temperature approach is varied during reconciliation.
    #    \arg \c 2 meaning the specified equilibrium temperature approach is kept constant while reconciling.
    #     The default value is two.
    #   \param EquTempApp refers to Equilibrium Temperature Approach. If the reaction is an equilibrium reaction
    #   and it does attain equilibrium, \b EquTempApp can be used to specify the temperature offset. This
    #   temperature offset is added to the reactor outlet temperature while calculating the equilibrium conatant.
    #   The default value of \b EquTempApp is zero.
    #   \par The following validation checks are performed while creating the reaction object.
    #   \arg \c Uniqueness of the components in \b Comp.
    #   \arg \c Equality of number of elements in \b Comp and \b Coef.
    #   \arg \c Stoichiometric balance of the reaction 
    def __init__(self,Name,Comp,Coef,EquTempAppFlag=2,EquTempApp=0.0):
        C=[]
        ## Name of the reaction object
        self.Name = Name
        ## Extent of the reaction.
        self.RxnExt=0.0
        ## Refers to the index of the Extent of reaction (\b RxnExt) in the decision variable vector of the flow sheet.
        #  This index is assigned by the ipopt object at the time of reconciliation.
        self.RxnExtXindex=0
        ##  EquTempAppFlag is a flag which can take two values namely
        #    \arg \c 1 meaning the specified equilibrium temperature approach is varied during reconciliation.
        #    \arg \c 2 meaning the specified equilibrium temperature approach is kept constant while reconciling.
        #     The default value is two.
        self.EquTempAppFlag=EquTempAppFlag
        if (EquTempAppFlag==1):
            ##   EquTempApp refers to Equilibrium Temperature Approach. If the reaction is an equilibrium reaction
            #   and it does attain equilibrium, \b EquTempApp can be used to specify the temperature offset. This
            #   temperature offset is added to the reactor outlet temperature while calculating the equilibrium conatant.
            #   The default value of \b EquTempApp is zero. 
            self.EquTempApp=EquTempApp
            ## Refers to the index of the Equilibrium temperature approach (\b EquTempApp) in the decision variable vector of the flow sheet.
            #  This index is assigned by the ipopt object at the time of reconciliation.
            self.EquTempAppXindex=0
        elif (EquTempAppFlag==2):
            self.EquTempApp=EquTempApp
        
        if (0 in Coef):
            print 'One of the corfficients of a reaction is zero'
            exit()
        for i in Comp:
            if (i not in C):
                C.append(i)
        if (len(C)!=len(Comp)):
            print 'Components of a reaction are not unique'
            exit()
        elif (len(Comp)!=len(Coef)):
            print 'No of components in a reaction and no of coefficients are not matching'
            exit()
        else:
            self.Coef={}
            for ind,i in enumerate(Comp):
                self.Coef[i]=Coef[ind]
        self.Validation()
#------------------------------------------------------------------------------------------------
    ## Checks whether the reaction is balanced or not.
    def Validation(self):
        C=[]
        for i in self.Coef.keys():
            for j in i.MF.keys():
                if (j not in C):
                    C.append(j)
        for i in C:
            sumC=0.0
            for j in self.Coef.keys():
                if (i in j.MF.keys()):
                    sumC=sumC+j.MF[i]*self.Coef[j]
            if (sumC != 0):
                print 'Error in Reaction '+self.Name+' :  ' + 'The reaction is not balanced'
                print 'The elemental balance of '+ '(' + i + ')' +' is not satisfied'
                exit()
                    