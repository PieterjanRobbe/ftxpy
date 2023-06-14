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
def param_names():
    return ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "voidPortion", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]

# ===================================================================
def steps():
    return range(10)

# ===================================================================
def get_root_dir():
    return os.path.join(os.environ["CSCRATCH"], "ftxpy", "parameter_study")

# ===================================================================
def get_name(param_name, step):
    return f"{param_name}_{step}"

# ===================================================================
def get_work_dir(param_name, step):
    return os.path.join(get_root_dir(), get_name(param_name, step))

# ===================================================================
class DummyBatchScript():

    def __init__(self, slurm_settings):
        self.slurm_settings = slurm_settings

    def submit(self):
        pass

# ===================================================================
def define():

    for param_name in param_names():
        for step in steps():

            # set seed
            np.random.seed(19910308)

            # load configuration file
            config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile=profile())

            # define parameters
            parameters = config["input"]["parameters"]
            
            # update parameters
            parameters["SIM_NAME"].set_value(get_name(param_name, step))
            a = parameters[param_name].lower
            b = parameters[param_name].upper
            if parameters[param_name].log10_transform:
                a = np.log10(a)
                b = np.log10(b)
            value = (step / (len(steps()) - 1)) * (b - a) + a
            if parameters[param_name].log10_transform:
                value = 10**value
            parameters[param_name].set_value(value)

            # define inputs
            source = os.path.expandvars(config["input"]["source"])
            inputs = ftxpy.FTXInput(parameters=parameters, source=source)

            # define batchscript
            slurm_settings = config["batchscript"]["slurm_settings"]
            batchscript = DummyBatchScript(slurm_settings)

            # set up a work directory
            work_dir = get_work_dir(param_name, step)
            shutil.rmtree(work_dir, ignore_errors=True)
            os.makedirs(work_dir)

            # set up an ftx run
            run = ftxpy.FTXRun(work_dir, inputs, batchscript)

            # set up an ftx simulation
            simulation = ftxpy.FTXSimulation(run)

            # save simulation
            simulation.save(overwrite=True)

# ===================================================================
def step():
    # run as usual with dummy batchscript
    simulations = {}
    n = 0
    for param_name in param_names():
        for step in steps():
            simulation_file = os.path.join(get_work_dir(param_name, step), "simulation.pk")
            if os.path.isfile(simulation_file):
                simulation = ftxpy.FTXSimulation.load(simulation_file)
                simulation.step()
                simulations[param_name, step] = simulation
                n = max(n, len(simulation._runs) - 1)
            else:
                print(f"Simulation file '{simulation_file}' not found!")

    # actually run the jobs
    config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile=profile())
    slurm_settings = config["batchscript"]["slurm_settings"]
    slurm_settings["output"] = f"log.slurm.stdOut.{n}"
    nb_not_finished = sum([not simulation.has_finished() for simulation in simulations.values()])
    if nb_not_finished > 0:
        slurm_settings["min_nodes"] = 2*nb_not_finished
        commands = config["batchscript"]["commands"][:-1]
        configs = []
        for param_name in param_names():
            for step in steps():
                if not simulations[param_name, step].has_finished():
                    configs.append(f"{simulations[param_name, step].current_run.work_dir}/ips.ftx.config")
        ips_command = "ips.py --config=" + ",".join(configs) + f" --platform=$CFS/atom/users/pieterja/ips-examples/iterative-xolotlFT-UQ/conf.ips.cori --log=log.framework.{n} 2>>log.stdErr.{n} 1>>log.stdOut.{n}"
        commands.append(ips_command)
        batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
        with ftxpy.working_directory(get_root_dir()):
            job_id = batchscript.submit()
        for param_name in param_names():
            for step in steps():
                if not simulations[param_name, step].has_finished():
                    simulations[param_name, step].current_run._job_id = job_id
                    simulations[param_name, step].save(overwrite=True)
        
# ===================================================================
def status():
    for param_name in param_names():
        for step in steps():
            simulation_file = os.path.join(get_work_dir(param_name, step), "simulation.pk")
            if os.path.isfile(simulation_file):
                simulation = ftxpy.FTXSimulation.load(simulation_file)
                simulation.print_status()
            else:
                print(f"Simulation file '{simulation_file}' not found!")

# ===================================================================
def remove():
    for param_name in param_names():
        for step in steps():
            shutil.rmtree(get_work_dir(param_name, step), ignore_errors=True)

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
