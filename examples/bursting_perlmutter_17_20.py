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
def depths():
    return range(17, 21)

# ===================================================================
def factors():
    return range(2,10)

# ===================================================================
def get_root_dir():
    return os.path.join(os.environ["PSCRATCH"], "ftxpy", "bursting_17_20")

# ===================================================================
def get_name(depth, factor):
    return f"depth_{depth}_factor_{factor}"

# ===================================================================
def get_work_dir(depth, factor):
    return os.path.join(get_root_dir(), get_name(depth, factor))

# ===================================================================
def load_group():
    return ftxpy.FTXGroup.load(os.path.join(get_root_dir(), "simulation_group.pk"))

# ===================================================================
def define():

    # list of simulations
    simulations = list()

    for depth in depths():
        for factor in factors():

            # load configuration file
            config = ftxpy.utils.parse(ftxpy._ftxpy_config_perlmutter_, case="PISCES", profile=profile())

            # define parameters
            parameters = config["input"]["parameters"]
            
            # update parameters
            parameters["SIM_NAME"].set_value(get_name(depth, factor))
            parameters["netParam"].set_value(f"8 0 0 100 6 false")
            parameters["END_TIME"].set_value(3.15)
            parameters["burstingDepth"].set_value(depth)
            parameters["burstingFactor"].set_value(10**factor)

            # define inputs
            source = os.path.expandvars(config["input"]["source"])
            inputs = ftxpy.FTXInput(parameters=parameters, source=source)

            # define batchscript
            slurm_settings = config["batchscript"]["slurm_settings"]
            commands = config["batchscript"]["commands"]
            batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
            # print(slurm_settings)
            # print(commands)

            # set up a work directory
            work_dir = get_work_dir(depth, factor)
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
    group = load_group()
    for nb in [31, 78, 83]:
        group.simulations[nb].current_run.batchscript = ftxpy.DummyBatchscript()
    group.save(overwrite=True)
    
    # group = load_group()
    # simulations = {}
    # for nb, simulation in enumerate(group.simulations):
    #     for param_name, step in zip(["E0_He", "biasFactor", "initialV"], [1, 8, 3]):
    #         name = get_name(param_name, step)
    #         if name in simulation._name:
    #             print(f"simulation {name} has index {nb}")# load configuration file
    #             config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile=profile())

    #             # define parameters
    #             parameters = config["input"]["parameters"]
                
    #             # update parameters
    #             parameters["SIM_NAME"].set_value(get_name(param_name, step))
    #             parameters["netParam"].set_value(f"8 0 0 100 6 false")
    #             a = parameters[param_name].lower
    #             b = parameters[param_name].upper
    #             if parameters[param_name].log10_transform:
    #                 a = np.log10(a)
    #                 b = np.log10(b)
    #             value = (step / (len(steps()) - 1)) * (b - a) + a
    #             if parameters[param_name].log10_transform:
    #                 value = 10**value
    #             parameters[param_name].set_value(value)

    #             # define inputs
    #             source = os.path.expandvars(config["input"]["source"])
    #             inputs = ftxpy.FTXInput(parameters=parameters, source=source)

    #             # define batchscript
    #             slurm_settings = config["batchscript"]["slurm_settings"]
    #             commands = config["batchscript"]["commands"]
    #             batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

    #             # set up a work directory
    #             work_dir = get_work_dir(param_name, step)
    #             shutil.rmtree(work_dir, ignore_errors=True)
    #             os.makedirs(work_dir)

    #             # set up an ftx run
    #             run = ftxpy.FTXRun(work_dir, inputs, batchscript)

    #             # set up an ftx simulation
    #             simulation = ftxpy.FTXSimulation(run)

    #             simulations[nb] = simulation

    # for nb, simulation in simulations.items():
    #     group.simulations[nb] = simulation

    # group.save(overwrite=True)

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
