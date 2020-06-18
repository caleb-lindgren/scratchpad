#!/bin/bash

#SBATCH --time=18:00:00   # walltime
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=524288M   # memory per CPU core
#SBATCH --mail-user=calebmlindgren@gmail.com   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

jupyter nbconvert --ExecutePreprocessor.timeout=None --to notebook --inplace --execute 5_wst2_find_enriched_pathways_gseapy_reactome.ipynb
