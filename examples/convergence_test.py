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
    return range(10)

# ===================================================================
def network_sizes():
    return [50, 100, 150, 200, 250]

# ===================================================================
def get_root_dir():
    return os.path.join(os.environ["CSCRATCH"], "ftxpy", "convergence_test")

# ===================================================================
def get_name(network_size, seed):
    return f"network_size_{network_size}_seed_{seed}"

# ===================================================================
def get_work_dir(network_size, seed):
    return os.path.join(get_root_dir(), get_name(network_size, seed))

# ===================================================================
class DummyBatchScript():

    def __init__(self, slurm_settings):
        self.slurm_settings = slurm_settings

    def submit(self):
        pass

# ===================================================================
def define():

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
            for param_name in ["SBV_W", "EF_W", "EF_He", "E0_He", "ALPHA0_He", "lattice", "impurityRadius", "biasFactor", "initialV", "voidPortion", "He1", "He2", "He3", "He4", "He5", "He6", "He7", "V1"]:
                parameters[param_name].set_random_value()

            # define inputs
            source = os.path.expandvars(config["input"]["source"])
            inputs = ftxpy.FTXInput(parameters=parameters, source=source)

            # define batchscript
            slurm_settings = config["batchscript"]["slurm_settings"]
            batchscript = DummyBatchScript(slurm_settings)

            # set up a work directory
            work_dir = get_work_dir(network_size, seed)
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
    for network_size in network_sizes():
        for seed in seeds():
            simulation_file = os.path.join(get_work_dir(network_size, seed), "simulation.pk")
            if os.path.isfile(simulation_file):
                simulation = ftxpy.FTXSimulation.load(simulation_file)
                simulation.step()
                simulations[network_size, seed] = simulation
            else:
                print(f"Simulation file '{simulation_file}' not found!")

    # actually run the jobs
    config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile=profile())
    slurm_settings = config["batchscript"]["slurm_settings"]
    nb_not_finished = sum([not simulation.has_finished() for simulation in simulations.values()])
    if nb_not_finished > 0:
        slurm_settings["min_nodes"] = 2*nb_not_finished
        commands = config["batchscript"]["commands"][:-1]
        configs = []
        for network_size in network_sizes():
            for seed in seeds():
                if not simulations[network_size, seed].has_finished():
                    configs.append(f"{simulations[network_size, seed].current_run.work_dir}/ips.ftx.config")
        ips_command = "ips.py --config=" + ",".join(configs) + " --platform=$CFS/atom/users/pieterja/ips-examples/iterative-xolotlFT-UQ/conf.ips.cori --log=log.framework 2>>log.stdErr 1>>log.stdOut"
        commands.append(ips_command)
        batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)
        with ftxpy.working_directory(get_root_dir()):
            job_id = batchscript.submit()
        for network_size in network_sizes():
            for seed in seeds():
                if not simulations[network_size, seed].has_finished():
                    simulations[network_size, seed].current_run._job_id = job_id
                    simulations[network_size, seed].save(overwrite=True)
        
# ===================================================================
def status():
    for network_size in network_sizes():
        for seed in seeds():
            simulation_file = os.path.join(get_work_dir(network_size, seed), "simulation.pk")
            if os.path.isfile(simulation_file):
                simulation = ftxpy.FTXSimulation.load(simulation_file)
                simulation.print_status()
            else:
                print(f"Simulation file '{simulation_file}' not found!")

# ===================================================================
def remove():
    for network_size in network_sizes():
        for seed in seeds():
            shutil.rmtree(get_work_dir(network_size, seed), ignore_errors=True)

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
