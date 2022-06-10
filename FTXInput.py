# import statements
import os

# special imports
from pyFTX.defaults import get_default_parameters
from pyFTX.utils import working_directory

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

    def __init__(self, parameters:dict=get_default_parameters(), source:str=None, input_files:list=list()):
        """
        Constructs all the necessary attributes for the FTXInput object

        Parameters
        ----------
            parameters : dict (keyword argument)
                A dict with parameter names as key and FTX parameters as values
            source : str (keyword argument)
                A source directory where to load files from
            input_files : list (keyword argument)
                A list of input files
        """
        self.parameters = parameters # dict with parameters
        self.input_files = input_files # list with input files
        if not source is None:
            self.get_input_files_from_source(source) # add files from source directory
        self._files = {} # dict with file names and file contents
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
        with working_directory(src):
            for file in os.listdir():
                self.input_files.append(os.path.join(src, file))

    def stage_input_files(self)->None:
        """Stages the input files"""
        for file in self.input_files:
            file_name = os.path.basename(file)
            if not os.path.isfile(file):
                print(f"Requested input file {file} does not exist")
                raise ValueError("FTXPy -> FTXInput -> stage_input_files(src) : Requested input file does not exist")
            with open(file, "r") as f:
                file_contents = f.readlines()
            self._files[file_name] = file_contents

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
            for file_name, file_contents in self._files.items():
                lines = file_contents.copy()
                for param_name, param_value in self.parameters.items():
                    for line_nb, line in enumerate(lines):
                        lines[line_nb] = line.replace("{" + param_name + "}", str(param_value.get_value()))
                with open(file_name, "w") as f:
                    f.writelines(lines)