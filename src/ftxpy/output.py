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
        self.sputtering_yields = None
        self.last_TRIDYN = None

    def load_surface(self):
        runs = self.ftx_simulation.get_runs()
        surface_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "surface.txt")) for run in runs] for file in file_list]
        surfaces = [np.loadtxt(surface_file).reshape(-1, 2) for surface_file in surface_files if os.path.isfile(surface_file) and os.path.getsize(surface_file)]
        allSurface_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allSurface.txt")) for run in runs] for file in file_list]
        allSurfaces = [np.loadtxt(allSurface_file) for allSurface_file in allSurface_files if os.path.isfile(allSurface_file) and os.path.getsize(allSurface_file)]
        if len(surfaces) == 0 and len(allSurfaces) == 0:
            print(f"WARNING: no surface files found for {self.ftx_simulation._name}")
            self.surface = ([0], [0])
        else:
            surface = np.unique(np.vstack(surfaces + allSurfaces), axis=0)
            # surface = np.vstack(surfaces + allSurfaces)
            surface[:, 1] -= surface[0, 1] # subtract baseline
            self.surface = (surface[:, 0], surface[:, 1])

    def load_retention(self):
        runs = self.ftx_simulation.get_runs()
        retentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "retentionOut.txt")) for run in runs] for file in file_list]
        retentionOuts = [np.loadtxt(retentionOut_file, usecols=(0, 1, 2, 5)) for retentionOut_file in retentionOut_files if os.path.isfile(retentionOut_file) and os.path.getsize(retentionOut_file)]
        allRetentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allRetentionOut.txt")) for run in runs] for file in file_list]
        allRetentionOuts = [np.loadtxt(allRetentionOut_file, usecols=(0, 1, 2, 5)) for allRetentionOut_file in allRetentionOut_files if os.path.isfile(allRetentionOut_file) and os.path.getsize(allRetentionOut_file)]
        if len(retentionOuts) == 0 and len(allRetentionOuts) == 0:
            print(f"WARNING: no He retention files found for {self.ftx_simulation._name}")
            self.retention = ([0], [0])
        else:
            retention = np.unique(np.vstack(retentionOuts + allRetentionOuts), axis=0)
            # retention = np.vstack(retentionOuts + allRetentionOuts)
            # self.retention = (retention[1:, 0], 100*(retention[1:, 2] + retention[1:, 5]) / (retention[1:, 1])) # * self.get_sticking_coeff())) # 100*(He content + He bulk ) / (fluence * He sticking coeff)
            self.retention = (retention[1:, 0], 100*(retention[1:, 2] + retention[1:, 3]) / (retention[1:, 1] * self.get_sticking_coeff())) # 100*(He content + He bulk ) / (fluence * He sticking coeff)

    def load_content(self):
        runs = self.ftx_simulation.get_runs()
        retentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "retentionOut.txt")) for run in runs] for file in file_list]
        retentionOuts = [np.loadtxt(retentionOut_file, usecols=(0, 2)) for retentionOut_file in retentionOut_files if os.path.isfile(retentionOut_file) and os.path.getsize(retentionOut_file)]
        allRetentionOut_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "allRetentionOut.txt")) for run in runs] for file in file_list]
        allRetentionOuts = [np.loadtxt(allRetentionOut_file, usecols=(0, 2)) for allRetentionOut_file in allRetentionOut_files if os.path.isfile(allRetentionOut_file) and os.path.getsize(allRetentionOut_file)]
        if len(retentionOuts) == 0 and len(allRetentionOuts) == 0:
            print(f"WARNING: no He content files found for {self.ftx_simulation._name}")
            self.content = ([0], [0])
        else:
            retention = np.unique(np.vstack(retentionOuts + allRetentionOuts), axis=0)
            # retention = np.vstack(retentionOuts + allRetentionOuts)
            # self.content = (retention[1:, 0], retention[1:, 2])
            self.content = (retention[1:, 0], retention[1:, 1])

    def load_sputtering_yields(self):
        runs = self.ftx_simulation.get_runs()
        param_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "workers__xolotlWorker_*", "params_*.txt")) for run in runs] for file in file_list]
        t = []
        sputtering_yields = []
        for param_file in param_files:
            t.append(float(param_file.split("_")[-1][:-4]))
            with open(param_file, "r") as io:
                lines = io.readlines()
                for line in lines:
                    if "sputtering=" in line:
                        sputtering_yields.append(float(line.split("=")[-1]))
                        break
        t = np.array(t)
        sputtering_yields = np.array(sputtering_yields)
        t, idcs = np.unique(t, return_index=True)
        sputtering_yields = sputtering_yields[idcs]
        self.sputtering_yields = (t, sputtering_yields)

    def load_last_TRIDYN(self):
        runs = self.ftx_simulation.get_runs()
        last_TRIDYN_files = [file for file_list in [glob.glob(os.path.join(run.get_work_dir(), "work", "driver__xolotlFtridynDriver_*", "last_TRIDYN_*.dat")) for run in runs] for file in file_list]
        t = []
        last_TRIDYN = []
        for last_TRIDYN_file in last_TRIDYN_files:
            t.append(float(last_TRIDYN_file.split("_")[-1][:-4]))
            last_TRIDYN.append(np.loadtxt(last_TRIDYN_file))
        t = np.array(t)
        t, idcs = np.unique(t, return_index=True)
        last_TRIDYN = [last_TRIDYN[idx] for idx in idcs]
        self.last_TRIDYN = (t, last_TRIDYN)

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

    def get_sputtering_yields(self):
        """Get sputtering yieds to plot"""
        if self.sputtering_yields is None:
            print("No sputtering yields found, execute 'load_sputtering_yields()' first")
            raise ValueError("FTXPy -> FTXOutput -> get_sputtering_yields(): No sputtering yields found, execute 'load_sputtering_yields()' first")
        return self.sputtering_yields

    def get_last_TRIDYN(self):
        """Get he bins"""
        if self.last_TRIDYN is None:
            print("No TRIDYN data found, execute 'load_last_TRIDYN()' first")
            raise ValueError("FTXPy -> FTXOutput -> get_heBin(): No TRIDYN data found, execute 'load_last_TRIDYN()' first")
        return self.last_TRIDYN

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