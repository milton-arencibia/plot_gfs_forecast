#!/bin/bash
#SBATCH --job-name=gfs_plot
#SBATCH --output=log.plots.%A_%a.out
#SBATCH --error=log.plots.%A_%a.err
#SBATCH --time=01:30:00
#SBATCH --ntasks=1
#SBATCH --mem=4G
#SBATCH --account=fv3-cpu
#SBATCH --qos=batch

# Activate the Conda environment
source /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/etc/profile.d/conda.sh
conda activate /scratch1/NCEPDEV/global/Milton.Arencibia/miniforge/envs/pyn_env

# Read forecast configuration from environment variables
start_hr=${START_HR:-0}
end_hr=${END_HR:-72}
interval=${INTERVAL:-6}
pressure_levels=${PRESSURE_LEVELS:-500}  # Default to 500 hPa

# Calculate forecast hour for this task
forecast_hour=$((start_hr + SLURM_ARRAY_TASK_ID * interval))

# Exit early if forecast_hour exceeds end_hr
if (( forecast_hour > end_hr )); then
    echo "⏭️ Skipping: forecast_hour $forecast_hour > $end_hr"
    exit 0
fi

# Optional: Rename job at runtime to reflect forecast hour
scontrol update JobName=gfs_plot_f${forecast_hour} JobId=$SLURM_JOB_ID

echo "🌀 Running forecast hour: $forecast_hour"
echo "📋 Pressure levels: $pressure_levels"

# Call the plotting script
python -u plot_gfs_forecast.py "$forecast_hour" "$pressure_levels"
#python -u plot_gfs_analysis.py "$forecast_hour" "$pressure_levels"
