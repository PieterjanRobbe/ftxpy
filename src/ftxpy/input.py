# import statements
import os
import shutil

# special imports
from .utils import working_directory

# class that represents a collection of FTX input files
class FTXInput():
    """
    A class to represent a collection of FTX input files

    Methods
    -------
    get_input_files_from_source(src):
        Get list of input files from a source directory
    stage_input_files()
        Stages the input files
    write_files(dest)
        Writes the contents of the input files to a destination directory
    """

    def __init__(self, parameters:dict, source:str=None):
        """
        Constructs all the necessary attributes for the FTXInput object

        Parameters
        ----------
            parameters : dict
                A dict with parameter names as key and FTX parameters as values
            source : str (keyword argument)
                A source directory where to load files from
        """
        self.parameters = parameters # dict with parameters
        self.input_files = self.get_input_files_from_source(source) # add files from source directory
        self._files = dict() # dict with file names and file contents
        self._dirs = list() # list of directories
        self.stage_input_files()

    def get_input_files_from_source(self, src:str)->None:
        """
        Get list of input files from a source directory
        
            Parameters:
                src (str): The source directory
        """
        if not os.path.isdir(src):
            print(f"Source directory {src} does not exist")
            raise ValueError("FTXPy -> FTXInput -> get_input_files_from_source(src) : Source directory does not exist")
        input_files = list()
        with working_directory(src):
            for file in os.listdir():
                input_files.append(os.path.join(src, file))
        return input_files

    def stage_input_files(self)->None:
        """Stages the input files"""
        for file in self.input_files:
            if not os.path.exists(file):
                print(f"Requested input file {file} does not exist")
                raise ValueError("FTXPy -> FTXInput -> stage_input_files(src) : Requested input file does not exist")
            if os.path.isdir(file):
                self._dirs.append(file)
            else:
                with open(file, "r") as f:
                    file_contents = f.readlines()
                self._files[os.path.basename(file)] = file_contents

    def write_files(self, dest:str)->None:
        """
        Writes the contents of the input files to a destination directory
        
            Parameters:
                dest (str): The destination directory
        """
        if not os.path.isdir(dest):
            print(f"Destination directory {dest} does not exist")
            raise ValueError("FTXPy -> FTXInput -> write_files(dest) : Destination directory does not exist")
        with working_directory(dest):
            for dir_name in self._dirs:
                shutil.copytree(dir_name, os.path.basename(dir_name), dirs_exist_ok=True)
            for file_name, file_contents in self._files.items():
                lines = file_contents.copy()
                for _ in range(2): # repeat twice to capture self-references in parameters
                    for param_name, param_value in self.parameters.items():
                        for line_nb in range(len(lines)):
                            if "{" + param_name + "}" in lines[line_nb]:
                                lines[line_nb] = lines[line_nb].replace("{" + param_name + "}", str(param_value.get_value()))
                with open(file_name, "w") as f:
                    f.writelines(lines)