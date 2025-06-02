import pygrib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import sys

def plot_forecast_hour(forecast_hour, pressure_levels=[500], input_dir='.', output_dir='level_plots'):
    # Format forecast hour with zero-padding (e.g., 6 -> '006')
    fh_str = f"{forecast_hour:03d}"
    grib_file = os.path.join(input_dir, f"gfs.t00z.pgrb2.0p25.f{fh_str}")

    if not os.path.exists(grib_file):
        print(f"GRIB file not found: {grib_file}")
        return

    print(f"\nProcessing forecast hour: {forecast_hour} (file: {grib_file})")
    os.makedirs(output_dir, exist_ok=True)

    # Variables to plot with settings
    variables = {
        # Surface-related and heightAboveGround first
        'Convective available potential energy': {'units': 'J/kg', 'cmap': 'YlGnBu', 'level_type': 'surface'},
        '2 metre temperature': {'units': '°C', 'cmap': 'coolwarm', 'convert': lambda x: x - 273.15, 'level_type': 'heightAboveGround'},
        '2 metre relative humidity': {'units': '%', 'cmap': 'BrBG', 'level_type': 'heightAboveGround'},
        'Precipitation rate': {'units': 'kg/m^2/s', 'cmap': 'Blues', 'level_type': 'surface'},

        # Isobaric level variables
        'Temperature': {'units': '°C', 'cmap': 'coolwarm', 'convert': lambda x: x - 273.15, 'level_type': 'isobaricInhPa'},
        'Geopotential height': {'units': 'm', 'cmap': 'viridis', 'level_type': 'isobaricInhPa'},
        'U component of wind': {'units': 'm/s', 'cmap': 'RdBu_r', 'level_type': 'isobaricInhPa'},
        'V component of wind': {'units': 'm/s', 'cmap': 'RdBu_r', 'level_type': 'isobaricInhPa'},
        'Vertical velocity': {'units': 'Pa/s', 'cmap': 'bwr', 'level_type': 'isobaricInhPa'},
    }

    grbs = pygrib.open(grib_file)
    field_data = {var: [] for var in variables}

    # Cache lat/lon for each variable to avoid recomputing
    latlon_cache = {}

    # Collect GRIB messages by variable and level type
    for grb in grbs:
        name = grb.name
        if name in variables:
            if grb.typeOfLevel == variables[name]['level_type']:
                field_data[name].append(grb)

    # Plot surface and near-surface fields (no level selection)
    print("\n📍 Plotting surface and near-surface fields...")
    for varname, settings in variables.items():
        if settings['level_type'] not in ['surface', 'heightAboveGround']:
            continue

        grbs_list = field_data[varname]
        if not grbs_list:
            print(f"  ❌ {varname} not available at expected level")
            continue

        grb = grbs_list[0]
        level_label = f"{grb.level}m" if settings['level_type'] == 'heightAboveGround' else "surface"

        data = grb.values
        if 'convert' in settings:
            data = settings['convert'](data)

        # Cache lat/lon once per variable
        if varname not in latlon_cache:
            latlon_cache[varname] = grb.latlons()
        lats, lons = latlon_cache[varname]

        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_title(f"{varname} at {level_label}\nValid: {grb.validDate}")
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.STATES, linestyle=':')

        cf = plt.contourf(lons, lats, data, levels=20, cmap=settings['cmap'], transform=ccrs.PlateCarree())
        plt.colorbar(cf, orientation='horizontal', pad=0.05, label=f"{varname} ({settings['units']})")

        fname = f"{varname.replace(' ', '_').lower()}_{level_label}_f{fh_str}.png"
        filepath = os.path.join(output_dir, fname)
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"  ✅ Saved: {fname}")

    # Plot isobaric variables at selected levels
    def get_grb(grbs_list, level):
        for grb in grbs_list:
            if grb.level == level:
                return grb
        return None

    # Determine available pressure levels from temperature field (optional check)
    temperature_grbs = field_data['Temperature']
    available_levels = sorted({grb.level for grb in temperature_grbs})
    if not available_levels:
        print("No temperature fields found on isobaric levels.")
        grbs.close()
        return

    # If user requested levels not in file, warn
    missing_levels = [lvl for lvl in pressure_levels if lvl not in available_levels]
    if missing_levels:
        print(f"Warning: Some requested pressure levels not found in file: {missing_levels}")

    for level in pressure_levels:
        if level not in available_levels:
            continue
        print(f"\n📍 Plotting isobaric fields at {level} hPa...")
        for varname, settings in variables.items():
            if settings['level_type'] != 'isobaricInhPa':
                continue
            grb = get_grb(field_data[varname], level)
            if grb is None:
                print(f"  ❌ {varname} not available at {level} hPa")
                continue

            data = grb.values
            if 'convert' in settings:
                data = settings['convert'](data)

            if varname not in latlon_cache:
                latlon_cache[varname] = grb.latlons()
            lats, lons = latlon_cache[varname]

            plt.figure(figsize=(10, 6))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_title(f"{varname} at {level} hPa\nValid: {grb.validDate}")
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS, linestyle=':')
            ax.add_feature(cfeature.STATES, linestyle=':')

            cf = plt.contourf(lons, lats, data, levels=20, cmap=settings['cmap'], transform=ccrs.PlateCarree())
            plt.colorbar(cf, orientation='horizontal', pad=0.05, label=f"{varname} ({settings['units']})")

            fname = f"{varname.replace(' ', '_').lower()}_{level}hPa_f{fh_str}.png"
            filepath = os.path.join(output_dir, fname)
            plt.savefig(filepath, dpi=150)
            plt.close()
            print(f"  ✅ Saved: {fname}")

    grbs.close()


if __name__ == "__main__":
    # Command-line args: start_hr end_hr step_hr
    if len(sys.argv) == 4:
        try:
            start_hr = int(sys.argv[1])
            end_hr = int(sys.argv[2])
            step_hr = int(sys.argv[3])
            forecast_hours = list(range(start_hr, end_hr + 1, step_hr))
        except Exception as e:
            print(f"Invalid arguments: {e}")
            sys.exit(1)
    else:
        # Default forecast hour(s)
        forecast_hours = [0, 6, 12]

    for fh in forecast_hours:
        plot_forecast_hour(fh, pressure_levels=[500, 850, 250])

