# import statements
import os
import pyslurm
import shlex
import subprocess

# special imports
from pyFTX.defaults import get_default_slurm_settings, get_default_ftx_commands

# class that represents a batchscript
class Batchscript():
    """
    A class to represent a batchscript

    Methods
    -------
    submit():
        Submit this batchscript to the slurm scheduler
    """

    def __init__(self, name="batchscript.srun", slurm_settings=get_default_slurm_settings(profile="debug"), commands=get_default_ftx_commands()):
        """
        Constructs all the necessary attributes for the Batchscript object

        Parameters
        ----------
            name : str
                The name of this batchscript
            slurm_settings : dict (keyword argument)
                An optional dict of slurm settings
            commands : list (keyword argument)
                An optional list of commands to run
        """
        self.name = name
        self.slurm_settings = slurm_settings
        self.commands = commands

    def submit(self)->None:
        """
        Submit this batchscript to the slurm scheduler
        
        Return
        ------
            job_id : int
                The job id for this batch job
        """
        job = {key: val for key, val in self.slurm_settings.items()}
        job["wrap"] = "\n".join(self.commands)
        try:
            job_id = pyslurm.job().submit_batch_job(job)
        except:
            print(f"Error submitting batchscript")
            raise ValueError("FTXPy -> Batchscript -> submit() : Error submitting batchscript")
        return job_id