from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
import os

def main(ncfile):
    ds = Dataset(ncfile, "r")

    if "T2" not in ds.variables:
        print("❌ 'T2' (2-metre temperature) not found in the file.")
        return

    # Extract time string
    times = ds.variables["Times"][:]
    time_str = times[0].tobytes().decode("utf-8").strip()
    time_tag = time_str.replace("-", "").replace(":", "").replace("_", "")

    print(f"✅ Found time: {time_str}")
    print("📌 T2 has shape:", ds.variables["T2"].shape)

    input("Press Enter to continue and save the plot...")

    # Load 2m temperature (first time step), convert to Celsius
    t2 = ds.variables["T2"][0, :, :] - 273.15

    # Latitude and longitude
    try:
        lats = ds.variables["XLAT"][0, :, :]
        lons = ds.variables["XLONG"][0, :, :]
    except KeyError:
        print("❌ Could not find XLAT/XLONG.")
        return

    # Plot setup
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_title(f"2-metre Temperature (°C)\nValid: {time_str}")
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')

    cf = ax.contourf(lons, lats, t2, levels=20, cmap="coolwarm", transform=ccrs.PlateCarree())
    plt.colorbar(cf, orientation='horizontal', pad=0.05, label='Temperature (°C)')
    plt.tight_layout()

    # Save file
    out_name = f"t2_temperature_{time_tag}.png"
    plt.savefig(out_name, dpi=150)
    plt.close()
    print(f"✅ Saved plot: {out_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python plot_t2_mpas_netcdf4.py <MPAS file>")
    else:
        main(sys.argv[1])

