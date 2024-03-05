import os
from pandas import ExcelWriter
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pandas as pd
from datetime import datetime

#os.chdir(r"C:\Users\Desi\Desktop\TesiStanford\keithley_results")
path =  os.getcwd()

def plot_max_values(list_df, conc, couple,step,DUT,TOT, mode = 1, folder = None):
    
    # If list_df is a list
    if isinstance(list_df, list):
        diff_in_time = pd.concat(list_df, ignore_index=False)
        numberoftests = 1
    # If list_df is a dict
    elif isinstance(list_df, dict):
        diff_in_time = pd.concat(list_df.values(), ignore_index=False)
        numberoftests = len(list_df)
    else:
        raise ValueError("Invalid input type for list_df. Expected list or dict.")
        
    colors_L = sns.color_palette("Blues",25)
    colors_R = sns.color_palette("YlOrBr",25)
    colors_diff = sns.light_palette("seagreen",25)

    diff_in_time_grouped = diff_in_time.groupby(diff_in_time.index)
    threshold = diff_in_time.index.max()

    diff_in_time_max = [group for name, group in diff_in_time_grouped if name >= threshold]
    
    fig, ax = plt.subplots(figsize = (15,5))
    for i in range(numberoftests):
        if mode == 1 or mode == 3:
            ax.scatter(range(i*int(len(diff_in_time_max[0])/numberoftests),(1+i)*int(len(diff_in_time_max[0])/numberoftests)),
            (abs(diff_in_time_max[0][i*int(len(diff_in_time_max[0])/numberoftests):(1+i)*int(len(diff_in_time_max[0])/numberoftests)]['VDL']
            -diff_in_time_max[0][i*int(len(diff_in_time_max[0])/numberoftests):(1+i)*int(len(diff_in_time_max[0])/numberoftests)]['VDR'])
            -abs(diff_in_time_max[0].iloc[0]['VDL']-diff_in_time_max[0].iloc[0]['VDR']))*1000, label = conc[i], color = colors_diff[10+i] )
        if mode == 2 or mode == 3:
            ax.scatter(range(i*int(len(diff_in_time_max[0])/numberoftests),(1+i)*int(len(diff_in_time_max[0])/numberoftests)), (diff_in_time_max[0]
            [i*int(len(diff_in_time_max[0])/numberoftests):(1+i)*int(len(diff_in_time_max[0])/numberoftests)]['VDL']-diff_in_time_max[0].iloc[0]['VDL'])*1000,
            label = 'Left-'+conc[i], color = colors_L[10+i])
            ax.scatter(range(i*int(len(diff_in_time_max[0])/numberoftests),(1+i)*int(len(diff_in_time_max[0])/numberoftests)), (diff_in_time_max[0]
            [i*int(len(diff_in_time_max[0])/numberoftests):(1+i)*int(len(diff_in_time_max[0])/numberoftests)]['VDR']-diff_in_time_max[0].iloc[0]['VDR'])*1000,
            label = 'Right-'+conc[i], color = colors_R[10+i])

    
    ax.set_xlabel('Index')
    ax.set_ylabel('Value [mV]')
    plt.title('Change of Max values in time')
    plt.grid()
    plt.legend()
    if folder : plt.savefig(folder+"\plotmaxvalues-"+couple+"-"+DUT+TOT+".jpeg")
    plt.show()
    
    
def create_folder(device_name,type_of_test,additional_comment= None):
    """
    create a new folder of the type mmddyyyy-devicename-type_of_test-additional_comment
    return path of the folder
    """
    today = datetime.now()
    if additional_comment:
        os.mkdir(today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test+'-'+additional_comment)
        return today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test+'-'+additional_comment
    else:
        os.mkdir(today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test)
        return today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test

                 
