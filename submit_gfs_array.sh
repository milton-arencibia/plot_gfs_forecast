#!/bin/bash

# Default forecast range: 0 to 72 hours every 6h
START_HR=${1:-0}
END_HR=${2:-72}
INTERVAL=${3:-6}
PRESSURE_LEVELS=${4:-500}  # Default to 500 hPa if not passed

# Compute number of array tasks
NUM_JOBS=$(( (END_HR - START_HR) / INTERVAL + 1 ))
MAX_TASK_ID=$(( NUM_JOBS - 1 ))

echo "🚀 Submitting Slurm array for forecast hours $START_HR to $END_HR every ${INTERVAL}h"
echo "   This will create $NUM_JOBS tasks (array 0-$MAX_TASK_ID)"
echo "📋 Pressure levels: $PRESSURE_LEVELS"

# Export environment and submit job with computed array range and pressure levels
sbatch --export=START_HR=${START_HR},END_HR=${END_HR},INTERVAL=${INTERVAL},PRESSURE_LEVELS=${PRESSURE_LEVELS} \
       --array=0-${MAX_TASK_ID} \
       plot_gfs_array.sbatch

