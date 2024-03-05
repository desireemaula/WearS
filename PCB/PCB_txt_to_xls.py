import sys
sys.path.append('..')

from utils import save_xls
import pandas as pd

path = r"C:\Users\Desi\Desktop\TesiStanford\iSENS_2024_2_19_18_54_27.txt"  # path of the txt file you want to analyze
f = open(path,"r") 

data = pd.DataFrame()
columns = ['time','DAC','Ch1','Ch2']
for i,line in enumerate(f):
    data[columns[i]] = line.split(',')
    
save_xls([data], 'iSENS_2024_2_19_18_54_27','PCB_data',additional_comment= None, mode = 2)