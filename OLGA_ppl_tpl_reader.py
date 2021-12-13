# -*- coding: utf-8 -*-
"""
 
@author: Giuseppe Armenise
"""
import tkinter as tk
from tkinter import messagebox

from tkinter import filedialog
from tkinter import ttk
import xlsxwriter
from time_conv import *
Branch_names=[]
Branch_x=[]
Branch_y=[]
Branch_overall_y=[]
Branch_overall_x=[]
Number_vars=0
variables_names=[]
variable_container=[]
Timeseries=[]
time_unit='unknown'
time_conv=Dim_Value(1.0,'s')
is_tpl=False
i_graph=1
unit_geometry=''
TimeGraph=[]
VarGraph=[]

program_name="OLGA ppl/tpl reader"

Olga_unit = {
        'S': "s",
        'M':"min",
        'h':"h",
        "d":"d"
        }

class StartApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.winfo_toplevel().title(program_name)
        self.frames = {}
        page_name = StartPage.__name__
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        for F in (StartPage,SelectTimes,SelectVariables,GraphEditor):
                page_name = F.__name__
                frame = F(parent=container, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open ppl/tpl',command=lambda:[StartPage.Import_ppl(self,self.labelpath)])
        filemenu.add_command(label='Save as .xlsx',command=lambda:[self.Save_as_xlsx()])
        filemenu.add_command(label="Quit", command=lambda:self.AppQuit())
        menubar.add_cascade(label="File",menu=filemenu)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Homepage',command=lambda:self.show_frame("StartPage"))
        editmenu.add_command(label='Select Times',command=lambda:self.show_frame("SelectTimes"))
        editmenu.add_command(label='Select Variables',command=lambda:self.show_frame("SelectVariables"))
        editmenu.add_command(label='Edit Graphs',command=lambda:self.show_frame("GraphEditor"))
        menubar.add_cascade(label="Edit",menu=editmenu)
        self.config(menu=menubar)
    
    def AppQuit(self):
        Can_Quit=messagebox.askquestion('Quit','Close '+program_name+'?')
        if Can_Quit=='yes':
            self.destroy()
            
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    
    def define_x_axis(self,len_var,x_ax):
        x_axis=[]
        if len(x_ax)-1==len_var:
            for j in range(len_var):
                x_axis.append((x_ax[j]+x_ax[j+1])/2.0)
        else:
            x_axis=x_ax.copy()
        return x_axis
    
    def Save_as_xlsx(self):
        global unit_geometry
        if Number_vars==0:
            messagebox.showwarning('Save File','No file loaded')
        else:
            try:
                File_To_Save=filedialog.asksaveasfilename(defaultextension='.xlsx')
                workbook=xlsxwriter.Workbook(File_To_Save)
                worksheet=workbook.add_worksheet('Branch-Geometry')
                for i in range(len(Branch_names)):
                    worksheet.write(0,i*2,str(Branch_names[i]))
                    for j in range(len(Branch_overall_x[i])):
                        worksheet.write(1+j,i*2,Branch_overall_x[i][j])
                    for j in range(len(Branch_overall_y[i])):
                        worksheet.write(1+j,i*2+1,Branch_overall_y[i][j])
                    worksheet.write(0,i*2+1,str("unit: "+unit_geometry))
                if self.HowSave.get()==1 and is_tpl==False:
                    n_var=0
                    for i in range(len(variables_names)):
                        if variables_names[i] in self.listAddVars.get(0,tk.END):
                            n_var+=1
                            try:
                                worksheet=workbook.add_worksheet(('('+str(n_var)+')'+str(variables_names[i][0:10])).replace('\'','').replace('\"',''))
                            except:
                                worksheet=workbook.add_worksheet(('('+str(n_var)+')'))
                            worksheet.write(0,0,str('Variable:'))
                            worksheet.write(0,1,str(variables_names[i]))
                            cell_i=2
                            worksheet.write(1,0,str('time ('+time_unit+') :').replace('\'',''))
                            worksheet.write(2,0,str('Pipe Length '+unit_geometry+':'))
                            for j in range(len(Branch_overall_x)):
                                if (str(Branch_names[j]) in str(variables_names[i])) and \
                                (len(Branch_overall_x[j])==len(variable_container[i][0]) or \
                                 len(Branch_overall_x[j])-1==len(variable_container[i][0])):
                                    index_branch=1*j
                            x_actual_axis=self.define_x_axis(len(variable_container[i][0]),Branch_overall_x[index_branch])
                            for j in range(len(variable_container[i][0])):
                                worksheet.write(j+3,0,float(x_actual_axis[j]))
                            for times in range(len(Timeseries)):
                                if Timeseries[times] in self.listAddTime.get(0,tk.END):
                                    worksheet.write(1,cell_i,Timeseries[times])
                                    for j in range(len(variable_container[i][times])):
                                        worksheet.write(3+j,cell_i,float(variable_container[i][times][j]))
                                    cell_i+=1
                elif is_tpl==False:
                    for times in range(len(Timeseries)):
                        cell_i=0
                        if Timeseries[times] in self.listAddTime.get(0,tk.END):
                            worksheet=workbook.add_worksheet(('time ='+str(Timeseries[times])[0:15]+time_unit).replace('\'',''))
                            for i in range(len(variables_names)):
                                if variables_names[i] in self.listAddVars.get(0,tk.END):
                                    worksheet.write(0,cell_i*2,str('Pipe Length '+unit_geometry+':'))
                                    worksheet.write(0,cell_i*2+1,str(variables_names[i]))
                                    for j in range(len(Branch_overall_x)):
                                        if (str(Branch_names[j]) in str(variables_names[i])) and \
                                        (len(Branch_overall_x[j])==len(variable_container[i][0]) or \
                                         len(Branch_overall_x[j])-1==len(variable_container[i][0])):
                                            index_branch=1*j
                                    x_actual_axis=self.define_x_axis(len(variable_container[i][0]),Branch_overall_x[index_branch])
                                    for j in range(len(variable_container[i][times])):
                                        worksheet.write(1+j,cell_i*2,float(x_actual_axis[j]))
                                        worksheet.write(1+j,cell_i*2+1,float(variable_container[i][times][j]))
                                    cell_i+=1
                else:
                    worksheet=workbook.add_worksheet('Variables')
                    cell_i=0
                    for i in range(len(variables_names)):
                        if variables_names[i] in self.listAddVars.get(0,tk.END):
                            worksheet.write(0,cell_i,str(variables_names[i]))
                            for j in range(len(variable_container)):
                                worksheet.write(1+j,cell_i,float(variable_container[j][i]))
                            cell_i+=1
                for i in range(self.ListGraph.size()):
                    worksheet=workbook.add_worksheet(self.ListGraph.get(i))
                    worksheet.write(0,0,str('Variable:'))
                    worksheet.write(0,1,str(VarGraph[i]))
                    worksheet.write(1,0,str('Title:'))
                    worksheet.write(1,3,str('Legend:'))
                    worksheet.write(1,1,str(self.ListGraph.get(i)))
                    worksheet.write(2,0,str('x Label:'))
                    worksheet.write(3,0,str('y Label:'))
                    index_var=variables_names.index(VarGraph[i])
                    worksheet.write(3,1,str(variables_names[index_var]))
                    worksheet.write(1,4,str(variables_names[index_var]))
                    cell_j=4
                    worksheet.write(cell_j,1,str(str(variables_names[index_var])))
                    if is_tpl:
                        worksheet.write(2,1,str(variables_names[0]))
                        worksheet.write(cell_j,0,str(variables_names[0]))                    
                        cell_j+=1
                        for j in range(len(variable_container)):
                            worksheet.write(cell_j,0,float(variable_container[j][0]))
                            worksheet.write(cell_j,1,float(variable_container[j][index_var]))
                            cell_j+=1
                        len_plot=len(variable_container)
                    else:
                        worksheet.write(0,3,str('Time:'))
                        index_time=Timeseries.index(TimeGraph[i])
                        worksheet.write(0,4,str(Timeseries[index_time])+time_unit)
                        for j in range(len(Branch_overall_x)):
                            if (str(Branch_names[j]) in str(VarGraph[i])) and \
                            (len(Branch_overall_x[j])==len(variable_container[index_var][index_time]) or \
                             (len(Branch_overall_x[j])-1==len(variable_container[index_var][index_time]))):
                                index_branch=1*j
                        worksheet.write(2,1,str('Pipe Length '+unit_geometry))
                        worksheet.write(cell_j,0,str('Pipe Length '+unit_geometry))                    
                        cell_j+=1
                        x_actual_axis=self.define_x_axis(len(variable_container[index_var][index_time]),Branch_overall_x[index_branch])
                        for j in range(len(variable_container[index_var][index_time])):
                            worksheet.write(cell_j,0,float(x_actual_axis[j]))
                            worksheet.write(cell_j,1,float(variable_container[index_var][index_time][j]))
                            cell_j+=1
                        len_plot=len(variable_container[index_var][index_time])
                    chart=workbook.add_chart({'type':'scatter'})
                    chart.set_title({'name':'=\''+self.ListGraph.get(i)+'\'!$B$2'})
                    chart.set_x_axis({'name':'=\''+self.ListGraph.get(i)+'\'!$B$3'})
                    chart.set_y_axis({'name':'=\''+self.ListGraph.get(i)+'\'!$B$4'})
                    chart.add_series({'name':'=\''+str(self.ListGraph.get(i))+'\'!$E$2','categories': '=\''+str(self.ListGraph.get(i))+'\'!$A$6:$A$'+str(len_plot+5),\
                    'values':'=\''+str(self.ListGraph.get(i))+'\'!$B$6:$B$'+str(len_plot+5),'marker': {'type': 'none'},\
                    'line':{'width':2.50, 'transparency': 50}})
                    worksheet.insert_chart('E3', chart)
                workbook.close()
                messagebox.showinfo('Save File','File saved')
            except:
                messagebox.showerror('Save File','File not saved')
                
    def clear_vars(self,LabelText):
        LabelText.config(text=" ")
        Branch_names.clear()
        Branch_x.clear()
        Branch_y.clear()
        Branch_overall_x.clear()
        Branch_overall_y.clear()
        variables_names.clear()
        variable_container.clear()
        self.listTimes.delete(0,tk.END)
        self.listAddTime.delete(0,tk.END)
        self.listVars.delete(0,tk.END)
        self.listAddVars.delete(0,tk.END)
        self.ListVarGraph.delete(0,tk.END)
        self.ListTimeGraph.delete(0,tk.END)
        self.ListGraph.delete(0,tk.END)
        VarGraph.clear()
        TimeGraph.clear()
        Timeseries.clear()
        global Number_vars
        Number_vars=0
        global time_unit
        time_unit='unknown'
        global i_graph
        i_graph=1
        global unit_geometry
        unit_geometry=''
        
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        frame1=tk.Frame(self)
        frame1.pack(pady=10)
        
        ImportedFileLabel1=tk.Label(frame1, text="Imported file:")
        ImportedFileLabel1.pack(side='top',pady=10)
        
        ImportedFileLabel2=tk.Label(frame1, text=" ")
        ImportedFileLabel2.pack(side='top',fill="both",pady=10)
        controller.labelpath=ImportedFileLabel2
        
        frame2=tk.LabelFrame(self,text='Excel Sheet (ppl)')
        frame2.pack(pady=10)

        SaveChoice = tk.IntVar()
        SaveChoice.set(0)
        S_Choices = [("Time", 0),("Variable", 1)]
        for text, choice in S_Choices:
            RadioChoice=tk.Radiobutton(frame2, text=text,variable=SaveChoice,\
            value=choice)
            RadioChoice.pack(side='left', padx=10)
        SaveChoice.set(0)
        controller.HowSave=SaveChoice
        frame18=tk.Label(self,text='Developed by Giuseppe Armenise')
        frame18.place(x=100,y=750)
        
    def Import_ppl(controller,LabelText):
        global is_tpl
        global Number_vars
        global time_unit
        global i_graph
        global unit_geometry
        File_To_Open=filedialog.askopenfilename(title = "Select file",\
                                                filetypes = (("ppl files","*.ppl"),\
                                                             ("tpl files","*.tpl"),\
                                                             ("all files","*.*")))
        if File_To_Open!='':
            controller.clear_vars(LabelText)
            try:
                is_tpl = True if File_To_Open.split(".")[-1] == 'tpl' else False
                f = open(File_To_Open, "r+")
                current_line=f.readline()
                while (str('CATALOG') in current_line)==False:
                    if str('GEOMETRY') in current_line:
                        unit_geometry=current_line.replace('\n','').replace('\'','').replace('GEOMETRY','')
                    if str('BRANCH') in (current_line):
                        Branch_names.append(f.readline().replace('\n','').replace('\'',''))
                        branch_iter=int(f.readline().replace('\n',''))
                        current_x_branch=[]
                        current_y_branch=[]
                        while len(Branch_x)<=branch_iter:
                            current_x_branch.extend(f.readline().replace('\n','').split(' '))
                            for adding in current_x_branch:
                                if adding!='' and adding!=' ':
                                    Branch_x.append(float(adding))
                            current_x_branch.clear()
                        while len(Branch_y)<=branch_iter:
                            current_y_branch.extend(f.readline().replace('\n','').split(' '))
                            for adding in current_y_branch:
                                if adding!='' and adding!=' ':
                                    Branch_y.append(float(adding))
                            current_y_branch.clear()
                        Branch_overall_x.append(1*Branch_x)
                        Branch_overall_y.append(1*Branch_y)
                        Branch_x.clear()
                        Branch_y.clear()
                    current_line=f.readline()
                Number_vars=int(f.readline().replace('\n',''))
                for i in range(Number_vars):
                    variables_names.append(f.readline().replace('\n',''))
                    variable_container.append([])
                    controller.listVars.insert(tk.END,variables_names[-1])
                if is_tpl==False:
                    time_unit=f.readline().replace('\n','').\
                    replace('TIME SERIES','')
                    time_unit = ''.join(c for c in time_unit if c.isalpha())
                    global time_conv
                    time_conv=Dim_Value(1.,Olga_unit[time_unit])
                    controller.TimeUnit.current(controller.TimeUnit["values"].index(Olga_unit[time_unit]))
                else:
                    variable_container.clear()
                    variables_names.insert(0,f.readline().replace('\n',''))
                    variable_container.insert(0,f.readline().replace('\n','').split(' '))
                    controller.listVars.insert(0,variables_names[0])
                time_continue=True
                while time_continue:
                    try:
                        if is_tpl:
                            current_var=f.readline().replace('\n','').split(' ')
                            if len(current_var)==1:
                                time_continue=False
                            else:
                                variable_container.append(current_var)
                        else:
                            Timeseries.append(float(f.readline().replace('\n','')))
                            for i in range(Number_vars):
                                current_var=f.readline().replace('\n','').split(' ')
                                try:
                                    current_var.remove('')
                                except:
                                    pass
                                variable_container[i].append(current_var)
                            controller.listTimes.insert(tk.END,Timeseries[-1])
                    except:
                        time_continue=False
                f.close()
                if is_tpl:
                    controller.listAddVars.insert(tk.END,controller.listVars.get(0))
                    controller.ListVarGraph.insert(tk.END,controller.listVars.get(0))             
                LabelText.config(text=str(File_To_Open))
            except:
                controller.clear_vars(LabelText)
        else:
            pass

class SelectTimes(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        controller.geometry("900x600")
        frame1=tk.Frame(self,padx=5,pady=5)
        frame1.pack(side='top',pady=10)
        
        frame1_1=tk.Frame(frame1)
        frame1_1.pack(side='left',padx=5,pady=10)
        
        AddTimesLabel=tk.Label(frame1_1, text="Times:")
        AddTimesLabel.pack(side='top',pady=5,padx=100)
        UnitTimesLabel=tk.Label(frame1_1, text="unit: ")
        UnitTimesLabel.pack(side='left',pady=5,padx=10)
        comboTime = ttk.Combobox(frame1_1, values=["s","min","h","d"])
        comboTime.pack(side='left',padx=10)
        
        controller.TimeUnit=comboTime
        
        Label_Added=tk.Label(frame1,text='Added Times: ')
        Label_Added.pack(side='right',padx=200)
        
        frame2=tk.Frame(self)
        frame2.pack(side='top',padx=5,pady=5)
        
        listbox1 = tk.Listbox(frame2,height=20,width=30)
        listbox1.pack(side='left',pady=5)
        Scrollbar1=tk.Scrollbar(frame2, orient="vertical")
        Scrollbar1.config(command=listbox1.yview)
        Scrollbar1.pack(side='left',fill="y")
        controller.listTimes=listbox1
        
        def ConvTime(eventObject):
            global time_conv
            global Timeseries
            global time_unit
            time_unit=comboTime.get()
            time_conv.converter(comboTime.get())
            listbox1.delete(0,tk.END)
            list_to_add=[]
            for i in range(len(Timeseries)): Timeseries[i]=operator.mul(Timeseries[i],time_conv.val)
            for i in range(controller.listAddTime.size()): list_to_add.append(operator.mul(controller.listAddTime.get(i),time_conv.val))
            for i in range(len(TimeGraph)): TimeGraph[i]=operator.mul(TimeGraph[i],time_conv.val)
            controller.listAddTime.delete(0,tk.END)
            controller.ListTimeGraph.delete(0,tk.END)
            for i in range(len(list_to_add)):
                controller.listAddTime.insert(tk.END,list_to_add[i])
                controller.ListTimeGraph.insert(tk.END,list_to_add[i])             
            del list_to_add
            for i in range(len(Timeseries)): listbox1.insert(tk.END,Timeseries[i])
            time_conv.val=1.
        comboTime.bind("<<ComboboxSelected>>", ConvTime)
        
        frame2_1=tk.Frame(frame2)
        frame2_1.pack(side='left')
        
        Button1=tk.Button(frame2_1,text='Add Time',command=lambda:[Add_Button1(self)])
        Button1.pack(side='top',padx=10,pady=10)
        Button1_1=tk.Button(frame2_1,text='Add All Times',command=lambda:[Add_Button1_1(self)])
        Button1_1.pack(side='top',padx=10,pady=10)
        
        Button2=tk.Button(frame2_1,text='Delete',command=lambda:[Del_Button2(self)])
        Button2.pack(side='top',padx=10,pady=10)
        Button3=tk.Button(frame2_1,text='Delete All',command=lambda:[Del_Button3(self)])
        Button3.pack(side='top',padx=10,pady=10)
        
        listbox2 = tk.Listbox(frame2,height=20,width=30)
        listbox2.pack(side='left',pady=5)
        Scrollbar2=tk.Scrollbar(frame2, orient="vertical")
        Scrollbar2.config(command=listbox2.yview)
        Scrollbar2.pack(side='left',fill="y")
        controller.listAddTime=listbox2
        
        def Add_Button1(self):
            if listbox1.size()==0:
                pass
            else:
                if (listbox1.get(tk.ACTIVE) in listbox2.get(0,tk.END))==False:
                    listbox2.insert(tk.END,listbox1.get(tk.ACTIVE))
                    controller.ListTimeGraph.insert(tk.END,listbox1.get(tk.ACTIVE))
            
        def Add_Button1_1(self):
            listbox2.delete(0,tk.END)
            controller.ListTimeGraph.delete(0,tk.END)
            for adding in listbox1.get(0, tk.END):
                listbox2.insert(tk.END,adding)
                controller.ListTimeGraph.insert(tk.END,adding)
        
        def Del_Button2(self):
            if listbox2.size()==0:
                pass
            else:
                Ask_Del=messagebox.askokcancel("Delete Time","Delete the Time "+ str(listbox2.get(tk.ACTIVE)) + " ?")
                if Ask_Del==True:
                    controller.ListTimeGraph.delete(listbox2.index(tk.ACTIVE))
                    listbox2.delete(tk.ACTIVE)

        def Del_Button3(self):
            Ask_Del=messagebox.askokcancel("Delete Time","Delete the added Times?")
            if Ask_Del==True:
                listbox2.delete(0,tk.END)
                controller.ListTimeGraph.delete(0,tk.END)
        
class SelectVariables(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        controller.geometry("900x600")
        frame1=tk.Frame(self)
        frame1.pack(side='top',padx=5,pady=10)
        
        frame1_1=tk.Frame(frame1)
        frame1_1.pack(side='left',padx=5,pady=10)
        
        AddVarsLabel=tk.Label(frame1_1, text="Variables:")
        AddVarsLabel.pack(anchor=tk.W,padx=100)
        
        label_filter=tk.Label(frame1_1, text='Filter:')
        label_filter.pack(side='left',padx=10,pady=20)
        Entry_filter=tk.Entry(frame1_1, width=15)
        Entry_filter.pack(side='left',padx=10,pady=20)
        Button_filter=tk.Button(frame1_1,text='Filter',command=lambda:[filter_callback(Entry_filter.get())])
        Button_filter.pack(side='left',padx=10,pady=20)
        
        Label_Added=tk.Label(frame1,text='Added Variables: ')
        Label_Added.pack(anchor=tk.E,padx=200,pady=5)
        
        frame2=tk.Frame(self)
        frame2.pack(side='top',pady=5,padx=5,fill=tk.X,expand=True)
        
        listbox1 = tk.Listbox(frame2,height=20)
        listbox1.pack(side='left',pady=5,fill=tk.X, expand=True)
        Scrollbar1=tk.Scrollbar(frame2, orient="vertical")
        Scrollbar1.config(command=listbox1.yview)
        Scrollbar1.pack(side='left',fill="y")
        controller.listVars=listbox1
        
        frame2_1=tk.Frame(frame2)
        frame2_1.pack(side='left')
        
        Button1=tk.Button(frame2_1,text='Add Variable',command=lambda:[Add_Button1(self)])
        Button1.pack(side='top',padx=10,pady=10)
        Button1_1=tk.Button(frame2_1,text='Add All Variables',command=lambda:[Add_Button1_1(self)])
        Button1_1.pack(side='top',padx=10,pady=10)
        
        Button2=tk.Button(frame2_1,text='Delete',command=lambda:[Del_Button2(self)])
        Button2.pack(side='top',padx=10,pady=10)
        Button3=tk.Button(frame2_1,text='Delete All',command=lambda:[Del_Button3(self)])
        Button3.pack(side='top',padx=10,pady=10)
        
        listbox2 = tk.Listbox(frame2,height=20)
        listbox2.pack(side='left',fill=tk.X, expand=True)
        Scrollbar2=tk.Scrollbar(frame2, orient="vertical")
        Scrollbar2.config(command=listbox2.yview)
        Scrollbar2.pack(side='left',fill="y")
        controller.listAddVars=listbox2
        
        def Add_Button1(self):
            if listbox1.size()==0:
                pass
            else:
                if (listbox1.get(tk.ACTIVE) in listbox2.get(0,tk.END))==False:
                    listbox2.insert(tk.END,listbox1.get(tk.ACTIVE))
                    controller.ListVarGraph.insert(tk.END,listbox1.get(tk.ACTIVE))
            
        def Add_Button1_1(self):
            for adding in listbox1.get(0, tk.END):
                if adding not in listbox2.get(0, tk.END):
                    listbox2.insert(tk.END,adding)
                    controller.ListVarGraph.insert(tk.END,adding)
        
        def Del_Button2(self):
            if listbox2.size()==0:
                pass
            else:
                Ask_Del=messagebox.askokcancel("Delete Variable","Delete the Variable "+ str(listbox2.get(tk.ACTIVE)) + " ?")
                if Ask_Del==True:
                    controller.ListVarGraph.delete(listbox2.index(tk.ACTIVE))
                    listbox2.delete(tk.ACTIVE)

        def Del_Button3(self):
            Ask_Del=messagebox.askokcancel("Delete Variable","Delete the added Variables?")
            if Ask_Del==True:
                listbox2.delete(0,tk.END)
                controller.ListVarGraph.delete(0,tk.END)
                
        def filter_callback(text_filter):
            listbox1.delete(0,tk.END)
            for i in range(len(variables_names)):
                if text_filter in variables_names[i]:
                    listbox1.insert(tk.END,variables_names[i])

class GraphEditor(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        MFrame1=tk.Frame(self)
        MFrame1.pack(side='left',fill=tk.X,expand=True)
        
        MFrame2=tk.Frame(self)
        MFrame2.pack(side='left',fill=tk.X,expand=True)
        
        frame1=tk.Frame(MFrame1)
        frame1.pack(side='top',padx=5,pady=10)

        Label_Added=tk.Label(frame1,text='Added Variables:')
        Label_Added.pack(anchor=tk.E,padx=20,pady=5)
        
        frame2=tk.Frame(MFrame1)
        frame2.pack(side='top',pady=5,padx=5,fill=tk.X,expand=True)
        
        listbox1 = tk.Listbox(frame2,height=10)
        listbox1.pack(side='left',pady=5,fill=tk.X, expand=True)
        controller.ListVarGraph=listbox1
        
        Scrollbar1=tk.Scrollbar(frame2, orient="vertical")
        Scrollbar1.config(command=listbox1.yview)
        Scrollbar1.pack(side='left',fill="y")
        
        frame3=tk.Frame(MFrame1)
        frame3.pack(side='top',padx=5,pady=10)

        Label_AddedTime=tk.Label(frame3,text='Added Times:')
        Label_AddedTime.pack(anchor=tk.E,padx=20,pady=5)
        
        frame4=tk.Frame(MFrame1)
        frame4.pack(side='top',pady=5,padx=5,fill=tk.X,expand=True)
        
        listbox2 = tk.Listbox(frame4,height=10)
        listbox2.pack(side='left',pady=5,fill=tk.X, expand=True)
        controller.ListTimeGraph=listbox2
        
        Scrollbar2=tk.Scrollbar(frame4, orient="vertical")
        Scrollbar2.config(command=listbox2.yview)
        Scrollbar2.pack(side='left',fill="y")
        
        Button1=tk.Button(MFrame2,text='Add Graph',command=lambda:[Add_Button1(self)])
        Button1.pack(side='top',padx=10,pady=10)
        
        frame5=tk.Frame(MFrame2)
        frame5.pack(side='top',padx=5,pady=10)

        Label_AddedGraph=tk.Label(frame5,text='Graphs:')
        Label_AddedGraph.pack(anchor=tk.E,padx=20,pady=5)
        
        frame6=tk.Frame(MFrame2)
        frame6.pack(side='top',pady=5,padx=5,fill=tk.X,expand=True)
        
        listbox3 = tk.Listbox(frame6,height=10)
        listbox3.pack(side='left',pady=5,fill=tk.X, expand=True)
        controller.ListGraph=listbox3
        
        Scrollbar3=tk.Scrollbar(frame6, orient="vertical")
        Scrollbar3.config(command=listbox3.yview)
        Scrollbar3.pack(side='left',fill="y")
        
        def Add_Button1(self):
            global time_unit
            global i_graph
            global VarGraph
            global TimeGraph
            if listbox1.size()==0:
                messagebox.showwarning("Add Graph","No Variable to Add")
            elif is_tpl==False and listbox2.size()==0:
                messagebox.showwarning("Add Graph","No Time to Add")
            else:
                if is_tpl==False:
                    yes_no=messagebox.askquestion("Add Graph","Add the graph:\nVariable: "+listbox1.get(tk.ACTIVE)\
                                               +"\nTime: "+str(listbox2.get(tk.ACTIVE))+time_unit+ " ?")
                else:
                    yes_no=messagebox.askquestion("Add Graph","Add the graph:\nVariable: "+listbox1.get(tk.ACTIVE)+" ?")
                if yes_no=='yes':
                    VarGraph.append(listbox1.get(tk.ACTIVE))
                    if is_tpl==False:
                        TimeGraph.append(listbox2.get(tk.ACTIVE))
                    listbox3.insert(tk.END,'Graph-' + str(i_graph))
                    i_graph+=1


if __name__ == "__main__":
    app = StartApp()
    #uncomment to add an icon
    # try:
    #     app.iconbitmap('icon.ico')
    # except:
    #     messagebox.showinfo('Icon','Icon not found')
    app.mainloop()
