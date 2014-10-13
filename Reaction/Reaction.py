'''
Created on Jun 19, 2014

@author: Senthil
'''
class Reaction:
    def __init__(self,Name,Comp,Coef,EqFlag=0):
        C=[]
        self.Name = Name
        self.EqFlag=EqFlag
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
                    