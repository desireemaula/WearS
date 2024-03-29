import os
from pandas import ExcelWriter
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pandas as pd
from datetime import datetime
import numpy as np

#os.chdir(r"C:\Users\Desi\Desktop\TesiStanford\keithley_results")
path =  os.getcwd()

def plot_max_values(list_df, conc, couple,step,DUT,TOT, mode = 1, folder = None):
    """
    Plot the change of max values over time.
    
    Parameters:
    - list_df (list or dict): List or dictionary containing DataFrame objects.
    - conc (list): List of concentrations.
    - couple (str): Description of the FET couple under test.
    - step (str): Description of the step.
    - DUT (str): Description of the DUT.
    - TOT (str): Description of the TOT.
    - mode (int, optional): Mode for plotting. Default is 1. if mode = 2 -> VDL and VDR are plotted. If mode = 2: VDL, VDR, VDL-VDR are plotted
    - folder (str, optional): Folder to save the plot image. Default is None.

    Returns:
    - None
    """
    
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
    
    return
    
    
def create_folder(device_name,type_of_test,additional_comment= None):
    
    """
    create a new folder of the type mmddyyyy-devicename-type_of_test-additional_comment
    return path of the folder
    
    Parameters:
    - device_name (str): name of the DUT
    - type_of_test (str): TOT
    - additional_comment (str): remark you might want to add in the folder name
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
    Save a list of DataFrames to an Excel file, with each DataFrame as a separate sheet.

    Parameters:
    - list_df (list or dict): List or dictionary containing DataFrame objects.
    - device_name (str): Name of the device.
    - type_of_test (str): Type of test performed.
    - additional_comment (str, optional): Additional comment to include in the file name. Default is None.
    - mode (int, optional): Mode for saving the Excel file. Default is 1.

    Returns:
    - directory (str): Name of the directory where the Excel file is saved.
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
        for key, df in enumerate(list_df):
            list_df[key].to_excel(writer, sheet_name="step #" + str(key))
    writer.close()
    return directory
    
def plot_mean_std(k, mean_std_L,mean_std_R, mean_std, conc, couple, folder = None):
    """
    Plot mean and standard deviation for left and right sides.

    Parameters:
    - k (int): Number of concentration you want to show.
    - mean_std_L (list): List of mean and standard deviation for the VDL.
    - mean_std_R (list): List of mean and standard deviation for the VDR.
    - mean_std (list): List of mean and standard deviation for VDL-VDR.
    - conc (list): List of concentrations.
    - couple (str): Description of the FET couple.
    - folder (str, optional): Folder to save the plot image. Default is None.

    Returns:
    - None
    """ 
    col_L = '#1E5986'
    col_R = '#BF8F00'
    col_diff = "#FF8080"
    
    fig, ax = plt.subplots(figsize = (11.69,8.26))
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    ax.tick_params(axis='both', width=1.5, length=8, labelsize=26)


    L = [i[0]*1000 - mean_std_L[0][0]*1000 for i in mean_std_L]
    R = [i[0]*1000 - mean_std_R[0][0]*1000 for i in mean_std_R]
    plt.scatter(conc[:k], [i[0]*1000 for i in mean_std], color = col_diff, label='Diff OFET' , linewidth = 3)
    plt.errorbar(conc[:k], [i[0]*1000 for i in mean_std], yerr=[i[1]*1000 for i in mean_std], color = col_diff, linewidth = 3)
    plt.scatter(conc[:k], L , color = col_L, label='Left OFET', linewidth = 3)
    plt.errorbar(conc[:k], L, yerr=[i[1]*1000 for i in mean_std_L], color = col_L, linewidth = 3)
    plt.scatter(conc[:k], R , color = col_R, label='Right OFET', linewidth = 3)
    plt.errorbar(conc[:k], R, yerr=[i[1]*1000 for i in mean_std_R], color = col_R, linewidth = 3)
    plt.xlabel('Concentration', fontsize = 36)
    plt.ylabel('V-$V_{baseline}$ [mV]', fontsize = 36)
    #plt.title('Mean and Std DeltaV dor different concentrations (last 5 values of the last 6 steps)')
    plt.legend( fontsize=22, frameon=False)
    #plt.grid()
    if folder : plt.savefig(folder+"\meanL_R_diff_last5-"+couple+".png",bbox_inches='tight')
    
def calculate_mean_std(Nlastvalues,Nvalidsteps,df_list, column):
    """
    Calculate the mean and standard deviation of the specified column from the last Nlastvalues values
    of the last Nvalidsteps steps in the given list of DataFrames.

    Parameters:
    - Nlastvalues (int): Number of last values to consider for calculating mean and standard deviation.
    - Nvalidsteps (int): Number of last steps to consider for calculating mean and standard deviation.
    - df_list (list): List of DataFrame objects.
    - column (str): Name of the column for which mean and standard deviation are calculated.

    Returns:
    - mean (float): Mean value of the specified column from the last Nlastvalues values of the last Nvalidsteps steps.
    - std (float): Standard deviation of the specified column from the last Nlastvalues values of the last Nvalidsteps steps.
    """
    last_values = np.array([subdf[column].iloc[-Nlastvalues:].values for subdf in df_list[-Nvalidsteps:]])
    mean = np.mean(last_values)
    std = np.std(np.mean(last_values, axis=1))
    return [mean, std]
   
    
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
    vgs_max_derivative = datax[index_max_derivative]

    # Compute Vth using the linear extrapolation with y = 0 (IdS = 0)
    Vth = -sqrty[index_max_derivative]/np.max(IdS_derivative)+vgs_max_derivative
    
    if plot:
        plt.plot(datax, tangent_equation, 'g--', label='Tangente')
        # Plot della curva IdS vs vgs e del punto di massima derivata
        plt.plot(datax, IdS_sqrt, 'bo', label='sqroot(IdS)')
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

def save_table_xlsx(data, TOT, name_file):
    """
    save the data in an xlsx file of the type 'mmddyyyy-name_file' in the main path
    input:
        data = np array of data to save in the xlsx file (i.e., [mean_L, std_L, mean_R, std_L], where mean_L etc are array of data)
        name_columns = str array to name the columns of the table with (non mandatory)
        TOT = str - type of test
        name_file = str - name of the table
    """
    path = create_folder('_',TOT)
    table = pd.DataFrame(data).transpose().rename(columns = {0: 'Mean_L [mV]', 1: 'std_L [mV]', 2: 'Mean_R [mV]', 3: 'std_R [mV]', 4: 'Diff |Vl-VR| [mV]', 5: 'std diff [mV]'})
    table.to_excel(path+"\_"+name_file+".xlsx")
    return