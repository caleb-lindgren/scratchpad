#!/bin/bash

#SBATCH --time=07:00:00   # walltime
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=8192M   # memory per CPU core

jupyter nbconvert --ExecutePreprocessor.timeout=None --to notebook --inplace --execute pancancer_enrichment_step_1.ipynb
