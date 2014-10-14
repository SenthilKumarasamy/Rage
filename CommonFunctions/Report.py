'''
Created on Jul 29, 2014

@author: Senthil

'''
from Units.Heater import Heater
from Units.HeatExchanger import HeatExchanger
from Units.Seperator import Seperator
from Units.Reactor import Reactor
from fpdf import FPDF
def Report(ListUints):
    pdf=FPDF()      
    for i in ListUints:
        pdf.add_page()
        pdf.set_font('Arial','B',10)
        pdf.cell(200,5,'===================================================================================================',0,0.5,'C')
        pdf.cell(200,5, txt="Units Summary", ln=0.5, align="C")
        pdf.cell(200,5,'===================================================================================================',0,0.5,'C')
        if (isinstance(i,Heater)):
            pdf.cell(200, 5, txt='Unit Name : '+i.Name, ln=0.5, align="C")
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Inlet stream deatils :', ln=0.1,align='L')
#            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.cell(200,5,'Stream Name : %s'%(i.input.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(i.input.FTag.Tag,i.input.FTag.Sigma,i.input.FTag.Flag,i.input.FTag.Meas,i.input.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(i.input.TTag.Tag,i.input.FTag.Sigma,i.input.TTag.Flag,i.input.TTag.Meas,i.input.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(i.input.PTag.Tag,i.input.FTag.Sigma,i.input.PTag.Flag,i.input.PTag.Meas,i.input.PTag.Est),ln=0.5,align='L' )
            for j in i.input.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.input.CTag[j].Tag,i.input.FTag.Sigma,i.input.CTag[j].Flag,i.input.CTag[j].Meas,i.input.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C') 
            
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Outlet stream deatils :', ln=0.5,align='L')
#            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.cell(200,5,'Stream Name : %s'%(i.output.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                      TagName            Sigma      Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s        %f            %d                            %f                    %f'%(i.output.FTag.Tag,i.output.FTag.Sigma,i.output.FTag.Flag,i.output.FTag.Meas,i.output.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s         %f           %d                            %f                    %f'%(i.output.TTag.Tag,i.output.TTag.Sigma,i.output.TTag.Flag,i.output.TTag.Meas,i.output.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s        %f            %d                            %f                    %f'%(i.output.PTag.Tag,i.output.PTag.Sigma,i.output.PTag.Flag,i.output.PTag.Meas,i.output.PTag.Est),ln=0.5,align='L' )
            for j in i.input.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s           %f         %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.output.CTag[j].Tag,i.output.CTag[j].Sigma,i.output.CTag[j].Flag,i.output.CTag[j].Meas,i.output.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Energy Stream details :', ln=0.5,align='L')
