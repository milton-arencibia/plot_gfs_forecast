import pygrib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
import numpy as np
import os
import sys
import datetime

# ==== CONFIGURATION ====
start_date = datetime.datetime(2025, 4, 1, 0)
end_date = datetime.datetime(2025, 4, 15, 23)
gfs_anl_dir = "/scratch1/NCEPDEV/global/glopara/data/metplus.data/archive/gfs/"
base_output_dir = "gfs_anl"

def plot_forecast_hour(forecast_hour, pressure_levels=[500]):
    forecast_datetime = start_date + datetime.timedelta(hours=forecast_hour)

    if forecast_datetime > end_date:
        print(f"❌ Forecast datetime {forecast_datetime} exceeds end_date {end_date}")
        return

    yyyymmddhh = forecast_datetime.strftime('%Y%m%d%H')
    grib_file = os.path.join(gfs_anl_dir, f"pgbanl.gdas.{yyyymmddhh}")

    if not os.path.exists(grib_file):
        print(f"❌ GRIB file not found: {grib_file}")
        return

    print(f"\n📂 Processing: {grib_file}")

    grbs = pygrib.open(grib_file)

    try:
        first_msg = grbs.message(1)
        yyyymmdd = str(first_msg.dataDate)
    except:
        yyyymmdd = forecast_datetime.strftime('%Y%m%d')

    output_dir = f"{base_output_dir}_{yyyymmdd}"
    os.makedirs(output_dir, exist_ok=True)

    variables = {
        'Precipitation rate': {'units': 'kg/m^2/s', 'cmap': 'Blues', 'level_type': 'surface'},
        'Temperature': {'units': '°C', 'cmap': 'coolwarm', 'convert': lambda x: x - 273.15, 'level_type': 'isobaricInhPa'},
        'Relative humidity': {'units': '%', 'cmap': 'BrBG', 'level_type': 'isobaricInhPa'},
        'Geopotential height': {'units': 'm', 'cmap': 'viridis', 'level_type': 'isobaricInhPa'},
        'U component of wind': {'units': 'm/s', 'cmap': 'RdBu_r', 'level_type': 'isobaricInhPa'},
        'V component of wind': {'units': 'm/s', 'cmap': 'RdBu_r', 'level_type': 'isobaricInhPa'},
        'Vertical velocity': {'units': 'Pa/s', 'cmap': 'bwr', 'level_type': 'isobaricInhPa'},
    }

    field_data = {var: [] for var in variables}
    latlon_cache = {}

    for grb in grbs:
        name = grb.name
        if name in variables and grb.typeOfLevel == variables[name]['level_type']:
            field_data[name].append(grb)

    print("\n📍 Plotting surface fields...")
    for varname, settings in variables.items():
        if settings['level_type'] != 'surface':
            continue

        grbs_list = field_data[varname]
        if not grbs_list:
            print(f"  ❌ {varname} not available at expected level")
            continue

        grb = grbs_list[0]
        level_label = "surface"
        data = settings.get('convert', lambda x: x)(grb.values)

        if varname not in latlon_cache:
            latlon_cache[varname] = grb.latlons()
        lats, lons = latlon_cache[varname]

        data_cyclic, lon_cyclic = add_cyclic_point(data, coord=lons[0])

        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_title(f"{varname} at {level_label}\nValid: {grb.validDate}")
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.STATES, linestyle=':')

        cf = plt.contourf(lon_cyclic, lats[:, 0], data_cyclic, levels=20, cmap=settings['cmap'], transform=ccrs.PlateCarree())
        plt.colorbar(cf, orientation='horizontal', pad=0.05, label=f"{varname} ({settings['units']})")

        fname = f"{varname.replace(' ', '_').lower()}_{level_label}_f{forecast_hour:03d}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150)
        plt.close()
        print(f"  ✅ Saved: {fname}")

    def get_grb(grbs_list, level):
        return next((grb for grb in grbs_list if grb.level == level), None)

    temperature_grbs = field_data['Temperature']
    available_levels = sorted({grb.level for grb in temperature_grbs})
    if not available_levels:
        print("⚠️ No temperature fields found on isobaric levels.")
        grbs.close()
        return

    missing_levels = [lvl for lvl in pressure_levels if lvl not in available_levels]
    if missing_levels:
        print(f"⚠️ Some requested pressure levels not found: {missing_levels}")

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

            data = settings.get('convert', lambda x: x)(grb.values)

            if varname not in latlon_cache:
                latlon_cache[varname] = grb.latlons()
            lats, lons = latlon_cache[varname]

            data_cyclic, lon_cyclic = add_cyclic_point(data, coord=lons[0])

            plt.figure(figsize=(10, 6))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_title(f"{varname} at {level} hPa\nValid: {grb.validDate}")
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS, linestyle=':')
            ax.add_feature(cfeature.STATES, linestyle=':')

            cf = plt.contourf(lon_cyclic, lats[:, 0], data_cyclic, levels=20, cmap=settings['cmap'], transform=ccrs.PlateCarree())
            plt.colorbar(cf, orientation='horizontal', pad=0.05, label=f"{varname} ({settings['units']})")

            fname = f"{varname.replace(' ', '_').lower()}_{level}hPa_f{forecast_hour:03d}.png"
            plt.savefig(os.path.join(output_dir, fname), dpi=150)
            plt.close()
            print(f"  ✅ Saved: {fname}")

    # === ZONAL MEAN WIND PLOTS ===
    print("\n📍 Plotting zonal mean winds...")
    for comp in ['U component of wind', 'V component of wind']:
        levels = []
        latitudes = None
        zonal_means = []

        for grb in sorted(field_data[comp], key=lambda g: g.level):
            data = grb.values
            lats, _ = grb.latlons()
            zonal_mean = np.mean(data, axis=1)  # mean over longitude
            zonal_means.append(zonal_mean)
            levels.append(grb.level)
            if latitudes is None:
                latitudes = lats[:, 0]

        if not zonal_means:
            print(f"  ❌ No zonal means available for {comp}")
            continue

        zonal_means = np.array(zonal_means)
        levels = np.array(levels)

        plt.figure(figsize=(10, 6))
        cf = plt.contourf(latitudes, levels, zonal_means, levels=20, cmap=variables[comp]['cmap'])
        plt.gca().invert_yaxis()
        plt.colorbar(cf, orientation='horizontal', pad=0.05, label=f"{comp} ({variables[comp]['units']})")
        plt.title(f"Zonal Mean {comp}\nValid: {forecast_datetime}")
        plt.xlabel("Latitude")
        plt.ylabel("Pressure Level (hPa)")

        fname = f"zonal_mean_{comp.split()[0].lower()}_f{forecast_hour:03d}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150)
        plt.close()
        print(f"  ✅ Saved: {fname}")

    grbs.close()

# ==== ENTRY POINT ====
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_gfs_analysis.py <forecast_hour> [pressure_levels]")
        sys.exit(1)

    forecast_hour = int(sys.argv[1])
    if len(sys.argv) >= 3:
        try:
            pressure_levels = [int(x) for x in sys.argv[2].split(',')]
        except Exception as e:
            print(f"❌ Invalid pressure levels: {e}")
            sys.exit(1)
    else:
        pressure_levels = [500]

    plot_forecast_hour(forecast_hour, pressure_levels)

