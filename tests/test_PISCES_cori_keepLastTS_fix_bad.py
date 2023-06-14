import ftxpy
import os
import shutil

# load configuration file
config = ftxpy.utils.parse(ftxpy._ftxpy_config_cori_, case="PISCES", profile="debug")

# define inputs
parameters = config["input"]["parameters"]
source = os.path.expandvars(config["input"]["source"])
inputs = ftxpy.FTXInput(parameters=parameters, source=source)

# define batchscript
slurm_settings = config["batchscript"]["slurm_settings"]
commands = config["batchscript"]["commands"]
batchscript = ftxpy.Batchscript(slurm_settings=slurm_settings, commands=commands)

# set up a work directory
work_dir = os.path.join(os.environ["CSCRATCH"], "ftxpy", "test_PISCES_cori_keepLastTS_fix_bad")
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