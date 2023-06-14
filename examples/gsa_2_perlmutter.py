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
def get_root_dir(batch):
    return os.path.join(os.environ["PSCRATCH"], "ftxpy", f"gsa_2_batch_{batch}")

# ===================================================================
def get_name(n):
    return f"sample_{n}"

# ===================================================================
def get_work_dir(batch, n):
    return os.path.join(get_root_dir(batch), get_name(n))

# ===================================================================
def load_group(batch):
    return ftxpy.FTXGroup.load(os.path.join(get_root_dir(batch), "simulation_group.pk"))

# ===================================================================
def param_names():
    return ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]

# ===================================================================
def define(batch):

    # list of simulations
    simulations = list()

    batch_start, batch_end = [int(n) for n in batch.split("_")]

    for n in range(batch_start, batch_end + 1):

        # load configuration file
        config = ftxpy.utils.parse(ftxpy._ftxpy_config_perlmutter_, case="PISCES", profile=profile())

        # define parameters
        parameters = config["input"]["parameters"]

        # get the nth point
        pts = np.loadtxt("d_19_n_2048")
        pt = pts[n - 1, :]
        
        # update parameters
        parameters["SIM_NAME"].set_value(get_name(n))
        parameters["netParam"].set_value(f"8 0 0 100 6 false")
        for d, param_name in enumerate(param_names()):
            a = parameters[param_name].lower
            b = parameters[param_name].upper
            if parameters[param_name].log10_transform:
                a = np.log10(a)
                b = np.log10(b)
            value = pt[d] * (b - a) + a
            if parameters[param_name].log10_transform:
                value = 10**value
            parameters[param_name].set_value(value)
        #
        a = 1
        b = 20
        value = pt[17] * (b - a) + a
        parameters["burstingDepth"].set_value(value)
        #
        a = 6
        b = 9
        value = pt[18] * (b - a) + a
        parameters["burstingFactor"].set_value(10**value)

        # define inputs
        source = os.path.expandvars(config["input"]["source"])
        inputs = ftxpy.FTXInput(parameters=parameters, source=source)

        # define batchscript
        slurm_settings = config["batchscript"]["slurm_settings"]
        slurm_settings["job_name"] = f"gsa_2_{batch}"
        commands = config["batchscript"]["commands"]
        batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
        # print(slurm_settings)
        # print(commands)

        # set up a work directory
        work_dir = get_work_dir(batch, n)
        shutil.rmtree(work_dir, ignore_errors=True)
        os.makedirs(work_dir)

        # set up an ftx run
        run = ftxpy.FTXRun(work_dir, inputs, batchscript)

        # set up an ftx simulation
        simulation = ftxpy.FTXSimulation(run)
        simulations.append(simulation)

    # create a simulation group
    group = ftxpy.FTXGroup(get_root_dir(batch), simulations)

    # save the simulation group
    group.save(overwrite=True)

# ===================================================================
def start(batch):
    group = load_group(batch)
    group.start()
    group.save(overwrite=True)

# ===================================================================
def step(batch):
    group = load_group(batch)
    group.step()
    group.save(overwrite=True)

# ===================================================================
def print_status(batch):
    group = load_group(batch)
    group.print_status()

# ===================================================================
def postprocess(batch):
    group = load_group(batch)
    group.postprocess()

# ===================================================================
def delete_failed_restarts(batch):
    group = load_group(batch)
    group.save(overwrite=True)

# ===================================================================
def main():

    # add argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("batch")
    args = parser.parse_args()

    # parse action
    try:
        action = eval(args.action)
    except:
        raise ValueError(f"could not parse action '{args.action}'")

    # perform action
    action(args.batch)

# ===================================================================
if __name__ == "__main__":
    main()
