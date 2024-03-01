"""
    Copyright 2023 Tektronix, Inc.                      
    See www.tek.com/sample-license for licensing terms. 
"""

from pyvisa.highlevel import ResourceManager
import pyvisa.constants as pyconst
import pandas as pd
import time
import re
from functools import reduce
from datetime import datetime

class Communications:
    """
    This class offers the consumer a collection of wrapper menthods that
    leverage PyVisa calls and attempts to condense collections of methods
    therein while also adding in a means for echoing command calls to the
    terminal if the appropriate internal attribute is set to True. 

    Note that this is a work in progress and by no means a work of 
    perfection. Please feel free to copy, reuse, or enhance to your own
    liking and feel free to leave suggestions for improvement. Thanks!
    """

    def __init__(self, instrument_resource_string=None):
        self._instrument_resource_string = instrument_resource_string
        self._resource_manager = None
        self._instrument_object = None
        self._timeout = 20000
        self._echo_cmds = False
        self._version = 1.1

        try:
            if self._resource_manager is None:
                self._resource_manager = ResourceManager()
        except visa.VisaIOError as visaerror:
            print(f"{visaerror}")
        except visa.VisaIOWarning as visawarning:
            print(f"{visawarning}")

    def connect(self, instrument_resource_string=None, timeout=None):
        """
        Open an instance of an instrument object for remote communication.

        Args:
            timeout (int): Time in milliseconds to wait before the \
                communication transaction with the target instrument\
                    is considered failed (timed out).
            
        Returns:
            None
        """
        try:
            if instrument_resource_string != None:
                self._instrument_resource_string = instrument_resource_string
                
            self._instrument_object = self._resource_manager.open_resource(
                self._instrument_resource_string
            )

            if timeout is None:
                self._instrument_object.timeout = self._timeout
            else:
                self._instrument_object.timeout = timeout
                self._timeout = timeout

            # Check for the SOCKET as part of the instrument ID string and set
            # the following accordingly...
            if "SOCKET" in self._instrument_resource_string:
                self._instrument_object.write_termination = "\n"
                self._instrument_object.read_termination = "\n"
                self._instrument_object.send_end = True

        except visa.VisaIOError as visaerr:
            print(f"{visaerr}")
        return

    def configure_rs232_settings(
        self,
        baudrate=9600,
        databits=8,
        parity=0,
        stopbits=1,
        flowcontrol=0,
        writetermination="\n",
        readtermination="\n",
        sendend=True,
    ):
        """
            This method pulls the collection of RS-232 settings together in 
            one location. For applicable PyVisa-specific constants that best
            align with this method's use, refer to documentation on
            pyvisa.constants. 

        Args:
            baudrate (int): Defines the baud rate to be used for data \
                transmission. Options are typically 2400, 4800, 9600, and \
                    others up to 115200. Refer to your instrument documentation \
                        for what is truly applicable. 
            databits (int): Typically 8, sometimes 7.
            parity (pyconst.Parity): Options include none, odd, and even.
            stopbits (pyconst.StopBits): Options include one and two.
            flowcontrol (pyconst.ControlFlow): Options include none, xon/xoff, \
                rts/cts, and dtr/dsr.
            read_terminator (str): Character options include "\\n" and "\\r".
            sendend (bool): Specifies whether or not the end character is to be \
                sent. 

        Returns:
            None
        """
        # First verify that the instrument resource string has "ASRL" so
        #   we know it connected as a serial instrument.
        if "ASRL" in self._instrument_resource_string:
            self._instrument_object.baud_rate = baudrate
            self._instrument_object.data_bits = databits
            if parity == 0:
                self._instrument_object.parity = pyconst.Parity.none
            elif parity == 1:
                self._instrument_object.parity = pyconst.Parity.odd
            elif parity == 2:
                self._instrument_object.parity = pyconst.Parity.even

            if stopbits == 0:
                self._instrument_object.stop_bits = pyconst.StopBits.one_and_a_half
            elif stopbits == 1:
                self._instrument_object.stop_bits = pyconst.StopBits.one
            elif stopbits == 2:
                self._instrument_object.stop_bits = pyconst.StopBits.two

            if flowcontrol == 0:
                self._instrument_object.flow_control = pyconst.ControlFlow.none
            elif flowcontrol == 1:
                self._instrument_object.flow_control = pyconst.ControlFlow.xon_xoff
            elif flowcontrol == 1:
                self._instrument_object.flow_control = pyconst.ControlFlow.rts_cts
            elif flowcontrol == 1:
                self._instrument_object.flow_control = pyconst.ControlFlow.dtr_dsr

            self._instrument_object.write_termination = writetermination
            self._instrument_object.read_termination = readtermination
            self._instrument_object.send_end = sendend

        else:
            print("raise an exception")

    def disconnect(self):
        """
        Close an instance of an instrument object.

        Args:
            None

        Returns:
            None
        """
        try:
            self._instrument_object.close()
        except visa.VisaIOError as visaerr:
            print(f"{visaerr}")
        return

    def write(self, command: str):
        """
        Issue controlling commands to the target instrument.

        Args:
            command (str): The command issued to the instrument to make it\
                perform some action or service.

        Returns:
            None
        """
        try:
            if self._echo_cmds is True:
                print(command)
            self._instrument_object.write(command)
        except visa.VisaIOError as visaerr:
            print(f"{visaerr}")
        return

    def read(self):
        """
        Used to read commands from the instrument.

        Args:
            None

        Returns:
            (str): The requested information returned from the target
            instrument.
        """
        return self._instrument_object.read()

    def query(self, command: str):
        """
        Used to send commands to the instrument  and obtain an information
        string from the instrument. Note that the information received will
        depend on the command sent and will be in string format.

        Args:
            command (str): The command issued to the instrument to make it
            perform some action or service.

        Returns:
            (str): The requested information returned from the target
            instrument.
        """
        response = ""
        try:
            if self._echo_cmds is True:
                print(command)
            response = self._instrument_object.query(command).rstrip()
        except visa.VisaIOError as visaerr:
            print(f"{visaerr}")

        return response
    
    def VgsIds(self):
        """
        VgsIds program
        """
        
        self._instrument_object.query("DE")
        self._instrument_object.query("CH2, 'VG', 'IG', 1, 1")
        self._instrument_object.query("CH1, 'VD', 'ID', 1, 3")
        self._instrument_object.query("CH3, 'VS', 'IS', 1, 3")
        self._instrument_object.query("SS")
        self._instrument_object.query("VR1, 2, -5, -0.05, 100e-3")
        self._instrument_object.query("VC3, -5, 0.01")
        self._instrument_object.query("VC1, 0, 0.1")
        self._instrument_object.query("HT 0")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")
        self._instrument_object.query("RG 1, 1e-6")
        self._instrument_object.query("RG 2, 1e-6")
        self._instrument_object.query("RG 3, 1e-6")
        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'VG', 1, -5, 2")
        self._instrument_object.query("YA 'ID', 1, 0, 0.04")
        self._instrument_object.query("YB 'IG', 1, 0, 0.04")
        self._instrument_object.query("MD")
        self._instrument_object.query("ME1")
        # wait for measurement to complete

        status = self._instrument_object.query("SP")
        while int(status) != 1:
            status = self._instrument_object.query("SP")
            time.sleep(1)

        dataID1 = self._instrument_object.query("DO'ID'")
        dataVG1 = self._instrument_object.query("DO 'VG'")
        dataIG1 = self._instrument_object.query("DO 'IG'")

        self._instrument_object.query("SS")
        self._instrument_object.query("VR1, -4.95, 2, 0.05, 0.001")
        self._instrument_object.query("VC3, -5, 0.01")
        self._instrument_object.query("VC1, 0, 0.1")
        self._instrument_object.query("HT 0")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")
        self._instrument_object.query("RG 1, 1e-6")
        self._instrument_object.query("RG 2, 1e-6")
        self._instrument_object.query("RG 3, 1e-6")
        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'VG', 1, -5, 2")
        self._instrument_object.query("YA 'ID', 1, 0, 0.04")
        self._instrument_object.query("YB 'IG', 1, 0, 0.04")
        self._instrument_object.query("MD")
        self._instrument_object.query("ME1")

        status = self._instrument_object.query("SP")
        while int(status) != 1:
            status = self._instrument_object.query("SP")
            time.sleep(1)

        dataID2 = self._instrument_object.query("DO'ID'")
        dataVG2 = self._instrument_object.query("DO 'VG'") #try with the T, VGT
        dataIG2 = self._instrument_object.query("DO 'IG'")

        data = pd.DataFrame()
        data['Id1'] = pd.Series(str(dataID1).split(dataID1[0])[1:]).apply(lambda x: float(x[:-1]))
        data['Id2'] = pd.concat(data['Id1'].loc[0],pd.Series(str(dataID2).split(dataID2[0])[1:]).apply(lambda x: float(x[:-1])))
        data['Ig1'] = pd.Series(str(dataIG1).split(dataIG1[0])[1:]).apply(lambda x: float(x[:-1]))
        data['Ig2'] = pd.Series(str(dataIG2).split(dataIG2[0])[1:]).apply(lambda x: float(x[:-1]))
        data['Vg1'] = pd.Series(str(dataVG1).split(dataVG1[0])[1:]).apply(lambda x: float(x[:-1]))
        #data['Vg2'] = pd.Series(str(dataVG2).split(dataVG2[0])[1:]).apply(lambda x: float(x[:-1]))

        return data
    
    
    def diode_connection_constantbias(self, mode = None):
        """
        Ch3 and Ch1 are biasing, Ch2 is in common  mode
        
        """
        self._instrument_object.query("DE")
        self._instrument_object.query("CH3, 'VDR', 'IDR', 2, 3")
        self._instrument_object.query("CH2, 'VG', 'IG', 3, 3")
        self._instrument_object.query("SS")
        self._instrument_object.query("IC1, 0.1, +10") # bias current 0.1

        self._instrument_object.query("HT 0.001")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("DE")
        self._instrument_object.query("CH1, 'VDL', 'IDL', 2, 3")
        self._instrument_object.query("SS")
        self._instrument_object.query("IC1, 0.1, +10") # bias current

        self._instrument_object.query("HT 0")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'IDL', 1, 0, 1E-06")
        self._instrument_object.query("YA 'VDL', 1, 0, 20")
        self._instrument_object.query("YB 'VDR', 1, 0, 20")
        self._instrument_object.query("NR 10")
        self._instrument_object.query("MD")
        self._instrument_object.query("ME1")
        start_time = time.time()
        elapsed_time = time.time() - start_time
        # wait for measurement to complete

        status = smu.query("SP")
        #print(status)
        while elapsed_time < 10  :
            print(elapsed_time)
            elapsed_time = time.time() - start_time
            status = self._instrument_object.query("SP")
            #print(status)
            time.sleep(1)

        dataVDL = self._instrument_object.query("DO 'VDL'")
        dataVDR = self._instrument_object.query("DO 'VDR'")
        dataIDL = self._instrument_object.query("DO 'IDL'")
        dataIDR = self._instrument_object.query("DO 'IDR'")

        diode_df = pd.DataFrame()
        diode_df["VDL"] = pd.Series(re.split(r'[NC]', dataVDL)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["VDR"] = pd.Series(re.split(r'[NC]', dataVDR)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["IDL"] = pd.Series(re.split(r'[NC]', dataIDL)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["IDR"] = pd.Series(re.split(r'[NC]', dataIDR)[1:]).apply(lambda x: float(x[:-1]))

        return diode_df
    
    ## Diode connections

    def diode_connection(self, mode = None):
        """
        Performs a diode connection test.
        CH3 and CH1 sweeps current from 0 to 1uA if mode == 'stability', else from 0 to 300nA
        CH2 is in common mode
        
        Returns a pandas dataframe with "VDL","VDR","IDL","IDR" columns
        
        """

        self._instrument_object.query("DE")
        self._instrument_object.query("CH3, 'VDR', 'IDR', 2, 1")
        self._instrument_object.query("CH2, 'VG', 'IG', 3, 3")
        self._instrument_object.query("SS")
        if mode == 'stability': self._instrument_object.query("IR1, 0, 1E-06, 5E-09, 10")
        else: self._instrument_object.query("IR1, 0, 300E-09, 5E-09, 10")

        self._instrument_object.query("HT 0.001")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("DE")
        self._instrument_object.query("CH1, 'VDL', 'IDL', 2, 1")
        self._instrument_object.query("SS")
        if mode == 'stability': self._instrument_object.query("IR1, 0, 1E-06, 5E-09, 10")
        else: self._instrument_object.query("IR1, 0, 300E-09, 5E-09, 10")

        self._instrument_object.query("HT 0.001")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'IDL', 1, 0, 1E-06")
        self._instrument_object.query("YA 'VDL', 1, 0, 20")
        self._instrument_object.query("YB 'VDR', 1, 0, 20")
        self._instrument_object.query("MD")
        self._instrument_object.query("ME1")
        # wait for measurement to complete

        status = self._instrument_object.query("SP")
        #print(status)
        while int(status) != 1:
            status = self._instrument_object.query("SP")
            #print(status)
            time.sleep(1)

        dataVDL = self._instrument_object.query("DO 'VDL'")
        dataVDR = self._instrument_object.query("DO 'VDR'")
        dataIDL = self._instrument_object.query("DO 'IDL'")
        dataIDR = self._instrument_object.query("DO 'IDR'")

        diode_df = pd.DataFrame()
        diode_df["VDL"] = pd.Series(re.split(r'[NC]', dataVDL)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["VDR"] = pd.Series(re.split(r'[NC]', dataVDR)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["IDL"] = pd.Series(re.split(r'[NC]', dataIDL)[1:]).apply(lambda x: float(x[:-1]))
        diode_df["IDR"] = pd.Series(re.split(r'[NC]', dataIDR)[1:]).apply(lambda x: float(x[:-1]))

        return diode_df
