from EX1 import Test1
from EX2 import Test2
from EX3 import Test3
from EX4 import Test4
from EX5 import Test5
from EX6 import Test6
from EX7 import Test7
from EX8 import Test8
from EX9 import Test9
from EX10 import Test10
from EX11 import Test11
from EX12 import Test12
from EX13 import Test13
from EX14 import Test14
from EX15 import Test15
from EX16 import Test16
from EX17 import Test17
from EX18 import Test18
from EX19 import Test19
from EX20 import Test20
from EX21 import Test21
from EX22 import Test22
from EX23 import Test23
from EX24 import Test24
Ctol=1e-5
Ptol=1.0
List=[]
List.append(Test1(Ctol))
List.append(Test2(Ctol))
List.append(Test3(Ctol))
List.append(Test4(Ctol))
List.append(Test5(Ctol))
List.append(Test6(Ctol))
List.append(Test7(Ctol))
List.append(Test8(Ctol))
List.append(Test9(Ctol))
List.append(Test10(Ctol))
List.append(Test11(Ctol))
List.append(Test12(Ctol,Ptol))
List.append(Test13(Ctol,Ptol))
List.append(Test14(Ctol,Ptol))
List.append(Test15(Ctol,Ptol))
List.append(Test16(Ctol,Ptol))
List.append(Test17(Ctol,Ptol))
List.append(Test18(Ctol,Ptol))
List.append(Test19(Ctol,Ptol))
List.append(Test20(Ctol,Ptol))
List.append(Test21(Ctol,Ptol))
List.append(Test22(Ctol,Ptol))
List.append(Test23(Ctol,Ptol))
List.append(Test24(Ctol,Ptol))

for ind,i in enumerate(List):
    print '=============================================================================================================================================================================='
    print 'Example Test Case: ',ind+1
    print 'Problem Description: ',i.Description
    if (i.Type==1):
        print 'Problem Type: Material/Flow Balance'
    elif (i.Type==2):
        print 'Problem Type: Material & Component Balance'
    elif (i.Type==3):
        print 'Problem Type: Material, Component, and Energy Balance'
    elif (i.Type==4):
        print 'Problem Type: Material, Component, Energy, and Pressure Balance'
    elif (i.Type==5):
        print 'Problem Type: Material & Component Balance with Normalization'
    elif (i.Type==6):
        print 'Problem Type: Material, Component, and Energy Balance with Normalization'
    elif (i.Type==7):
        print 'Problem Type: Material, Component, Energy, and Pressure Balance with Normalization'
    if (i.TestResult):
        print 'Result   : Python solution matches with the hard coded Matlab results or the solution.'
    else:
        print 'Result   : Python solution does not match the hard coded Matlab results'
        if (i.TestResultPercentage):
            print '         : But the maximum difference between the python and MatLab results is less than ', Ptol,'%'
        else:
            print '         : But the maximum difference between the python and MatLab results is greater than ', Ptol,'%'
        if (abs(i.OPT.obj)<abs(i.OPT.ObjSol)):
            print '         : The objective function value at optimum of python code is lesser than that of Matlab'
        elif (abs(i.OPT.obj)<abs(i.OPT.ObjSol)):
            print '         : The objective function value at optimum of python code is higher than that of Matlab'
        else:
            print '         : The objective function value at optimum of python code is equal than that of Matlab'
        print '         : Python objective function value at optimum is ',i.OPT.obj
        print '         : MatLab objective function value at optimum is ',i.OPT.ObjSol 
print '===================================================================================================================================================================================='