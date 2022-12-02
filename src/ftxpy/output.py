# import statements
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

# special imports
from .simulation import FTXSimulation
from .utils import save, load

class FTXOutput():

    def __init__(self, ftx_simulation:FTXSimulation):
        self.ftx_simulation = ftx_simulation
        self.surface = None
        self.retention = None
        self.content = None

    def load_surface(self):
        runs = self.ftx_simulation.get_runs()
        surface_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "surface.txt")) for run in runs] for file in file_list]
        surfaces = [np.loadtxt(surface_file).reshape(-1, 2) for surface_file in surface_files if os.path.isfile(surface_file) and os.path.getsize(surface_file)]
        allSurface_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allSurface.txt")) for run in runs] for file in file_list]
        allSurfaces = [np.loadtxt(allSurface_file) for allSurface_file in allSurface_files if os.path.isfile(allSurface_file) and os.path.getsize(allSurface_file)]
        surface = np.unique(np.vstack(surfaces + allSurfaces), axis=0)
        surface[:, 1] -= surface[0, 1] # subtract baseline
        self.surface = (surface[:, 0], surface[:, 1])

    def load_retention(self):
        runs = self.ftx_simulation.get_runs()
        retentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "retentionOut.txt")) for run in runs] for file in file_list]
        retentionOuts = [np.loadtxt(retentionOut_file) for retentionOut_file in retentionOut_files if os.path.isfile(retentionOut_file) and os.path.getsize(retentionOut_file)]
        allRetentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allRetentionOut.txt")) for run in runs] for file in file_list]
        allRetentionOuts = [np.loadtxt(allRetentionOut_file) for allRetentionOut_file in allRetentionOut_files if os.path.isfile(allRetentionOut_file) and os.path.getsize(allRetentionOut_file)]
        retention = np.unique(np.vstack(retentionOuts + allRetentionOuts), axis=0)
        self.retention = (retention[1:, 0], 100*(retention[1:, 2] + retention[1:, 5]) / (retention[1:, 1] * self.get_sticking_coeff())) # 100*(He content + He bulk ) / (fluence * He sticking coeff)

    def load_content(self):
        runs = self.ftx_simulation.get_runs()
        retentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "retentionOut.txt")) for run in runs] for file in file_list]
        retentionOuts = [np.loadtxt(retentionOut_file) for retentionOut_file in retentionOut_files if os.path.isfile(retentionOut_file) and os.path.getsize(retentionOut_file)]
        allRetentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allRetentionOut.txt")) for run in runs] for file in file_list]
        allRetentionOuts = [np.loadtxt(allRetentionOut_file) for allRetentionOut_file in allRetentionOut_files if os.path.isfile(allRetentionOut_file) and os.path.getsize(allRetentionOut_file)]
        retention = np.unique(np.vstack(retentionOuts + allRetentionOuts), axis=0)
        self.content = (retention[1:, 0], retention[1:, 2])

    def get_surface(self):
        """Get surface growth data to plot"""
        if self.surface is None:
            print("No surface data found, execute 'load_surface()' first")
            raise ValueError("FTXPy -> FTXOutput -> get_surface() : No surface data found, execute 'load_surface()' first")
        return self.surface

    def get_retention(self):
        """Get He retention data to plot"""
        if self.retention is None:
            print("No retention data found, execute 'load_retention()' first")
            raise ValueError("FTXPy -> FTXOutput -> get_retention() : No retention data found, execute 'load_retention()' first")
        return self.retention

    def get_content(self):
        """Get He content data to plot"""
        if self.retention is None:
            print("No content data found, execute 'load_content()' first")
            raise ValueError("FTXPy -> FTXOutput -> get_content() : No content data found, execute 'load_content()' first")
        return self.content

    def get_sticking_coeff(self):
        runs = self.ftx_simulation.get_runs()
        tridyn_dat_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "tridyn.dat")) for run in runs] for file in file_list]
        tridyn_exists = [os.path.isfile(tridyn_dat_file) for tridyn_dat_file in tridyn_dat_files]
        tridyn_ics = [i for i, tridyn_exist in enumerate(tridyn_exists) if tridyn_exist]
        if len(tridyn_ics) == 0:
            print(f"No tridyn.dat file(s) found!")
            raise ValueError("FTXPy -> FTXOutput -> get_sticking_coeff() : No tridyn.dat file(s) found!")
        with open(tridyn_dat_files[tridyn_ics[-1]], "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("He"):
                    return float(line.split()[-1])

    def plot_surface(self, t_end=None, figsize=(8, 5), kwargs={"linewidth": .75}, ax=None)->None:
        """Plot surface growth"""
        t, x = self.get_surface()
        if not t_end is None:
            t = np.append(t, t_end)
            x = np.append(x, x[-1])
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)
            ax.set_xlabel("time [s]")
            ax.set_ylabel("surface growth [nm]")
        ax.step(t, x, where="post", **kwargs)
        return ax

    def plot_retention(self, figsize=(8, 5), kwargs={"linewidth": .75}, ax=None)->None:
        """Plot He retention"""
        t, x = self.get_retention()
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)
            ax.set_xlabel("time [s]")
            ax.set_ylabel("He retention [%]")
        ax.plot(t, x, **kwargs)
        return ax

    def plot_content(self, figsize=(8, 5), kwargs={"linewidth": .75}, ax=None)->None:
        """Plot He content"""
        t, x = self.get_content()
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)
            ax.set_xlabel("time [s]")
            ax.set_ylabel("He content [?]")
        ax.plot(t, x, **kwargs)
        return ax

    def save(self, overwrite:bool=False)->None:
        """Save this FTX output"""
        file_name =  os.path.join(self.ftx_simulation._path, "output.pk")
        if overwrite and os.path.isfile(file_name):
            os.remove(file_name)
        if os.path.isfile(file_name):
            print(f"File {file_name} already exists, use 'overwrite=True' to overwrite the output file")
            raise ValueError("FTXPy -> FTXOutput -> save() : File already exists, use 'overwrite=True' to overwrite the output file")
        save(self, file_name)

    def load(file_name:str):
        """Load an FTX output from file"""
        if not os.path.isfile(file_name):
            print(f"File {file_name} does not exist")
            raise ValueError("FTXPy -> FTXOutput -> load() : File does not exist")
        return load(file_name)