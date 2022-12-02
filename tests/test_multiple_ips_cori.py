# import statements
import argparse
import ftxpy
import numpy as np
import os
import shutil

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
    commands = config["batchscript"]["commands"]
    batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

    # set up a work directory
    work_dir = os.path.join(root_dir, f"seed_{seed}")
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir)

    # set up an ftx run
    run = ftxpy.FTXRun(work_dir, inputs, batchscript)

    # set up an ftx simulation
    simulation = ftxpy.FTXSimulation(run)
    simulations.append(simulation)

# create a simulation group
group = ftxpy.FTXGroup(root_dir, simulations)

# start the simulation group
group.start()

# save the simulation group
group.save(overwrite=True)