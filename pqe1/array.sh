#!/bin/bash

#SBATCH -c 1
#SBATCH -t 0-00:10
#SBATCH -p short
#SBATCH --mem=1000M
#SBATCH -o log/slurm_%j_%a.out 
#SBATCH -e log/slurm_%j_%a.err 
#SBATCH --array=0-9999

echo $((SIM_MULT * 10000 + SLURM_ARRAY_TASK_ID ))
python simulate.py $((SIM_MULT * 10000 + SLURM_ARRAY_TASK_ID ))
