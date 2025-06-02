# plot_gfs_forecast
Instructions:

    Modify slurm job: plot_gfs_array.sbatch to pecify path to conda.sh and environment. See plot_gfs_forecast.py for required packages.

    bash submit_gfs_array.sh start_hr end_hr interval
    Default forecast range: 0 to 72 hours every 6h

    Add additional fields by modifying plot_gfs_forecast.py. Use the tool inspect_grib.py to view structure of GRIB and determine vertical Level Type for new fields.
