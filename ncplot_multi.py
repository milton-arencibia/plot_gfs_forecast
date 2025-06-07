import sys
import os
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_variable(ncfile, var_name, var_levels=None, level_indices=None):
    desc = ncfile.variables[var_name].description if 'description' in ncfile.variables[var_name].ncattrs() else var_name
    data = ncfile.variables[var_name]
    coords = data.coordinates.split() if 'coordinates' in data.ncattrs() else []

    # Surface or 2D fields
    if data.ndim == 3:
        lat = ncfile.variables[coords[1]][:]
        lon = ncfile.variables[coords[0]][:]
        values = data[0, :, :]

        plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)
        ax.set_title(f"{desc} (surface)")
        cf = ax.contourf(lon, lat, values, transform=ccrs.PlateCarree(), cmap='viridis')
        plt.colorbar(cf, orientation='horizontal', pad=0.05, label=data.units)
        out_path = f"plots/{var_name.lower()}_surface.png"
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"✅ Saved: {out_path}")

    # 4D fields (Time, Level, Lat, Lon)
    elif data.ndim == 4 and level_indices is not None:
        lat = ncfile.variables[coords[1]][:]
        lon = ncfile.variables[coords[0]][:]

        for level in level_indices:
            if level < 0 or level >= data.shape[1]:
                print(f"⚠️ Skipping {var_name} at level {level} (out of range)")
                continue

            values = data[0, level, :, :]
            plt.figure(figsize=(10, 6))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS)
            ax.set_title(f"{desc} (level {level})")
            cf = ax.contourf(lon, lat, values, transform=ccrs.PlateCarree(), cmap='viridis')
            plt.colorbar(cf, orientation='horizontal', pad=0.05, label=data.units)
            out_path = f"plots/{var_name.lower()}_level{level}.png"
            plt.savefig(out_path, dpi=150)
            plt.close()
            print(f"✅ Saved: {out_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py file.nc [level1,level2,...]")
        sys.exit(1)

    nc_path = sys.argv[1]
    levels = []
    if len(sys.argv) == 3:
        try:
            levels = [int(lvl.strip()) for lvl in sys.argv[2].split(',')]
        except ValueError:
            print("❌ Invalid level specification.")
            sys.exit(1)

    os.makedirs("plots", exist_ok=True)

    with Dataset(nc_path) as nc:
        # Surface/2D variables
        surface_vars = ['RAINNC', 'U10', 'V10', 'Q2', 'T2']
        for var in surface_vars:
            if var in nc.variables:
                plot_variable(nc, var)

        # 3D variables (use specified levels)
        level_vars = ['T', 'U', 'V', 'W']
        for var in level_vars:
            if var in nc.variables:
                plot_variable(nc, var, level_indices=levels if levels else [1])  # Default to level 1

if __name__ == "__main__":
    main()

