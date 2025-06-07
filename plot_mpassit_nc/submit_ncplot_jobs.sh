#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: bash submit_ncplot_jobs.sh <start_hr> <end_hr> <interval> <levels (e.g., 1,2)>"
    exit 1
fi

start_hr=$1
end_hr=$2
interval=$3
levels=$4

for ((hr=start_hr; hr<=end_hr; hr+=interval)); do
    fcst_hour=$(printf "%03d" $hr)
    datestr=$(date -d "2025-04-01 +${hr} hours" +"%Y-%m-%d_%H.00.00")
    ncfile="MPAS-out.${datestr}.nc"

    echo "🚀 Submitting forecast hour: $fcst_hour ($ncfile)"
    sbatch --export=ALL,NCFILE=$ncfile,FCST_HR=$fcst_hour,LEVELS=$levels \
           --job-name=ncplot_F${fcst_hour} \
           --output=log_F${fcst_hour}.out \
           --error=log_F${fcst_hour}.err \
           plot_nc_job.slurm
done

