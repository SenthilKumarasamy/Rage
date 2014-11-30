from xlrd import *
class ReadConfigfile():
    def __init__(self,File):
        book=open_workbook(File)
        sheet=book.sheet_by_index(0)
        nrow=sheet.nrows
        ncol=sheet.ncols
        self.EquTempApp=[]
        for i in range(nrow-1):
            str=sheet.cell(i,0).value
            if (str[0]!='$'):
                self.EquTempApp.append(float(sheet.cell(i,1).value))
        self.alpha=float(sheet.cell(nrow-1,1).value)