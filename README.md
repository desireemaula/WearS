# WearS

The repository provides three py files:

- utils.py: contains functions like:
  - plot_max_values
  - create_folder
  - save_xsl
  - plot_mean_std
  - calculate_mean_std
  - calculate_vth
- tests.py: contains functions like:
  - sensing_test
  - stability_test
- keithleyAPI: it's an API that connects with the 4200-SCS from Keithley and allows to perform tests like diode_connection, VGS_IDS and conductivity

The folder Sensing contains the jupyter notebook named 'DiodeSensingTest.jpynb' with the protocol for running Sensing Test. The protocol will guide you through the check of the correct stabilization of the device under testing (DUT) and the specific Type Of Test (TOT) you want to run. It will then automatically save the results in the xlsx format. The notebook 'DiodeSensingTest-Postproc.jpynb' contains function that will better help post processing the data acquired.

The folders PCB, Ion Sensing and Stability Test are postprocessing jupyter notebooks.

How to use this repository:

- Download anaconda from: https://www.anaconda.com/download
Packages to install:
numpy, pandas, matplotlib, os, sys, seaborn, datetime, plotly, re. 
To install these packages open your anaconda prompt and type 'pip install 'name of the package'
- Clone this repo:
Change the current working directory to the location where you want the cloned directory (type cd 'path where you want to clone the repo') on your command prompt. Type git clone 'url of the repository'
You can find the link of the repo here:
![image](https://github.com/desireemaula/WearS/assets/91323950/111505b4-b7a4-40e4-a16d-8551966d079f)
- Run and use the repo:
Open the anaconda prompt, type cd 'path where the repo is cloned', then type jupyter lab (you can use any other type of environment if you prefer (e.g., Visual Studio is suggested))

