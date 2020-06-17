#!/bin/bash

#SBATCH --time=02:00:00   # walltime
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=262144M   # memory per CPU core
#SBATCH --mail-user=calebmlindgren@gmail.com   # email address
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

jupyter nbconvert --ExecutePreprocessor.timeout=None --to notebook --inplace --execute 5_find_enriched_pathways_gseapy_reactome.ipynb
