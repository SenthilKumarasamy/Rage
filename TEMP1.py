from xlrd import *
book=open_workbook('NPLMeas.xls')
sheet=book.sheet_by_index(0)
nrow=sheet.nrows
ncol=sheet.ncols
Tag=[]
Meas=[]
Sigma=[]
Flag=[]
Unit=[]
for i in range(nrow):
    str=sheet.cell(i,0).value
    if (str[0]!='$'):
        Tag.append(sheet.cell(i,0).value)
        Meas.append(sheet.cell(i,1).value)
        Sigma.append(sheet.cell(i,2).value)
        Flag.append(sheet.cell(i,3).value)
        Unit.append(sheet.cell(i,4).value)

        
