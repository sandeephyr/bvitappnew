import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from PyInstaller.utils.hooks import copy_metadata

# datas = copy_metadata("streamlit")
 
st.write("""
# BVIT Automation
""")
a=False


#for selecting the test pattern
#df = pd.read_excel(r"FF  Transmission @  Impact Test Databank new.xlsx",sheet_name=opt_file_name)
df= pd.DataFrame()
uploaded_file=st.file_uploader("Choose a .xlsx file",type="xlsx")


if uploaded_file is not None:
	# file_contenets=uploaded_file.getvalue()
	# df=pd.read_excel(uploaded_file)
    print(uploaded_file)
    a=True




if a==True:
    opt_file_name=st.selectbox(label='Select the transmission mode',options=['1st Gear Jackrabbit','2-1 Shift down','3-2 Shift down','4-3 Shift down','Rev. Gear Jackrabbit']) # ,'Rev. Gear Coast'

    df=pd.read_excel(uploaded_file, sheet_name= opt_file_name)
    # for selecting tm model
    opt_TM=st.selectbox(label='TM Model', options=df["TM Model"].unique())
    df1=df.loc[(df["TM Model"]==opt_TM)] # filter the data set
    
    
    # fro selecting the failure mode
    opt_failure=st.selectbox(label='Failure Mode', options=df1["Failure Mode -Primary (Part Name -1)"].unique(),placeholder="Select an option")
    df2=df1.loc[df1["Failure Mode -Primary (Part Name -1)"]==opt_failure] # filter the data set
    
               
    # fro selecting the final gear ratio
    opt_Fgear_ratio=st.selectbox(label='Final Gear Ratio', options=df2[" Final Gear Ratio"].unique())
    df3=df2.loc[df2[" Final Gear Ratio"]==opt_Fgear_ratio]  # filter the data set
    
    print(df3.columns)
    # as different test pattern have different gear ratio column so to filter them
    if(opt_file_name=="3-2 Shift down"):
        opt_2st_gear_ratio=st.selectbox(label='2nd Gear Ratio', options=df3["2nd  Gear Ratio"].unique())
        df4=df3.loc[df3["2nd  Gear Ratio"]==opt_2st_gear_ratio] # filter the data set
    if((opt_file_name=='1st Gear Jackrabbit') or (opt_file_name=="2-1 Shift down")):
        opt_1st_gear_ratio=st.selectbox(label='1st Gear Ratio', options=df3["1st Gear Ratio"].unique())
        df4=df3.loc[df3["1st Gear Ratio"]==opt_1st_gear_ratio]  # filter the data set
    if(opt_file_name=="4-3 Shift down"):
        opt_3rd_gear_ratio=st.selectbox(label='3rd Gear Ratio', options=df3["3rd Gear Ratio"].unique())
        df4=df3.loc[df3["3rd Gear Ratio"]==opt_3rd_gear_ratio]  # filter the data set
    if(opt_file_name=="Rev. Gear Jackrabbit"):
        opt_rev_gear_ratio=st.selectbox(label='Rev. Gear Ratio', options=df3['Rev. Gear Ratio'].unique())
        df4=df3.loc[df3['Rev. Gear Ratio']==opt_rev_gear_ratio]  # filter the data set
    
    
    # for calculating damage percent and number of cycle for the input torque
    def Damage_calculation_tq(eq,tq):
        w=int(eq[0]) #intercept of equation
        e=int(eq[1]) #slope of equation
        x=(tq- w)/e  #calculation of no of cycle
        #print(x)
        oc=np.exp(x)
        if(opt_file_name=='1st Gear Jackrabbit'):
            damage_percent=(250/oc)*100
        if(opt_file_name== "Rev. Gear Jackrabbit"):
            damage_percent=(100/oc)*100
        if((opt_file_name=="2-1 Shift down") or (opt_file_name=="3-2 Shift down") or (opt_file_name=="4-3 Shift down")):
            damage_percent=(500/oc)*100
        return(oc,damage_percent)
    
    
    # for calculating the torque and damage percent for the given number of cycles
    def Damage_calculation_c(eq,input_c):
        w=int(eq[0]) #intercept of eq
        e=int(eq[1]) # slope of eq
        y=e*input_c + w  # calculation of torque
        if(opt_file_name=='1st Gear Jackrabbit'):
            damage_percent_c=(250/input_c)*100
        if(opt_file_name== "Rev. Gear Jackrabbit"):
            damage_percent_c=(100/input_c)*100
        if((opt_file_name=="2-1 Shift down") or (opt_file_name=="3-2 Shift down") or (opt_file_name=="4-3 Shift down")):
            damage_percent_c=(500/input_c)*100
        return(y,damage_percent_c)
    
    
    # calculating equation for counter torque
    def counter_torque_equation_calculation(d):
        x=[]
        nx=[]
        x=d["""Cycle (No's)"""]
        for i in x:
            nx.append(float(i))
        xx=np.array(nx)
        y=d['Counter Torque\n(Nm)']
        
        ny=[]
        for j in y:
            ny.append(float(j))
        yy=np.array(ny)
        co=np.polyfit(np.log(xx),yy,1)
        counter_torque_eq=np.poly1d(co)
        return counter_torque_eq
    
    
    # calculating equation for input torque
    def input_torque_equation_calculation(d):
        import numpy as np
        x=[]
        nx=[]
        x=d["""Cycle (No's)"""]
        for i in x:
            nx.append(float(i))
        xx=np.array(nx)
        y=d['Input Torque (Nm)']
        
        ny=[]
        for j in y:
            ny.append(float(j))
        yy=np.array(ny)
        co=np.polyfit(np.log(xx),yy,1)
        input_torque_eq=np.poly1d(co)
        return input_torque_eq
    
    
    # calculating equation for output torque
    def output_torque_equation_calculation(d):
        import numpy as np
        x=[]
        nx=[]
        x=d["""Cycle (No's)"""]
        for i in x:
            nx.append(float(i))
        xx=np.array(nx)
        y=d['Total Output Torque (Nm)']
        
        ny=[]
        for j in y:
            ny.append(float(j))
        yy=np.array(ny)
        co=np.polyfit(np.log(xx),yy,1)
        output_torque_eq=np.poly1d(co)
        return output_torque_eq
    
    
    
    edited_data=st.data_editor(df4,num_rows='dynamic')
    #edited_data
    
    
    # calling the function to calculate the equations
    inp=input_torque_equation_calculation(edited_data)
    out=output_torque_equation_calculation(edited_data)
    cou=counter_torque_equation_calculation(edited_data)
    
    # displaying the equation
    st.write("Input Torque Equation:",inp)
    st.write("Output Torque Equation:",out)
    st.write("Counter Torque Equation:",cou)
    
    # taking the torque input from user for performing calculations
    intq=st.number_input(label='Enter the torque value')
    
    # selecting the eq for which we want to do the calculation
    eq_sel=st.selectbox(label='Select the equation',options=['input torque','output torque','counter torque'])
    q=[]
    if (eq_sel=='input torque'):
        q=Damage_calculation_tq(inp,intq)
    if (eq_sel=='output torque'):
        q=Damage_calculation_tq(out,intq)
    if (eq_sel=='counter torque'):
        q=Damage_calculation_tq(cou,intq)
    
    # displaying the ouput of caclutions
    st.write("Number of cycles: ",q[0])
    st.write("Damage percentage: ",q[1])
    
    
    # taking the no of cycles input from user to perform calculations
    in_no_of_cycle=st.number_input(label='Enter the number of cycle',min_value=1,value='min')
    if (eq_sel=='input torque'):
        q1=Damage_calculation_c(inp,in_no_of_cycle)
    if (eq_sel=='output torque'):
        q1=Damage_calculation_c(out,in_no_of_cycle)
    if (eq_sel=='counter torque'):
        q1=Damage_calculation_c(cou,in_no_of_cycle)
    
    # displaying the ouput of caclutions
    st.write("Torque: ",q1[0])
    st.write("damage percent: ",q1[1])
    
    
    
    # making the data set to make the scatter plot of no of cycles and various types of torque
    noc=edited_data["""Cycle (No's)"""]
    outnm=edited_data["Total Output Torque (Nm)"]
    innm=edited_data['Input Torque (Nm)']
    counm=edited_data['Counter Torque\n(Nm)']
    data_frame=pd.DataFrame(data={
        "output torque":outnm,
        "no of cycle":noc,
        'input torque':innm,
        'counter torque':counm})
    
    
    # scatter plot for input torque
    #st.scatter_chart(data=data_frame,x="no of cycle",y="input torque")
    
    
    # line plot for input torque
    plt.figure(figsize = (3, 3))
    x_in = np.linspace(0,20000,100)
    y_in = inp[1]*(np.log(x_in)) + inp[0]
    plt.plot(x_in,y_in, color='blue', lw=2,label='TN curve')
    plt.scatter(noc,innm,c='green',label='Scatter plot')
    plt.xlabel("no of cycles",fontsize='large')
    plt.ylabel("Input Torque",fontsize='large')
    plt.legend(fontsize='large')
    st.pyplot(plt.gcf())
    
    
    # scatter plot for ouput torque
    #st.scatter_chart(data=data_frame,x="no of cycle",y="output torque")
    
    # line plot for output torque
    x_out = np.linspace(0, 20000, 100)
    y_out= out[1]*(np.log(x_out)) + out[0]
    plt.figure(figsize = (2,2))
    plt.scatter(noc,outnm,c='green',label='Scatter plot')
    plt.plot(x_out, y_out,color='blue',label='TN curve')
    plt.xlabel("no of cycles")
    plt.ylabel("Output Torque")
    plt.legend()
    st.pyplot(plt.gcf())
    
    
    # scatter plot for counter torque
    st.scatter_chart(data=data_frame,x="no of cycle",y="counter torque")
    
    # line plot for counter torque
    x_cou = np.linspace(0, 20000, 100)
    y_cou = cou[1]*(np.log(x_cou)) + cou[0]
    plt.figure(figsize = (3, 3))
    plt.scatter(noc,counm,c='green',label='Scatter plot')
    plt.plot(x_cou, y_cou,color='blue', lw=2,label='TN curve')
    plt.xlabel("no of cycles",fontsize='large')
    plt.ylabel("Counter Torque",fontsize='large')
    plt.legend(fontsize='large')
    st.pyplot(plt.gcf())
