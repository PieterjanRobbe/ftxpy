# import statements
import os
import pickle as pk

# special imports
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
	with open(file_name, "r") as f:
		for line in f:
			if string in line:
				return True
	return False

# function to save an object to a pickle file
def save(object, file_name):
    with open(file_name, "wb") as f:
        pk.dump(object, f)

# function to load an object from a pickle file
def load(file_name):
    with open(file_name, "rb") as f:
        return pk.load(f)

# return line number in file that corresponds to the last line containing a given search string
def get_last_occurance(file_contents:list, search_str:str)->int:
    lines = [line_nb for line_nb, line in enumerate(file_contents) if search_str in line]
    if len(lines) == 0:
        return -1
    return max(lines)