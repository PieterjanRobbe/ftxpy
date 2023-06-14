# import statements
import argparse
import ftxpy
import numpy as np
import os
import shutil

# ===================================================================
def profile():
    return "production"

# ===================================================================
def seeds():
    return range(10)

# ===================================================================
def network_sizes():
    return [50, 100, 150, 200, 250]

# ===================================================================
def get_root_dir():
    global burst
    return os.path.join(os.environ["SCRATCH"], "ftxpy", f"convergence_{burst}_burst")

# ===================================================================
def get_name(network_size, seed):
    return f"network_size_{network_size}_seed_{seed}"

# ===================================================================
def get_work_dir(network_size, seed):
    return os.path.join(get_root_dir(), get_name(network_size, seed))

# ===================================================================
def load_group():
    return ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))

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
            parameters["netParam"].set_value(f"8 0 0 {network_size} 6 false")
            for param_name in ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]:
                parameters[param_name].set_random_value()

            # update bursting parameters
            global burst
            if burst == "low":
                parameters["burstingFactor"].set_value(2e3)
        
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
    group = load_group()
    group.start()
    group.save(overwrite=True)

# ===================================================================
def step():
    group = load_group()
    group.step()
    group.save(overwrite=True)

# ===================================================================
def print_status():
    group = load_group()
    group.print_status()

# ===================================================================
def postprocess():
    group = load_group()
    group.postprocess()

# ===================================================================
def delete_failed_restarts():
    group = load_group()
    group.save(overwrite=True)

# ===================================================================
def custom():
    # group = load_group()
    # for nb, simulation in enumerate(group.simulations):
    #     print(nb, simulation._name)
    # group.save(overwrite=True)
    group = load_group()
    simulations = group.simulations
    for nb, simulation in enumerate(simulations):
        if nb == 48:
            simulation._runs = [simulation._runs[0]]
            simulation.current_run = simulation._runs[0]
            group.simulations[nb] = simulation
    for nb, simulation in enumerate(group.simulations):
        print(f"{simulation._name} has {len(simulation._runs)} runs")
    group.save(overwrite=True)

# ===================================================================
def main():

    # add argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("burst")
    parser.add_argument("action")
    args = parser.parse_args()

    # parse bursting factor
    global burst
    burst = args.burst

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
