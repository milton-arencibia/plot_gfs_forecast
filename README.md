# plot_gfs_forecast
Instructions:

    Modify slurm job: plot_gfs_array.sbatch to pecify path to conda.sh and environment. See plot_gfs_forecast.py for required packages.

    bash submit_gfs_array.sh start_hr end_hr interval_hr pressure_levels
    Default forecast range: 0 to 24 hours every 6h
    Default pressure level for isobaric levels: 500hPa

    example:

    bash submit_gfs_array.sh 0 24 6 500,850

    for 24H at 6H intervals with isobaric levels 500, 800 hPa

    Add additional fields by modifying plot_gfs_forecast.py. Use the tool inspect_grib.py to view structure of GRIB and determine vertical Level Type for new fields.
