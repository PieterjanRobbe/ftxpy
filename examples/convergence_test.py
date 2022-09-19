# import statements
import argparse
import ftxpy
import numpy as np
import os
import shutil
import sys

# ===================================================================
def get_configuration(case="PISCES", profile="production"):
    return ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case=case, profile=profile)

# ===================================================================
def get_work_dir(network_size, seed):
    return os.path.join(os.environ.get("CSCRATCH"), "ftxpy", "convergence_test", f"network_size_{network_size}_seed_{seed}")

# ===================================================================
def get_new_simulation(network_size, seed):

    # set seed
    np.random.seed(2022 + seed)

    # load configuration file
    config = get_configuration()

    # define inputs
    parameters = config["input"]["parameters"]
    source = os.path.expandvars(config["input"]["source"])
    inputs = ftxpy.FTXInput(parameters=parameters, source=source)

    # update parameters
    parameters["netParam"].set_value("8 0 0 {network_size} 6 false")
    for param_name in ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "voidPortion", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]:
        parameters[param_name].set_random_value()

    # load input files
    inputs = ftxpy.FTXInput(parameters=parameters, source=source)

    # get a batchscript
    slurm_settings = config["batchscript"]["slurm_settings"]
    commands = config["batchscript"]["commands"]
    batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

    # set up a work directory
    work_dir = get_work_dir(network_size, seed)
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir)

    # set up an FTX run
    run = ftxpy.FTXRun(work_dir, inputs, batchscript)

    # set up an FTX simulation
    return ftxpy.FTXSimulation(run)

# ===================================================================
def define(simulation):
    pass

# ===================================================================
def status(simulation):
    simulation.print_status()

# ===================================================================
def step(simulation):
    simulation.step()

# ===================================================================
def restart(simulation):
    simulation.restart()

# ===================================================================
def remove_last_restart(simulation):
    if len(simulation._runs) > 1:
        shutil.rmtree(simulation._runs[-1].get_work_dir()) # remove directory
        simulation._runs = simulation._runs[:-1] # remove last run from list
        simulation.current_run = simulation._runs[-1] # update current run

# ===================================================================
def delete_all_runs(simulation):
    simulation.delete_all_runs()

# ===================================================================
def delete_last_run(simulation):
    simulation.delete_last_run()

# ===================================================================
def change_to_debug(simulation):
    config = get_configuration(profile="debug")
    slurm_settings = config["batchscript"]["slurm_settings"]
    commands = config["batchscript"]["commands"]
    simulation.current_run.batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
    
# ===================================================================
def change_to_production(simulation):
    config = get_configuration(profile="production")
    slurm_settings = config["batchscript"]["slurm_settings"]
    commands = config["batchscript"]["commands"]
    simulation.current_run.batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

# ===================================================================
def postprocess(simulation):
    output = ftxpy.FTXOutput(simulation)
    output.load_surface()
    output.load_retention()
    output.load_content()
    output.save(overwrite=True)

# ===================================================================
def copy_pk_files(simulation):
    target_dir = os.path.join("pkfiles", os.path.split(simulation.get_path())[-1])
    os.makedirs(target_dir, exist_ok = True)
    shutil.copyfile(os.path.join(simulation.get_path(), "simulation.pk"), os.path.join(target_dir, "simulation.pk"))
    shutil.copyfile(os.path.join(simulation.get_path(), "output.pk"), os.path.join(target_dir, "simulation.pk"))

# ===================================================================
def parse_range(s):
    rs = []
    for x in s.split(","):
        r = [int(xi) for xi in x.split("-")]
        rs += [r[0]] if len(r) == 1 else list(range(r[0], r[1] + 1))
    return rs

# ===================================================================
def main():

    # add argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--network_sizes", dest="network_sizes", default="50")
    parser.add_argument("--seeds", dest="seeds", default="3")
    args = parser.parse_args()

    # parse actions
    try:
        action = eval(args.action)
    except:
        raise ValueError(f"could not parse action '{args.action}'")

    # parse network sizes
    try:
        network_sizes = parse_range(args.network_sizes)
    except:
        raise ValueError(f"could not parse network_sizes '{args.network_sizes}'")

    # parse seeds
    try:
        seeds = parse_range(args.seeds)
    except:
        raise ValueError(f"could not parse seeds '{args.seeds}'")

    # loop over all combinations
    for network_size in network_sizes:
        for seed in seeds:

            try:

                # print info
                print(f"running {args.action} for network size {network_size} and seed {seed}...")

                # define new simulation or load from file
                if args.action == "define":
                    simulation = get_new_simulation(network_size, seed)
                else:
                    simulation = ftxpy.FTXSimulation.load(os.path.join(get_work_dir(network_size, seed), "simulation.pk"))

                # perform action
                action(simulation)

                # save simulation
                simulation.save(overwrite=True)

            except Exception as exception:

                # print error and continue
                print(exception)

# ===================================================================
if __name__ == "__main__":
    main()
