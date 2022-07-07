# special imports
from pyFTX.FTXParameter import FTXParameter

# TODO: extract Profile class if more profiles need to be added

# function that returns the default FTX parameters
def get_default_parameters(profile:str="debug")->dict:
    """
    Returns a dict with default FTX parameter values
        
        Parameters:
            key (str): debug (default) or production (keyword argument)
    """
    default_parameters = dict()

    # profile-specific parameters
    if profile == "debug":
        end_time = 5.0e-4
        loop_time_step = 2.5e-4
        n_impacts = 1000
    elif profile == "production":
        end_time = 10
        loop_time_step = 0.05
        n_impacts = 100000
    else:
        print(f"Unknown profile '{profile}'")
        raise ValueError("FTXPy -> defaults -> get_default_parameters(profile) : Unknown profile")
    
    # time control parameters
    default_parameters["INIT_TIME"]        = FTXParameter("INIT_TIME", "The start time of the simulation", 0)
    default_parameters["END_TIME"]         = FTXParameter("END_TIME", "The end time of the simulation", end_time)
    default_parameters["LOOP_TIME_STEP"]   = FTXParameter("LOOP_TIME_STEP", "The initial length of a loop", loop_time_step)  
    default_parameters["LOOP_TS_FACTOR"]   = FTXParameter("LOOP_TS_FACTOR", "The multiplication factor for the loop length", 2)
    default_parameters["LOOP_TS_NLOOPS"]   = FTXParameter("LOOP_TS_NLOOPS", "Multiply 'LOOP_TIME_STEP' by 'LOOP_TS_FACTOR' every 'LOOP_TS_NLOOPS' loops", 2)
    default_parameters["START_MODE"]       = FTXParameter("START_MODE", "Start mode of the simulation ('INIT' or 'RESTART')", "INIT")
    default_parameters["LOOP_N"]           = FTXParameter("LOOP_N", "FTX loop number", 0)
    default_parameters["XOLOTL_MAX_TS"]    = FTXParameter("XOLOTL_MAX_TS", "A limit on how much to increase Xolotl's max time step", 0.001)
    default_parameters["XOLOTL_NUM_TRIES"] = FTXParameter("XOLOTL_NUM_TRIES", "Number of times to try to run Xolotl before giving up", 1)

    default_parameters["start_stop"]       = FTXParameter("start_stop", "(?) A parameter in PETSc, should be ~'LOOP_TIME_STEP'/10", loop_time_step/10)
    default_parameters["ts_adapt_dt_max"]  = FTXParameter("ts_adapt_dt_max", "Initial value of time step in PETSc", 1e-5)  
    default_parameters["ts_atol"]          = FTXParameter("ts_atol", "Absolute tolerance in PETSc", 1e-4)
    default_parameters["ts_rtol"]          = FTXParameter("ts_rtol", "Relative tolerance in PETSc", 1e-4)
    
    # fidelity parameters
    default_parameters["grid_size"]        = FTXParameter("grid_size", "The size of the computational domain", 256)
    default_parameters["network_size"]     = FTXParameter("network_size", "The size of the network (maximum vacancy size)", 250)
    default_parameters["nImpacts"]         = FTXParameter("nImpacts", "The number of particles to use", n_impacts)

    # F-Tridyn parameters
    default_parameters["SBV_W"]            = FTXParameter("SBV_W", "Surface binding energy of W [eV]", 8.78, lower=8.68, upper=12)
    default_parameters["EF_W"]             = FTXParameter("EF_W", "Cutoff energy of W [eV]", 3, lower=2.7, upper=3.3)
    default_parameters["EF_He"]            = FTXParameter("EF_He", "Cutoff energy of He [eV]", 0.1, lower=0.09, upper=1.1)
    default_parameters["E0_He"]            = FTXParameter("E0_He", "Beam energy [eV]", 250, lower=240, upper=300)
    default_parameters["ALPHA0_He"]        = FTXParameter("ALPHA0_He", "Incident angle [degrees]", 0, lower=0, upper=30)

    # Xolotl parameters
    default_parameters["lattice"]          = FTXParameter("lattice", "The length of the lattice side [nm]", 0.317, lower=0.316, upper=0.318)
    default_parameters["impurityRadius"]   = FTXParameter("impurityRadius", "The radius of the main impurity [nm]", 0.3, lower=0.27, upper=0.33)
    default_parameters["biasFactor"]       = FTXParameter("biasFactor", "Interstitial bias factor (interstitial clusters have a larger strain field) [-]", 1.15, lower=1.035, upper=1.265)
    default_parameters["initialV"]         = FTXParameter("initialV", "The initial concentration of vacancies in the material [#/nm3]", 1e-18, lower=1e-19, upper=1e-17, log10_transform=True)
    default_parameters["voidPortion"]      = FTXParameter("voidPortion", "The fraction of the computational domain that is void", 10)
    default_parameters["burstingFactor"]   = FTXParameter("burstingFactor", "Multiplication constant for the bursting rate [-]", 2e8, lower=1e2, upper=1e9, log10_transform=True)
    default_parameters["burstingDepth"]    = FTXParameter("burstingDepth", "The depth after which there is an exponential decrease in the probability of bursting [nm]", 10, lower=1, upper=20)
    default_parameters["He1"]              = FTXParameter("He1", "Migration energy threshold (above which the diffusion will be ignored) for He1 clusters [eV]", 0.13, lower=0.11, upper=0.25)
    default_parameters["He2"]              = FTXParameter("He2", "Migration energy threshold (above which the diffusion will be ignored) for He2 clusters [eV]", 0.2, lower=0.2, upper=0.3)
    default_parameters["He3"]              = FTXParameter("He3", "Migration energy threshold (above which the diffusion will be ignored) for He3 clusters [eV]", 0.25, lower=0.25, upper=0.4)
    default_parameters["He4"]              = FTXParameter("He4", "Migration energy threshold (above which the diffusion will be ignored) for He4 clusters [eV]", 0.2, lower=0.15, upper=0.5)
    default_parameters["He5"]              = FTXParameter("He5", "Migration energy threshold (above which the diffusion will be ignored) for He5 clusters [eV]", 0.12, lower=0.1, upper=0.2)
    default_parameters["He6"]              = FTXParameter("He6", "Migration energy threshold (above which the diffusion will be ignored) for He6 clusters [eV]", 0.3, lower=0.3, upper=0.45)
    default_parameters["He7"]              = FTXParameter("He7", "Migration energy threshold (above which the diffusion will be ignored) for He7 clusters [eV]", 0.4, lower=0.3, upper=0.45)
    default_parameters["V1"]               = FTXParameter("V1", "Migration energy threshold (above which the diffusion will be ignored) for V1 clusters [eV]", 1.3, lower=1.1, upper=1.5)

    return default_parameters

