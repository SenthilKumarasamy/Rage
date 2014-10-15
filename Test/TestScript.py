from EX1 import Test1
from EX2 import Test2
from EX3 import Test3
from EX4 import Test4
from EX5 import Test5
from EX6 import Test6
from EX7 import Test7
from EX8 import Test8
List=[]
List.append(Test1(1e-5))
List.append(Test2(1e-5))
List.append(Test3(1e-5))
List.append(Test4(1e-5))
List.append(Test5(1e-5))
List.append(Test6(1e-5))
List.append(Test7(1e-5))
List.append(Test8(1e-5))
for i in List:
    print i.TestResult