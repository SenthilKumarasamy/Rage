'''
Created on 27-Jul-2014

@author: admin
'''
def Str2Dic(str):
    '''Later read this list of elements from a file '''
    List=['C','H','O','S','N','He','Ar','Cl','Br','Ca','P'] 
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
        if (i not in List):
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
    
    
        