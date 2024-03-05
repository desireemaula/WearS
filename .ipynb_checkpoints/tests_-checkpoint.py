import utils
import time
import numpy as np
import pandas as pd
from datetime import datetime

def sensing_test(L, R, C, smu,k, conc, diode_df_dict, diode_dict_list, mean_std, mean_std_L, mean_std_R,DUT, TOT, couple, baseline):
    """
    The function `sensing_test` conducts a series of diode sensing tests and analyzes the results.
    It iterates over 20 runs, acquiring data from a diode connection each time.
    The function calculates the mean and standard deviation of the last Nlastvalues of the last Nvalidsteps for various parameters related to 'VDL' and 'VDR'.
    It then saves the collected data into Excel files. 
    
    Input:
    - `k`: Index for data management.
    - `conc`: str list of different concentrations.
    - `diode_df_dict`: dictionary where to store the df with the 20 sweeps of all the concentrations
    - `diode_dict_list`: dictionary where to store the list with the 20 sweeps of all the concentrations
    - `mean_std`, `mean_std_L`, `mean_std_R`: Lists for storing statistical data.
    - `L`,`R`, `C`: 'CH1', 'CH2' or 'CH3'

    """
    stop = 0
    step = 1
    tol = 0.001
    Nvalidsteps = 6
    Nlastvalues = 5
    diode_df_list = []
    
    # Loop for 20 runs
    for i in range(20):
        print('Run #:',i+1)
        diode_df_list.append(smu.diode_connection(L, R, C, '0', '300E-09', '5E-09'))
        time.sleep(10) # Wait for 10 seconds before the next run

    data_save = pd.concat(diode_df_list)  # saving the 20 sweeps in one df
    data_save['DIFFV'] = abs(data_save['VDL']- data_save['VDR']) # Calculate the difference between 'VDL' and 'VDR' and add it as a new column
    
    # Store dataframes and lists into dictionaries
    diode_df_dict[conc[k]] = data_save  
    diode_dict_list[conc[k]] = diode_df_list
    
    # Calculate mean and standard deviation of the last 5 measurements
    mean_last5 = (calculate_mean_std(Nlastvalues,Nvalidsteps,df_list,'VDL')[0]-calculate_mean_std(Nlastvalues,Nvalidsteps,df_list,'VDL')[0])
    std_last5 = np.std(np.mean([(subdf['VDL'].iloc[-Nlastvalues:]-subdf['VDR'].iloc[-Nlastvalues:]).values for subdf in diode_df_list[-Nvalidsteps:]],1))
    
    mean_std.append([mean_last5, std_last5])
    mean_std_L.append([calculate_mean_std(Nlastvalues,Nvalidsteps,df_list,'VDL')])
    mean_std_R.append([calculate_mean_std(Nlastvalues,Nvalidsteps,df_list,'VDR')])

    # Save dataframes to Excel files
    folder = utils.save_xls(diode_df_dict, DUT,TOT,couple+'-AS-'+conc[k])
    
    if k == 0: baseline = mean_std[0][0]
    mean_std[k][0] = mean_std[k][0]-baseline
    k = k+1
    print(mean_std)
    
    return k, diode_df_dict, diode_dict_list, mean_std, mean_std_L, mean_std_R, folder, baseline

import time
import numpy as np
import utils

def stability_test(L, R, C, smu, diode_df, mean_diff, mode, couple, DUT, TOT, max_steps):
    """
    Perform a stability test on a device using an SMU.

    Inputs:
    - smu: An instance of the Source Measurement Unit used for measurements.
    - diode_df: A DataFrame containing diode data collected during measurements.
    - mean_diff: A list to calculate mean differences during the stability test.
    - mode: The test mode controlling various parameters. ['sensing']
    - couple: The couple used for measurements.
    - DUT: The Device Under Test for which stability is being evaluated.
    - TOT: Type of Test.
    - max_steps: The maximum number of steps allowed for the stability test.
    - L,R,C: 'CH1', 'CH2', or 'CH3'
    """
    stop = False
    step = 0
    mean = []
    tol_std = 0.0005
    tol_mean = 0.002

    # Perform initial diode connection
    current_stop = '300E-09' if mode == 'sensing' else '1E-06'
    diode_df.append(smu.diode_connection(L, R, C, '0', current_stop, '5E-09'))
    time.sleep(10)

    # Check diode connection status
    if diode_df[0]['IDL'].max() == 20 or diode_df[0]['IDR'].max() == 20:
        raise Exception("Device not connected correctly") 

    while not stop:
        step += 1 
        print("Sweep #:", step)
        
        if step > max_steps:
            utils.save_xls(diode_df, DUT, TOT, couple, 2)
            raise Exception("Too many steps performed without stability")

        if step % 5 == 0:
            utils.plot_max_values(diode_df, ['baseline'], couple, step, DUT, TOT)
            utils.plot_max_values(diode_df, ['baseline'], couple, step, DUT, TOT, mode=3)

        # Perform diode connection and calculate mean differences
        diode_df.append(smu.diode_connection(L, R, C, '0', current_stop, '5E-09'))
        diff = abs((diode_df[step-2]['VDL'].iloc[-10:] - diode_df[step-2]['VDR'].iloc[-10:]) - 
                   (diode_df[step-1]['VDL'].iloc[-10:] - diode_df[step-1]['VDR'].iloc[-10:])).mean() #mean (|VDL-VDR|_step(i)-|VDL-VDR|_step(i-1)) of the last 10 values
        VDL_VDR = abs((diode_df[step-1]['VDL'].iloc[-10:] - diode_df[step-1]['VDR'].iloc[-10:])).mean()  #mean |VDL-VDR| of the last 10 values
        
        mean_diff.append(diff)
        mean.append(VDL_VDR)

        # Display calculated metrics
        print('|VDL-VDR|: ', round(VDL_VDR, 5))
        print('mean diff of diff L-R:', round(np.mean(mean_diff[1:]), 5))
        print('std diff of diff L-R:', round(np.std(mean_diff[1:]), 5))
        
        if step >= 8:
            print('std of the diff for last 8', round(np.std(mean[-8+step:step]), 5))

        # Check stability conditions
        if (step >= 10 and np.std(mean[-8+step:step]) < tol_std and 
                np.mean(mean_diff[-8+step:step]) < tol_mean):
            print(np.std(mean_diff[10:]))
            print('Device correctly stabilized')
            stop = True   

        time.sleep(10)

    # Save data to Excel and return results
    utils.save_xls(diode_df, DUT, TOT, couple, 2)
    return diode_df, mean_diff
