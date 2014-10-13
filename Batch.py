from Test.EX1 import Test1
from Test.EX2 import Test2
from Test.EX3 import Test3
List=[]
List.append(Test1(1e-5))
List.append(Test2(1e-5))
List.append(Test3(1e-5))
for i in List:
    print i.TestResult