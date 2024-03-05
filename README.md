# WearS

This repository contains three Python files:

- **utils.py**: This file includes various utility functions such as:
  - plot_max_values
  - create_folder
  - save_xls
  - plot_mean_std
  - calculate_mean_std
  - calculate_vth
  
- **tests.py**: The file contains functions related to testing, including:
  - sensing_test
  - stability_test
  
- **keithleyAPI**: This API facilitates connection with the 4200-SCS from Keithley and enables the execution of tests such as diode_connection, VGS_IDS, and conductivity.

The **Sensing** folder includes a Jupyter notebook named 'DiodeSensingTest.jpynb', which outlines the protocol for conducting the Sensing Test. This protocol guides users through checking the correct stabilization of the device under testing (DUT) and selecting the specific Type Of Test (TOT) they wish to run. The notebook automatically saves the results in the xlsx format. Additionally, the notebook 'DiodeSensingTest-Postproc.jpynb' contains functions designed to assist with post-processing the acquired data.

The folders **PCB**, **Ion Sensing**, and **Stability Test** contain post-processing Jupyter notebooks.

## How to Use This Repository:

1. **Download Anaconda**: Download Anaconda from [here](https://www.anaconda.com/download). Ensure that you have the following packages installed: numpy, pandas, matplotlib, os, sys, seaborn, datetime, plotly, re. You can install these packages by opening your Anaconda prompt and typing `pip install <name of the package>`.

2. **Clone the Repository**: Change the current working directory to the location where you want the cloned directory to be. Type `cd <path where you want to clone the repo>` in your command prompt. Then, type `git clone <url of the repository>`. You can find the link to the repository [here](https://github.com/desireemaula/WearS).

3. **Run and Use the Repository**: Open the Anaconda prompt, type `cd <path where the repo is cloned>`, and then type `jupyter lab`. You can use any other type of environment if you prefer (e.g., Visual Studio is suggested).
