# import statements
import os
import pickle as pk
import toml

# special imports
from .parameter import FTXParameter
from contextlib import contextmanager

# context manager to change the working directory
# from https://gist.github.com/nottrobin/3d675653244f8814838a
@contextmanager
def working_directory(path):
    """Temporarily change the working directory"""
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

# function to check if a given text occurs in a given file
def occursin_file(string, file_name):
    """Check if a given string occurs in a file with given name"""
    with open(file_name, "r") as f:
        for line in f:
            if string in line:
                return True
    return False

# function to save an object to a pickle file
def save(object, file_name):
    """Save a given object as a given file name with pickle"""
    with open(file_name, "wb") as f:
        pk.dump(object, f)

# function to load an object from a pickle file
def load(file_name):
    """Load an object from a given file name with pickle"""
    with open(file_name, "rb") as f:
        return pk.load(f)

# return line number in file that corresponds to the last line containing a given search string
def get_last_occurance(file_contents:list, search_str:str)->int:
    """Return the line number of the line that contains the last occurances of a given search string in a given file"""
    lines = [line_nb for line_nb, line in enumerate(file_contents) if search_str in line]
    if len(lines) == 0:
        return -1
    return max(lines)

# function to parse a toml file into parameters, slurm settings and a list of commands
def parse(config_file:str, case="PISCES", profile="debug"):
    """Parse a configuration file for a given case and profile"""

    # parse toml file
    config = toml.load(config_file)

    # input checking
    # TODO

    # update case-specific parameters
    for k, v in config["input"]["cases"][case]["parameters"].items():
        config["input"]["parameters"][k]["value"] = v
    
    # update profile-specific parameters
    for k, v in config["profiles"][profile]["input"]["parameters"].items():
        config["input"]["parameters"][k]["value"] = v

    # update profile-specific SLURM settings
    for k, v in config["profiles"][profile]["batchscript"]["slurm_settings"].items():
        config["batchscript"]["slurm_settings"][k] = v

    # parse parameters
    parameters = dict()
    for k, v in config["input"]["parameters"].items():
        parameters[k] = FTXParameter(name=k, **v)
    config["input"]["parameters"] = parameters

    return config