''' Flag = 0 means unmeasured, 1 means Measured, 2 means Constant'''
import collections as Con
class Readfile:
    def __init__(self,filename):
#         self.Name=[]
#         self.Meas=[]
#         self.Sigma=[]
#         self.Flag=[]
#         self.Unit=[]
#         f=open(filename,'r')
#         Lines=f.readlines()
#         Line1=[]
#         for i in Lines:
#             if (i[0]!='$'):
#                 Line1.append(i.replace("\n",""))
#         for i in Line1:
#             Temp=i.split('\t')
#             self.Name.append(Temp[0])
#             self.Meas.append(Temp[1])
#             self.Sigma.append(Temp[2])
#             self.Flag.append(Temp[3])
#             self.Unit.append(Temp[4].replace("\n",""))
#         if (len(self.Name)!=len(set(self.Name))):
#             print ('Some of the Tag Names are not unique. Printing Non Unique Tags')
#             Dic=Con.Counter(self.Name)
#             for i in Dic.keys():
#                 if (Dic[i]>1):
#                     print i,'repeated', Dic[i], ' times'
#             exit()
#         f.close()
        from xlrd import *
        book=open_workbook(filename)
        sheet=book.sheet_by_index(0)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.Name=[]
        self.Meas=[]
        self.Sigma=[]
        self.Flag=[]
        self.Unit=[]
        for i in range(nrow):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.Name.append(sheet.cell(i,0).value)
                self.Meas.append(sheet.cell(i,1).value)
                self.Sigma.append(sheet.cell(i,2).value)
                self.Flag.append(sheet.cell(i,3).value)
                self.Unit.append(sheet.cell(i,4).value)
        if (len(self.Name)!=len(set(self.Name))):
            print ('Some of the Tag Names are not unique. Printing Non Unique Tags')
            Dic=Con.Counter(self.Name)
            for i in Dic.keys():
                if (Dic[i]>1):
                    print i,'repeated', Dic[i], ' times'
            exit()