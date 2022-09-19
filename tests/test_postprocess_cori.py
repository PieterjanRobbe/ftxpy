import ftxpy
import os
import shutil

# get the PISCES simulation
work_dir = os.path.join(os.environ["CSCRATCH"], "ftxpy_test_PISCES")
simulation = ftxpy.FTXSimulation.load(os.path.join(work_dir, "simulation.pk"))

# create FTX output
output = ftxpy.FTXOutput(simulation)

# load surface growth, He content and He retention output
output.load_surface()
output.load_content()
output.load_retention()

# save outputs to file
output.save(overwrite=True)

# plot outputs
# output.plot_surface()
# output.plot_content()
# output.plot_retention()