#             pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.cell(200,5,'Stream Name : %s'%(i.Qstrm.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                      TagName       Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Energy                     :        %s               %s            %d                            %f                    %f'%(i.Qstrm.Q.Tag,i.Qstrm.Q.Sigma,i.Qstrm.Q.Flag,i.Qstrm.Q.Meas,i.Qstrm.Q.Est),ln=0.5,align='L' )
            pdf.cell(200,5,'===================================================================================================',0,0.5,'C')
        elif (isinstance(i,HeatExchanger)):
            pdf.cell(200, 5, txt='Unit Name : '+i.Name, ln=0.5, align="C")
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Inlet stream deatils :', ln=0.1,align='L')
#            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.cell(200,5,'Hotside inlet Stream Name : %s'%(i.Shellin.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(i.Shellin.FTag.Tag,i.Shellin.FTag.Sigma,i.Shellin.FTag.Flag,i.Shellin.FTag.Meas,i.Shellin.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(i.Shellin.TTag.Tag,i.Shellin.TTag.Sigma,i.Shellin.TTag.Flag,i.Shellin.TTag.Meas,i.Shellin.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(i.Shellin.PTag.Tag,i.Shellin.PTag.Sigma,i.Shellin.PTag.Flag,i.Shellin.PTag.Meas,i.Shellin.PTag.Est),ln=0.5,align='L' )
            for j in i.Shellin.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.Shellin.CTag[j].Tag,i.Shellin.FTag.Sigma,i.Shellin.CTag[j].Flag,i.Shellin.CTag[j].Meas,i.Shellin.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,'Coldside inlet Stream Name : %s'%(i.Tubein.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(i.Tubein.FTag.Tag,i.Tubein.FTag.Sigma,i.Tubein.FTag.Flag,i.Tubein.FTag.Meas,i.Tubein.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(i.Tubein.TTag.Tag,i.Tubein.TTag.Sigma,i.Tubein.TTag.Flag,i.Tubein.TTag.Meas,i.Tubein.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(i.Tubein.PTag.Tag,i.Tubein.PTag.Sigma,i.Tubein.PTag.Flag,i.Tubein.PTag.Meas,i.Tubein.PTag.Est),ln=0.5,align='L' )
            for j in i.Tubein.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.Tubein.CTag[j].Tag,i.Tubein.CTag[j].Sigma,i.Tubein.CTag[j].Flag,i.Tubein.CTag[j].Meas,i.Tubein.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Outlet stream deatils :', ln=0.1,align='L')
#            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.cell(200,5,'Hotside Outlet Stream Name : %s'%(i.Shellout.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(i.Shellout.FTag.Tag,i.Shellout.FTag.Sigma,i.Shellout.FTag.Flag,i.Shellout.FTag.Meas,i.Shellout.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(i.Shellout.TTag.Tag,i.Shellout.TTag.Sigma,i.Shellout.TTag.Flag,i.Shellout.TTag.Meas,i.Shellout.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(i.Shellout.PTag.Tag,i.Shellout.PTag.Sigma,i.Shellout.PTag.Flag,i.Shellout.PTag.Meas,i.Shellout.PTag.Est),ln=0.5,align='L' )
            for j in i.Shellout.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.Shellout.CTag[j].Tag,i.Shellout.FTag.Sigma,i.Shellout.CTag[j].Flag,i.Shellout.CTag[j].Meas,i.Shellout.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,'Coldside inlet Stream Name : %s'%(i.Tubeout.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(i.Tubeout.FTag.Tag,i.Tubeout.FTag.Sigma,i.Tubeout.FTag.Flag,i.Tubeout.FTag.Meas,i.Tubeout.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(i.Tubeout.TTag.Tag,i.Tubeout.TTag.Sigma,i.Tubeout.TTag.Flag,i.Tubeout.TTag.Meas,i.Tubeout.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(i.Tubeout.PTag.Tag,i.Tubeout.PTag.Sigma,i.Tubeout.PTag.Flag,i.Tubeout.PTag.Meas,i.Tubeout.PTag.Est),ln=0.5,align='L' )
            for j in i.Tubein.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(j.Name.replace(".FLD",""),i.Tubeout.CTag[j].Tag,i.Tubeout.CTag[j].Sigma,i.Tubeout.CTag[j].Flag,i.Tubeout.CTag[j].Meas,i.Tubeout.CTag[j].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
        elif (isinstance(i,Seperator)):
            pdf.cell(200, 5, txt='Unit Name : '+i.Name, ln=0.5, align="C")
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Inlet stream deatils :', ln=0.1,align='L')
            for j in i.input:
                pdf.set_font('Arial','BU',10)
                pdf.cell(200,5,'Stream Name : %s'%(j.Name),ln=0.5,align='C')
                pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
                pdf.set_font('Arial','B',10)
                pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(j.FTag.Tag,j.FTag.Sigma,j.FTag.Flag,j.FTag.Meas,j.FTag.Est),ln=0.5,align='L' )
                pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(j.TTag.Tag,j.TTag.Sigma,j.TTag.Flag,j.TTag.Meas,j.TTag.Est),ln=0.5,align='L' )
                pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(j.PTag.Tag,j.PTag.Sigma,j.PTag.Flag,j.PTag.Meas,j.PTag.Est),ln=0.5,align='L' )
                for k in j.CTag.keys():
                    pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(k.Name.replace(".FLD",""),j.CTag[k].Tag,j.CTag[k].Sigma,j.CTag[k].Flag,j.CTag[k].Meas,j.CTag[k].Est),ln=0.5,align='L' )
                pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
                pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Outlet stream deatils :', ln=0.1,align='L')
            for j in i.output:
                pdf.set_font('Arial','BU',10)
                pdf.cell(200,5,'Stream Name : %s'%(j.Name),ln=0.5,align='C')
                pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
                pdf.set_font('Arial','B',10)
                pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(j.FTag.Tag,j.FTag.Sigma,j.FTag.Flag,j.FTag.Meas,j.FTag.Est),ln=0.5,align='L' )
                pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(j.TTag.Tag,j.TTag.Sigma,j.TTag.Flag,j.TTag.Meas,j.TTag.Est),ln=0.5,align='L' )
                pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(j.PTag.Tag,j.PTag.Sigma,j.PTag.Flag,j.PTag.Meas,j.PTag.Est),ln=0.5,align='L' )
                for k in j.CTag.keys():
                    pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(k.Name.replace(".FLD",""),j.CTag[k].Tag,j.CTag[k].Sigma,j.CTag[k].Flag,j.CTag[k].Meas,j.CTag[k].Est),ln=0.5,align='L' )
                pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
        elif (isinstance(i,Reactor)):
            pdf.cell(200, 5, txt='Unit Name : '+i.Name, ln=0.5, align="C")
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Reactant stream deatils :', ln=0.1,align='L')
            j=i.Rstrm
            pdf.cell(200,5,'Stream Name : %s'%(j.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(j.FTag.Tag,j.FTag.Sigma,j.FTag.Flag,j.FTag.Meas,j.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(j.TTag.Tag,j.TTag.Sigma,j.TTag.Flag,j.TTag.Meas,j.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(j.PTag.Tag,j.PTag.Sigma,j.PTag.Flag,j.PTag.Meas,j.PTag.Est),ln=0.5,align='L' )
            for k in j.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(k.Name.replace(".FLD",""),j.CTag[k].Tag,j.CTag[k].Sigma,j.CTag[k].Flag,j.CTag[k].Meas,j.CTag[k].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
            pdf.set_font('Arial','BU',10)
            pdf.cell(200,5,txt='Product stream deatils :', ln=0.1,align='L')
            j=i.Pstrm
            pdf.cell(200,5,'Stream Name : %s'%(j.Name),ln=0.5,align='C')
            pdf.cell(20,8,'                                          TagName            Sigma     Measured Flag            Measured Value        Estimated Value',ln=0.5,align='L')
            pdf.set_font('Arial','B',10)
            pdf.cell(20,8,'    Flow                      :            %s           %f             %d                            %f                    %f'%(j.FTag.Tag,j.FTag.Sigma,j.FTag.Flag,j.FTag.Meas,j.FTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Temp                     :            %s            %f            %d                            %f                    %f'%(j.TTag.Tag,j.TTag.Sigma,j.TTag.Flag,j.TTag.Meas,j.TTag.Est),ln=0.5,align='L' )
            pdf.cell(20,8,'    Pres                      :            %s           %f             %d                            %f                    %f'%(j.PTag.Tag,j.PTag.Sigma,j.PTag.Flag,j.PTag.Meas,j.PTag.Est),ln=0.5,align='L' )
            for k in j.CTag.keys():
                pdf.cell(20,8,'    %s               :            %s          %f              %d                            %f                    %f'%(k.Name.replace(".FLD",""),j.CTag[k].Tag,j.CTag[k].Sigma,j.CTag[k].Flag,j.CTag[k].Meas,j.CTag[k].Est),ln=0.5,align='L' )
            pdf.cell(200,5,'-------------------------------------------------------------------------------------------------------------------------------------------------',ln=0.5,align='C')
        #pdf.set_auto_page_break(True,margin=0)
                                 
    pdf.output('tuto1.pdf','F')
    