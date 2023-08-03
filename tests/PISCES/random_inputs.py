import ftxpy
import os
import shutil

# load configuration file
config = ftxpy.utils.parse(ftxpy._ftxpy_config_perlmutter_, case="PISCES", profile="debug")

# define parameters of the simulation
parameters = config["input"]["parameters"]
parameters["SIM_NAME"].set_value(f"Test PISCES with random inputs")
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
work_dir = os.path.join(os.environ["PSCRATCH"], "ftxpy", "tests", "PISCES", "random_inputs")
shutil.rmtree(work_dir, ignore_errors=True)
os.makedirs(work_dir)

# set up an ftx run
run = ftxpy.FTXRun(work_dir, inputs, batchscript)

# set up an ftx simulation
simulation = ftxpy.FTXSimulation(run)

# start the simulation
simulation.start()

# save the simulation
simulation.save()