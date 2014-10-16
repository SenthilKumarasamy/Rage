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
Ctol=1e-5
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

for i in List:
    print i.TestResult