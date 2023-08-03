# import statements
import os
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
                An optional list of commands to run
        """
        self.slurm_settings = slurm_settings
        self.commands = commands

        # holds the original templates
        self.slurm_settings_template = slurm_settings
        self.commands_template = commands
        
    def submit(self, batchfile="batchscript.sh")->None:
        """
        Submit this batchscript to the slurm scheduler
        
        Return
        ------
            job_id : int
                The job id for this batch job
        """

        # write batchfile
        with open(batchfile, "w") as io:
            io.write("\n".join(self.header() + self.commands))

        # submit job
        try:
            result = subprocess.run(["sbatch", batchfile], stdout=subprocess.PIPE)
            job_id = result.stdout.decode().split()[-1]
        except:
            print(result.stdout.decode())
            print(f"Error submitting batchscript")
            raise ValueError("FTXPy -> Batchscript -> submit() : Error submitting batchscript")
        return job_id

    def header(self) -> str:
        """
        Get the header of this batchscript file
        
        Return
        ------
            header : str
                The header of this batchscript file
        """
        return ["#!/bin/bash"] + ["#SBATCH --" + setting["flag"] + "=" + str(setting["value"]) for setting in self.slurm_settings]
    
    def update_commands(self, **kwargs):
        for command_nb, command in enumerate(self.commands):
            self.commands[command_nb] = command.format(**kwargs)

    def update_slurm_setting(self, flag, value):
        for setting in self.slurm_settings:
            if setting["flag"] == flag:
                setting["value"] = value

    def reset(self):
        self.commands = self.commands_template
        self.slurm_settings = self.slurm_settings_template

# class that represents a dummy batchscript
class DummyBatchscript():

    def __init__(self):
        """
        A class to represent a dummy batchscript
        """
        self.slurm_settings = dict()

    def submit(self):
        pass

    def update_commands(self, **kwargs):
        pass

    def update_slurm_setting(self, flag, value):
        pass

    def reset(self):
        pass