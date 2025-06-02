#!/bin/bash
#SBATCH --job-name=gfs_plot
#SBATCH --output=log.plots.%A_%a.out
#SBATCH --error=log.plots.%A_%a.err
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --mem=4G
#SBATCH --account=fv3-cpu
#SBATCH --qos=batch

source /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/etc/profile.d/conda.sh
conda activate /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/envs/pyn_env

# Read forecast configuration from environment variables
start_hr=${START_HR:-0}
end_hr=${END_HR:-72}
interval=${INTERVAL:-6}

forecast_hour=$((start_hr + SLURM_ARRAY_TASK_ID * interval))

# Exit early if forecast_hour exceeds end_hr
if (( forecast_hour > end_hr )); then
    echo "⏭️ Skipping: forecast_hour $forecast_hour > $end_hr"
    exit 0
fi

# Optional: Rename job at runtime to reflect forecast hour
scontrol update JobName=gfs_plot_f${forecast_hour} JobId=$SLURM_JOB_ID

echo "🌀 Running forecast hour: $forecast_hour"

# Call your actual plotting script
python plot_gfs_forecast.py "$forecast_hour"

