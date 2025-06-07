#!/usr/bin/env python3
import os
import sys
import numpy as np
from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# --- Handle command-line arguments ---
if len(sys.argv) < 4:
    print("Usage: python plot_nc_fields.py <netcdf_file> <forecast_hour> <level1,level2,...>")
    sys.exit(1)

nc_file = sys.argv[1]
forecast_hour = sys.argv[2]
levels = [int(lvl) for lvl in sys.argv[3].split(',')]

# --- Load Dataset ---
ds = Dataset(nc_file)

# --- Extract valid time ---
time_var = ds.variables['XTIME']
valid_time = num2date(time_var[:], time_var.units)[0]

# --- Setup output directory ---
start_date = "20250401"
outdir = f"mpassit_plots_{start_date}"
os.makedirs(outdir, exist_ok=True)

# --- Variable plotting setup ---
fixed_vars = {
    'RAINNC': 'rainnc',
    'U10': 'u10',
    'V10': 'v10',
    'Q2': 'q2',
    'T2': 't2'
}

level_vars = {
    'T': 't',
    'U': 'u',
    'V': 'v',
    'W': 'w'
}

def plot_field(data, lats, lons, title, filename):
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')
    cf = ax.contourf(lons, lats, data, levels=20, cmap='viridis', transform=ccrs.PlateCarree())
    plt.title(title)
    plt.colorbar(cf, orientation='horizontal', pad=0.05)
    plt.savefig(filename, dpi=150)
    plt.close()

# --- Coordinate variables ---
lats = ds.variables['XLAT'][0]
lons = ds.variables['XLONG'][0]

# --- Plot fixed-height variables ---
for varname in fixed_vars:
    if varname in ds.variables:
        var = ds.variables[varname]
        desc = var.description if 'description' in var.ncattrs() else varname
        data = var[0, :, :]
        fname = os.path.join(outdir, f"{fixed_vars[varname]}_F{int(forecast_hour):03d}.png")
        title = f"{desc}\nValid: {valid_time.strftime('%Y-%m-%d %H:%M:%S')}"
        plot_field(data, lats, lons, title, fname)
        print(f"✅ Saved: {fname}")

# --- Plot variable-height variables ---
for varname in level_vars:
    if varname in ds.variables:
        var = ds.variables[varname]
        desc = var.description if 'description' in var.ncattrs() else varname
        for lvl in levels:
            if lvl >= var.shape[1]:
                print(f"⚠️  Skipping {varname} level {lvl}: out of bounds")
                continue
            data = var[0, lvl, :, :]
            fname = os.path.join(outdir, f"{level_vars[varname]}_lvl{lvl}_F{int(forecast_hour):03d}.png")
            title = f"{desc} at MPAS lvl {lvl}\nValid: {valid_time.strftime('%Y-%m-%d %H:%M:%S')}"
            plot_field(data, lats, lons, title, fname)
            print(f"✅ Saved: {fname}")

ds.close()

