# import statements
import os
import pyslurm
import shlex
import subprocess

# class that represents a batchscript
class Batchscript():
    """
    A class to represent a batchscript

    Methods
    -------
    submit():
        Submit this batchscript to the slurm scheduler
    """

    def __init__(self, slurm_settings:dict, commands:list):
        """
        Constructs all the necessary attributes for the Batchscript object

        Parameters
        ----------
            slurm_settings : dict
                An optional dict of slurm settings
            commands : list
                An optional list of commands to ru
        """
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

# class that represents a dummy batchscript
class DummyBatchscript():

    def __init__(self):
        """
        A class to represent a dummy batchscript
        """
        self.slurm_settings = dict()

    def submit(self):
        pass