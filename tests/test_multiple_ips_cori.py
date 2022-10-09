# import statements
import argparse
import ftxpy
import numpy as np
import os
import shutil
import sys

# ===================================================================
class DummyBatchScript():

    def __init__(self, slurm_settings):
        self.slurm_settings = slurm_settings

    def submit(self):
        pass

# ===================================================================
# test two different seeds
simulations = list()
root_dir = os.path.join(os.environ["CSCRATCH"], "ftxpy", "test_multiple_ips_cori")
for seed in [0, 1]:

    # set seed
    np.random.seed(2022 + seed)

    # load configuration file
    config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile="debug")

    # define parameters
    parameters = config["input"]["parameters"]
    
    # update parameters
    parameters["SIM_NAME"].set_value(f"seed_{seed}")
    for param_name in ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "voidPortion", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]:
        parameters[param_name].set_random_value()

    # define inputs
    source = os.path.expandvars(config["input"]["source"])
    inputs = ftxpy.FTXInput(parameters=parameters, source=source)

    # define batchscript
    slurm_settings = config["batchscript"]["slurm_settings"]
    batchscript = DummyBatchScript(slurm_settings)

    # set up a work directory
    work_dir = os.path.join(root_dir, f"seed_{seed}")
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir)

    # set up an ftx run
    run = ftxpy.FTXRun(work_dir, inputs, batchscript)

    # set up an ftx simulation
    simulation = ftxpy.FTXSimulation(run)
    simulation.start() # run as usual with dummy batchscript
    simulations.append(simulation)

# actually run the jobs
config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile="debug")
slurm_settings = config["batchscript"]["slurm_settings"]
slurm_settings["min_nodes"] = 4
commands = config["batchscript"]["commands"][:-1]
configs = [f"{simulation.current_run.work_dir}/ips.ftx.config" for simulation in simulations]
ips_command = "ips.py --config=" + ",".join(configs) + " --platform=$CFS/atom/users/$USER/ips-examples/iterative-xolotlFT-UQ/conf.ips.cori --log=log.framework 2>>log.stdErr 1>>log.stdOut"
commands.append(ips_command)
batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
with ftxpy.working_directory(root_dir):
    job_id = batchscript.submit()
for simulation in simulations:
    simulation.current_run._job_id = job_id
    simulation.save()