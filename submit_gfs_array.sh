#!/bin/bash

# Default forecast range: 0 to 72 hours every 6h
START_HR=${1:-0}
END_HR=${2:-72}
INTERVAL=${3:-6}

# Compute number of array tasks
NUM_JOBS=$(( (END_HR - START_HR) / INTERVAL + 1 ))
MAX_TASK_ID=$(( NUM_JOBS - 1 ))

echo "🚀 Submitting Slurm array for forecast hours $START_HR to $END_HR every $INTERVALh"
echo "   This will create $NUM_JOBS tasks (array 0-$MAX_TASK_ID)"

# Export environment and submit job with computed array range
sbatch --export=START_HR=${START_HR},END_HR=${END_HR},INTERVAL=${INTERVAL} \
       --array=0-${MAX_TASK_ID} \
       plot_gfs_array.sbatch

