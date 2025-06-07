#!/bin/bash
#SBATCH --time=00:45:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --account=fv3-cpu
#SBATCH --job-name=ncplot_F${FCST_HR}
#SBATCH --output=log_F${FCST_HR}.out
#SBATCH --error=log_F${FCST_HR}.err
#SBATCH --qos=batch

set -x

# Activate Conda environment
source /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/etc/profile.d/conda.sh
conda activate /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/envs/pyn_env

# Run the plotting script
echo "📅 Starting job for $NCFILE at forecast hour $FCST_HR with levels $LEVELS"
python plot_nc_fields.py $NCFILE $FCST_HR $LEVELS

