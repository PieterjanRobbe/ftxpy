#!/bin/sh
#SBATCH -A m1709
#SBATCH --job-name=ftx_job
#SBATCH --output=log.slurm.stdOut

#SBATCH --qos=regular
#SBATCH -C cpu
#SBATCH --nodes=1
#SBATCH -t 12:00:00

source activate ftx
module load PrgEnv-intel intel
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/gcc/11.2.0/snos/lib64
export OMP_PLACES=threads
export OMP_PROC_BIND=spread
ips.py --config=/pscratch/sd/p/pieterja/ftxpy/parameter_study/V1_1/init_V1_1/ips.ftx.config --platform=$CFS/atom/users/$USER/ips-examples/iterative-xolotlFT-UQ/conf.ips.cori --log=log.framework.0 2>>log.stdErr.0 1>>log.stdOut.0