# function that returns the default slurm settings
def get_default_slurm_settings(profile="debug")->dict:
    """
    Returns a dict with slurm settings
        
            Parameters:
                profile (str): debug (default) or production (keyword argument)
    """
    default_slurm_settings = dict()

    # profile-specific parameters
    if profile == "debug":
        partition = "debug"
        time_limit = 30
    elif profile == "production":
        partition = "regular"
        time_limit = 2880
    else:
        print(f"Unknown profile '{profile}'")
        raise ValueError("FTXPy -> defaults -> get_default_slurm_settings(profile) : Unknown profile")

    # slurm commands
    # NOTE: options should agree with the ones on https://github.com/PySlurm/pyslurm/blob/8febf21047d5f75e6335d65c341e82afa64f287c/pyslurm/pyslurm.pyx
    default_slurm_settings["job_name"] = "ftx_job"
    default_slurm_settings["account"] = "m1709"
    default_slurm_settings["constraints"] = "knl"
    default_slurm_settings["min_nodes"] = 2
    default_slurm_settings["output"] = "log.slurm.stdOut"
    default_slurm_settings["partition"] = partition
    default_slurm_settings["time_limit"] = time_limit
    return default_slurm_settings

# function that returns the default FTX commands to run
def get_default_ftx_commands()->list:
    """Returns a list with default commands to run"""
    return [
        "source $SLURM_SUBMIT_DIR/env.ips.cori",
        "source $SLURM_SUBMIT_DIR/env.GITR.cori.AL.sh",
        "export PYTHONPATH=$SLURM_SUBMIT_DIR:$PYTHONPATH",
        "module load python/3.9-anaconda-2021.11",
        "export OMP_PLACES=threads",
        "export OMP_PROC_BIND=spread",
        "python3 $IPS_PATH/bin/ips.py --config=ips.ftx.config --platform=conf.ips.cori --log=log.framework 2>>log.stdErr 1>>log.stdOut"
    ]
