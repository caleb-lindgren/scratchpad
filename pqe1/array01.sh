#!/bin/bash

#SBATCH -c 1
#SBATCH -t 0-01:00
#SBATCH -p short
#SBATCH --mem=2G
#SBATCH -o log/slurm_%j_%a.out 
#SBATCH -e log/slurm_%j_%a.err 
#SBATCH --array=0-9999

#python simulate.py $SLURM_ARRAY_TASK_ID
python simulate.py $((SLURM_ARRAY_TASK_ID + 10000))
