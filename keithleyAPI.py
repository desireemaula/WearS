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
    
    def VgsIds(self, gate, source, drain, vds, compliance_vds, vg_start,vg_stop,vg_step, compliance_vg, speed):
        """
        VgsIds program
        gate, source, drain: str of the channel ['CH1','CH2','CH3']
        """
        
        self._instrument_object.query("DE") # channel definition page
        self._instrument_object.query(gate+", 'VG', 'IG', 1, 1")
        self._instrument_object.query(drain+", 'VD', 'ID', 1, 3")
        self._instrument_object.query(source+", 'VS', 'IS', 1, 3")
        self._instrument_object.query("SS")
        self._instrument_object.query("VR"+gate[2]+", "+vg_start+", "+vg_stop+", "+vg_step+", "+compliance_vg)
        self._instrument_object.query("VC"+drain[2]+", "+vds+", "+compliance_vds)
        self._instrument_object.query("VC"+source[2]+", 0, 0.1")
        self._instrument_object.query("HT 0")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT"+speed)
        self._instrument_object.query("RS 5")
        self._instrument_object.query("RG 1, 1e-9")
        self._instrument_object.query("RG 2, 1e-9")
        #self._instrument_object.query("RG 3, 1e-9")
        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'VG', 1,"+vg_start+", "+vg_stop)
        self._instrument_object.query("YA 'ID', 1, 0, 0.04")
        self._instrument_object.query("YB 'IG', 1, 0, 0.04")
        self._instrument_object.query("MD")
        self._instrument_object.query("ME1")
        # wait for measurement to complete

        status = self._instrument_object.query("SP")
        while int(status) != 1:
            status = self._instrument_object.query("SP")
            time.sleep(1)

        dataID1 = self._instrument_object.query("DO 'ID'")
        dataVG1 = self._instrument_object.query("DO 'VG'")
        dataIG1 = self._instrument_object.query("DO 'IG'")
        dataVD1 = self._instrument_object.query("DO 'VD'")
        

        data = pd.DataFrame()
        data['Ids'] = pd.Series(str(dataID1).split(dataID1[0])[1:]).apply(lambda x: float(x[:-1]))       
        data['Igs'] = pd.Series(str(dataIG1).split(dataIG1[0])[1:]).apply(lambda x: float(x[:-1]))        
        data['Vgs'] = pd.Series(str(dataVG1).split(dataVG1[0])[1:]).apply(lambda x: float(x[:-1]))
        data['Vds'] = pd.Series(str(dataVD1).split(dataVD1[0])[1:]).apply(lambda x: float(x[:-1]))
        

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

    def diode_connection(self, Left, Right, Common, current_start, current_stop, step):
        """
        Performs a diode connection test. Sources current to two diode connected transistors and measures the voltage between Common-Left and Common Right
        
        Input:
        Left, Right, Common: str ('CH3','CH2','CH1')
        current start: str in [A]
        current stop: str in [A]
        step: str in [A]
        
        Returns a pandas dataframe with "VDL","VDR","IDL","IDR" columns
        
        """

        self._instrument_object.query("DE")
        self._instrument_object.query(Right+", 'VDR', 'IDR', 2, 1")
        self._instrument_object.query(Common+", 'VG', 'IG', 3, 3")
        self._instrument_object.query("SS")
        self._instrument_object.query("IR1, "+current_start+", "+current_stop+", "+step+", 10")

        self._instrument_object.query("HT 0.001")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("DE")
        self._instrument_object.query(Left+", 'VDL', 'IDL', 2, 1")
        self._instrument_object.query("SS")
        self._instrument_object.query("IR1, "+current_start+", "+current_stop+", "+step+", 10")

        self._instrument_object.query("HT 0.001")
        self._instrument_object.query("DT 0.001")
        self._instrument_object.query("IT2")
        self._instrument_object.query("RS 5")

        self._instrument_object.query("SM")
        self._instrument_object.query("DM1")
        self._instrument_object.query("XN 'IDL', 1, "+current_start+", "+current_stop)
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
