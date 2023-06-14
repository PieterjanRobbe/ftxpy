# import statements
import argparse
import ftxpy
import numpy as np
import os
import shutil
import sys

# ===================================================================
def profile():
    return "production"

# ===================================================================
def seeds():
    return [0]

# ===================================================================
def network_sizes():
    return [50]

# ===================================================================
def get_root_dir():
    return os.path.join(os.environ["CSCRATCH"], "ftxpy", "convergence_test_low_burst_start_stop_5")

# ===================================================================
def get_name(network_size, seed):
    return f"network_size_{network_size}_seed_{seed}"

# ===================================================================
def get_work_dir(network_size, seed):
    return os.path.join(get_root_dir(), get_name(network_size, seed))

# ===================================================================
def define():

    # list of simulations
    simulations = list()

    for network_size in network_sizes():
        for seed in seeds():

            # set seed
            np.random.seed(2022 + seed)

            # load configuration file
            config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile=profile())

            # define parameters
            parameters = config["input"]["parameters"]
            
            # update parameters
            parameters["SIM_NAME"].set_value(get_name(network_size, seed))
            parameters["nImpacts"].set_value(1000)
            parameters["netParam"].set_value(f"8 0 0 {network_size} 6 false")
            parameters["burstingFactor"].set_value(2e3)
            # parameters["END_TIME"].set_value(5)
            # parameters["LOOP_TIME_STEP"].set_value(0.05)
            # parameters["start_stop"].set_value(0.005)
            for param_name in ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]:
                parameters[param_name].set_random_value()
        
            # define inputs
            source = os.path.expandvars(config["input"]["source"])
            inputs = ftxpy.FTXInput(parameters=parameters, source=source)

            # define batchscript
            slurm_settings = config["batchscript"]["slurm_settings"]
            commands = config["batchscript"]["commands"]
            batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

            # set up a work directory
            work_dir = get_work_dir(network_size, seed)
            shutil.rmtree(work_dir, ignore_errors=True)
            os.makedirs(work_dir)

            # set up an ftx run
            run = ftxpy.FTXRun(work_dir, inputs, batchscript)

            # set up an ftx simulation
            simulation = ftxpy.FTXSimulation(run)
            simulations.append(simulation)

    # create a simulation group
    group = ftxpy.FTXGroup(get_root_dir(), simulations)

    # save the simulation group
    group.save(overwrite=True)

# ===================================================================
def start():
    group = ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))
    group.start()
    group.save(overwrite=True)

# ===================================================================
def step():
    group = ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))
    group.step()
    group.save(overwrite=True)

# ===================================================================
def print_status():
    group = ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))
    group.print_status()

# ===================================================================
def postprocess():
    group = ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))
    group.postprocess()

# ===================================================================
def delete_failed_restarts():
    group = ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))
    group.save(overwrite=True)

# ===================================================================
def main():

    # add argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    args = parser.parse_args()

    # parse action
    try:
        action = eval(args.action)
    except:
        raise ValueError(f"could not parse action '{args.action}'")

    # perform action
    action()

# ===================================================================
if __name__ == "__main__":
    main()
