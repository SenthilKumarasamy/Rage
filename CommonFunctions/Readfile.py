import collections as Con
from xlrd import *
## This class is used to create object that reads the specified Excel file containing the measurement details.
class Readfile:
    ##  Reads the Excel file and stores the details in its class data members.
    #   It ignores the rows that start with \$ symbol.
    #   It assumes the Excel file has the following format.
    #   \arg \c First column contains the Tag number of the sensor.
    #   \n The Tag number must be unique. Otherwise the program exits.
    #   \arg \c Second column contains the respective measured values or initial guess (in case of unmeasured variables).
    #   \arg \c Third column contains the sensor sigma values or the standard deviation of sensor noise.
    #   \arg \c Fourth column contains the value of the measurement flag. This flag takes one of the following values
    #   \n \c 0 meaning the respective variable is unmeasured.
    #   \n \c 1 meaning the respective variable is measured.
    #   \n \c 2 meaning the respective variable is kept constant and is not allowed change while reconciling.
    #   \arg \c Fifth column contains the unit of the measurement.
    ## \param filename refers to the full path of the Excel file containing the measurements.
    def __init__(self,filename):
        book=open_workbook(filename)
        sheet=book.sheet_by_index(0)
        nrow=sheet.nrows
        ncol=sheet.ncols
        ## Stores the Tag numbers of all the sensors as a list.
        #  The Tag number of each sensor must be unique i.e. each element of the list \b Name must be unique.
        self.Name=[]
        ## Stores the measured values or initial guess of all the sensors as a list.
        self.Meas=[]
        ## Stores the sigma values of all the sensors as a list
        self.Sigma=[]
        ## Stores the measurement flag value of all the sensors as a list
        #  It can take one of the following values.
        #  \arg \c 0 meaning the respective variable is unmeasured.
        #  \arg \c 1 meaning the respective variable is measured.
        #  \arg \c 2 meaning the respective variable is kept constant and is not allowed change while reconciling.
        self.Flag=[]
        ## Stores the unit of the respective variable.
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
