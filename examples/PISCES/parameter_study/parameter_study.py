# import statements
import argparse
import ftxpy
import os
import shutil

# ===================================================================
# setup
profile = "production" # simulation profile
nb_of_steps = 5 # number of different values of each parameter to test
parameters_to_vary = ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "voidPortion", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"] # list of parameters to vary
root_dir = os.path.join(os.environ["SCRATCH"], "ftxpy", "examples", "PISCES", "parameter_study")

# ===================================================================
# setup the simulations in the parameter study
def setup():

    # list of simulations
    simulations = list()

    for param_name in parameters_to_vary:
        for step in range(nb_of_steps):

            # load configuration file
            config = ftxpy.utils.parse(ftxpy._ftxpy_config_perlmutter_, case="PISCES", profile=profile)

            # define parameters
            parameters = config["input"]["parameters"]
            parameters["SIM_NAME"].set_value(f"{param_name}_{step}")
            parameters["netParam"].set_value(f"8 0 0 100 6 false")
            parameters["END_TIME"].set_value(1)
            parameters[param_name].set_value_from_0_1(step / (nb_of_steps - 1))

            # define inputs
            source = os.path.expandvars(config["input"]["source"])
            inputs = ftxpy.FTXInput(parameters=parameters, source=source)

            # define batchscript
            slurm_settings = config["batchscript"]["slurm_settings"]
            commands = config["batchscript"]["commands"]
            batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

            # set up a work directory
            work_dir = os.path.join(root_dir, f"{param_name}_{step}")
            shutil.rmtree(work_dir, ignore_errors=True)
            os.makedirs(work_dir)

            # set up an ftx run
            run = ftxpy.FTXRun(work_dir, inputs, batchscript)

            # set up an ftx simulation
            simulations.append(ftxpy.FTXSimulation(run))

    # create a simulation group
    group = ftxpy.FTXGroup(root_dir, simulations)

    # save the simulation group
    group.save(overwrite=True)

# ===================================================================
# add actions for this simulation group
def add_action(action, save=False):
    return f"""
def {action}():
    group = ftxpy.FTXGroup.load(os.path.join(root_dir, 'simulation_group.pk'))
    group.{action}()
    {'group.save(overwrite=True)' if save else ''}
    """

exec(add_action("start", save=True))
exec(add_action("step", save=True))
exec(add_action("print_status"))
exec(add_action("postprocess"))

# ===================================================================
# main function
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
# make script runnable
if __name__ == "__main__":
    main()
