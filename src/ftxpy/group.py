# import statements
import os

# special imports
from .simulation import FTXSimulation
from .batchscript import Batchscript, DummyBatchscript
from .output import FTXOutput
from .utils import save, load, working_directory

# class that represents an FTX simulation group
class FTXGroup():
    """
    A class to represent a group of FTX simulations

    Methods
    -------
    step()
        Execute the next step in this group of simulations
    print_status()
        Prints the status of this group of simulations
    save()
        Save this group FTX simulations
    load()
        Load a group of FTX simulations from file
    """

    def __init__(self, work_dir:str, simulations:list):
        """
        Constructs all the necessary attributes for the FTXGroup object

        Parameters
        ----------
            work_dir : str
                The name of the work directory where this group of FTX simulations wil be running
            simulations : list
                The list of simulations that are part of this group of FTX simulations
        """
        self.work_dir = work_dir
        if len(simulations) < 1:
            print(f"A simulation group needs at least one simulation, got {len(simulations)}")
            raise ValueError("FTXPy -> FTXGroup -> __init__() : A simulation group needs at least one simulation")
        self.simulations = simulations
        self.batchscript = simulations[0].current_run.batchscript
        for simulation in simulations:
            simulation.current_run.batchscript = DummyBatchscript()
        self.run_number = -1

    def _step(self, simulations):
        if len(simulations) > 0:
            self.run_number += 1
            self.batchscript.slurm_settings["output"] = f"log.slurm.stdOut.{self.run_number}"
            self.batchscript.slurm_settings["min_nodes"] = 2*len(simulations)
            configs = []
            for simulation in simulations:
                configs.append(f"{simulation.current_run.work_dir}/ips.ftx.config")
            ips_command = "ips.py --config=" + ",".join(configs) + f" --platform=$CFS/atom/users/$USER/ips-examples/iterative-xolotlFT-UQ/conf.ips.cori --log=log.framework.{self.run_number} 2>>log.stdErr.{self.run_number} 1>>log.stdOut.{self.run_number}"
            self.batchscript.commands[-1] = ips_command
            with working_directory(self.work_dir):
                job_id = self.batchscript.submit()
            for simulation in simulations:
                simulation.current_run._job_id = job_id
                simulation.current_run.batchscript.slurm_settings["output"] = os.path.join(self.work_dir, self.batchscript.slurm_settings["output"])

    def start(self):
        """Start this group of simulations"""
        simulations = list()
        for simulation in self.simulations:
            if not simulation.has_started():
                simulation.start()
                simulations.append(simulation)

        # actually run the jobs
        self._step(simulations)

    def step(self):
        """Execute the next step in this group of simulations"""
        simulations = list()
        for simulation in self.simulations:
            if not simulation.has_finished():
                simulation.restart()
                simulations.append(simulation)

        # actually run the jobs
        self._step(simulations)

    def print_status(self):
        """Prints the status of this group of FTX simulations"""
        for simulation in self.simulations:
            simulation.print_status()

    def save(self, overwrite:bool=False)->None:
        """Save this FTX group of simulations"""
        file_name =  os.path.join(self.work_dir, "simulation_group.pk")
        if overwrite and os.path.isfile(file_name):
            os.remove(file_name)
        if os.path.isfile(file_name):
            print(f"File {file_name} already exists, use 'overwrite=True' to overwrite the simulation group file")
            raise ValueError("FTXPy -> FTXGroup -> save() : File already exists, use 'overwrite=True' to overwrite the simulation group file")
        save(self, file_name)

    def postprocess(self):
        for simulation in self.simulations:
            # if simulation.has_finished():
            output = FTXOutput(simulation)
            output.load_surface()
            output.load_retention()
            output.load_content()
            output.save(overwrite=True)

    def load(file_name:str):
        """Load a group of FTX simulations from file"""
        if not os.path.isfile(file_name):
            print(f"File {file_name} does not exist")
            raise ValueError("FTXPy -> FTXGroup -> load() : File does not exist")
        return load(file_name)