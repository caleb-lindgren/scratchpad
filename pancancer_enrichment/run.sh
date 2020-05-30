#!/bin/bash

#SBATCH --time=10:00:00   # walltime
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=4096M   # memory per CPU core
#SBATCH --mail-user=calebmlindgren@gmail.com   # email address
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

jupyter nbconvert --ExecutePreprocessor.timeout=None --to notebook --inplace --execute pancancer_enrichment_step_1.ipynb
