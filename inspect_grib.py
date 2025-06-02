import pygrib
import sys
import os

# --- Handle command-line argument ---
if len(sys.argv) != 2:
    print("Usage: python inspect_grib.py <grib_file>")
    sys.exit(1)

grib_file = sys.argv[1]

if not os.path.isfile(grib_file):
    print(f"Error: File '{grib_file}' not found.")
    sys.exit(1)

# --- Open GRIB file ---
grbs = pygrib.open(grib_file)

# --- Collect unique variable entries ---
variable_info = set()

for grb in grbs:
    variable_info.add((
        grb.name,          # Full descriptive name
        grb.shortName,     # Short name (e.g. 't')
        grb.parameterName, # Parameter ID name
        grb.typeOfLevel,   # e.g. 'isobaricInhPa'
        grb.level          # Pressure level or height
    ))

grbs.close()

# --- Output table ---
print(f"\n📦 Variables in GRIB file: {grib_file}\n")
print(f"{'Full Name':40} {'Short Name':10} {'Parameter':30} {'Level Type':20} {'Level'}")
print("=" * 120)

for name, short, param, level_type, level in sorted(variable_info):
    print(f"{name:40} {short:10} {param:30} {level_type:20} {level}")

