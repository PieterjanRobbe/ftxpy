import os
import shlex
import subprocess

# special imports
from .batchscript import Batchscript
from .input import FTXInput
from .parameter import FTXParameter
from .utils import working_directory, occursin_file

# class that represents an FTX run
class FTXRun():
    """
    A class to represent an FTX run

    Methods
    -------
    get_work_dir()
        Returns the work dir of this FTX run
    change_work_dir(work_dir)
        Change the work directory for this FTX run to the given work directory
    write_files()
        Write the files for this FTX run
    start()
        Start this FTX run
    clean()
        Clean this run directory
    is_running()
        Check if this FTX run is currently running
    is_queueing()
        Check if this FTX run is currently queueing
    has_started
        Check if this FTX run has started
    has_finished
        Check if this FTX run has finished
    has_exceeded_the_time_limit
        Check if this FTX run has been killed because it exceeded the specified time limit
    has_failed
        Check if this FTX run has failed because of another error
    """
    
    def __init__(self, work_dir:str, inputs:FTXInput, batchscript:Batchscript):
        """
        Constructs all the necessary attributes for the FTXRun object

        Parameters
        ----------
            work_dir : str
                The name of the work directory where this FTX run wil be running
            inputs : FTXInput
                The FTX input files to use
            batchscript : Batchscript
                The batchscript associated with this FTX run
        """
        self.work_dir = work_dir
        self.inputs = inputs
        self.batchscript = batchscript
        self._job_id = None
        self.change_work_dir(self.work_dir) # also update SIM_ROOT in IPS config file!

    def get_work_dir(self)->str:
        """Returns the work dir of this FTX run"""
        return self.work_dir
    
    def change_work_dir(self, work_dir:str)->None:
        """Change the work directory for this FTX run to the given work directory"""
        self.work_dir = work_dir
        self.inputs.parameters["SIM_ROOT"] = FTXParameter(name="SIM_ROOT", value=work_dir)

    def write_files(self, overwrite:bool=False)->None:
        """Write the files for this FTX run"""
        if os.path.isdir(self.work_dir):
            if not overwrite and len(os.listdir(self.work_dir)) > 1:
                print(f"Work directory {self.work_dir} exists and is not empty")
                raise ValueError("FTXPy -> FTXRun -> write_inputs() : Work directory exists and is not empty")
        else:
            os.makedirs(self.work_dir)
        self.inputs.write_files(self.work_dir)

    def clean(self):
        """Clean this run directory"""
        with working_directory(self.work_dir):
            clean_sh = "clean.sh"
            if not os.path.isfile(clean_sh):
                print(f"File {clean_sh} does not exist")
                raise ValueError("FTXPy -> FTXRun -> clean() : File does not exist")
            os.system("chmod u+x " + clean_sh)
            os.system("./" + clean_sh)

    def get_log_file(self):
        """Returns the content of the log.ftx file of this run"""
        with working_directory(self.work_dir):
            log_ftx = "log.ftx"
            if not os.path.isfile(log_ftx):
                print(f"File {log_ftx} does not exist")
                raise ValueError("FTXPy -> FTXRun -> get_log_file() : File does not exist")
            with open(log_ftx, "r") as f:
                return f.readlines()

    def start(self)->None:
        """Start this FTX run"""
        with working_directory(self.work_dir):
            self.batchscript.update_commands(config_files="ips.ftx.config", log_file="log.framework", platform_file="conf.ips", stdout_file="log.stdOut", stderr_file="log.stdErr")
            self._job_id = self.batchscript.submit()

    def is_running(self)->bool:
        """Check if this FTX run is currently running"""
        cmd = f"squeue --job {self._job_id}"
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        return result.stdout.decode().split()[-4] == "R"

    def is_queueing(self)->bool:
        """Check if this FTX run is currently queueing"""
        cmd = f"squeue --job {self._job_id}"
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        return result.stdout.decode().split()[-4] == "PD"

    def has_started(self)->bool:
        """Check if this FTX run has started"""
        return self._job_id is not None

    def has_finished(self)->bool:
        """Check if this FTX run has finished"""
        with working_directory(self.work_dir):
            log_ftx_file = "log.ftx"
            if not os.path.isfile(log_ftx_file):
                return False
            return occursin_file("FT-X driver:finalize called", log_ftx_file)

    def has_errored(self)->bool:
        """Check if this FTX run has errored"""
        with working_directory(self.work_dir):
            log_warning_file = "log.warning"
            if not os.path.isfile(log_warning_file):
                return True
            return occursin_file("ERROR", log_warning_file)

    def has_exceeded_the_time_limit(self)->bool:
        """Check if this FTX run has been killed because it exceeded the specified time limit"""
        with working_directory(self.work_dir):
            log_slurm_stdOut_file = self.batchscript.slurm_settings["output"]
            if not os.path.isfile(log_slurm_stdOut_file):
                return False
            return occursin_file("DUE TO TIME LIMIT", log_slurm_stdOut_file)

    def has_failed(self)->bool:
        """Check if this FTX run has failed because of another error"""
        return self.has_started() and not self.has_finished() and not self.has_errored() and not self.has_exceeded_the_time_limit() and not self.is_queueing() and not self.is_running()