def save_xls(list_df, device_name,type_of_test,additional_comment= None, mode = 1):
    """
    Save a list of dataframes to an excel file, 
    with each dataframe as a separate page
    """  
    today = datetime.now()
    if os.path.isdir(today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test)!=1:
        directory = create_folder(device_name,type_of_test)
        print('The directory doesn\'t exist')
    else:
        directory = today.strftime('%m%d%Y')+'-'+device_name+'-'+type_of_test
        print('The directory exists')
        
    path_ = os.path.join(path, directory) 
    print(path_)
    if additional_comment:
        writer = ExcelWriter(path_+'/'+directory+additional_comment+'.xlsx')
    else:
        writer = ExcelWriter(path_+'/'+directory+'.xlsx')

    if mode == 1:
        for key in list_df.keys():
            list_df[str(key)].to_excel(writer, sheet_name="step #" + str(key))   
        
    else:
        for key in range(len(list_df)):
            list_df[key].to_excel(writer, sheet_name="step #" + str(key))
    writer.save()
    return directory
    
def plot_mean_std(k, mean_std_L,mean_std_R, mean_std, conc, couple, folder = None):
    fig, ax = plt.subplots(figsize = (10,8))
    L = [i[0]*1000 - mean_std_L[0][0]*1000 for i in mean_std_L]
    R = [i[0]*1000 - mean_std_R[0][0]*1000 for i in mean_std_R]
    plt.scatter(conc[:k], [i[0]*1000 for i in mean_std] )
    plt.errorbar(conc[:k], [i[0]*1000 for i in mean_std], yerr=[i[1]*1000 for i in mean_std], label='std')
    plt.scatter(conc[:k], L )
    plt.errorbar(conc[:k], L, yerr=[i[1]*1000 for i in mean_std_L], label='std_L')
    plt.scatter(conc[:k], R )
    plt.errorbar(conc[:k], R, yerr=[i[1]*1000 for i in mean_std_R], label='std_R')
    plt.xlabel('Concentration')
    plt.ylabel('DeltaV [mV]')
    plt.title('Mean and Std DeltaV dor different concentrations (last 5 values of the last 6 steps)')
    plt.legend()
    plt.grid()
    if folder : plt.savefig(folder+"\meanL_R_diff_last5-"+couple+".png")
    
def calculate_mean_std(Nlastvalues,Nvalidsteps,df_list, column):
    mean = np.mean([(subdf[column].iloc[-Nlastvalues:]).values for subdf in diode_df_list[-Nvalidsteps:]])
    std = np.std(np.mean([(subdf[column].iloc[-Nlastvalues:]).values for subdf in diode_df_list[-Nvalidsteps:]],1))
    return mean,std
   
    
def calculate_vth(datax,datay, plot = None):
    """
    Compute the Vth starting from a VGS-IDS curve in the saturation regime with linear extrapolation
    and plot the corresponding curves if plot = None
    Input:
        datax = X axis data (VGS) 
        datay = Y axis data (IDS) -> non squared! 
        
    """
    sqrty =  np.sqrt(datay)
    
    IdS_derivative = np.gradient(sqrty, datax)
    # Find the max derivative point
    index_max_derivative = np.argmax(IdS_derivative)
    vgs_max_derivative = vgs[index_max_derivative]

    # Compute Vth using the linear extrapolation with y = 0 (IdS = 0)
    Vth = -sqrty[index_max_derivative]/np.max(IdS_derivative)+vgs_max_derivative
    
    if plot:
        plt.plot(vgs, tangent_equation, 'g--', label='Tangente')
        # Plot della curva IdS vs vgs e del punto di massima derivata
        plt.plot(vgs, IdS_sqrt, 'bo', label='sqroot(IdS)')
        plt.xlabel('$v_{gs}$ (V)')
        plt.ylabel('$IdS$ (A)')
        plt.title('Curva IdS vs vgs')
        plt.plot(vgs_max_derivative, IdS_max_derivative, 'ro', label=f'Point of Max derivate: {vgs_max_derivative:.2f} V')  # Punto di massima derivata
        plt.plot(Vth, 0, 'mo', label=f'Vth: {Vth:.2f} V')  # Punto di massima derivata

        plt.ylim(-0.0001, 0.0011)
        plt.xlabel('$v_{gs}$ (V)')
        plt.ylabel('$IdS$ (A)')
        plt.title('IdS vsVvgs Curve')
        plt.legend()
        plt.grid(True)
        plt.show()

        
    return Vth