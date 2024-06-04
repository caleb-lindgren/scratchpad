#!/bin/bash

#SBATCH -c 1
#SBATCH -t 0-01:00
#SBATCH -p short
#SBATCH --mem=8G
#SBATCH -o log/slurm_%j_%a.out 
#SBATCH -e log/slurm_%j_%a.err 
#SBATCH --array=0-999

python simulate.py $SLURM_ARRAY_TASK_ID
