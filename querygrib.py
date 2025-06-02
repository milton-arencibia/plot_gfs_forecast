import pygrib

# GRIB file path
grib_file = 'gfs.t00z.pgrb2.0p25.f000'

# Open GRIB file
grbs = pygrib.open(grib_file)

# Store unique variable names
variable_info = set()

for grb in grbs:
    # You can include more fields for deeper inspection
    variable_info.add((
        grb.name,             # full descriptive name
        grb.shortName,        # short identifier (e.g. 't', 'gh', 'u')
        grb.parameterName,    # raw parameter name from GRIB
        grb.typeOfLevel       # e.g. 'isobaricInhPa', 'surface'
    ))

grbs.close()

# Sort and print
print(f"\nVariables in GRIB file: {grib_file}\n")
print(f"{'Full Name':40} {'Short Name':10} {'Parameter':30} {'Level Type'}")
print("="*100)
for name, short, param, level in sorted(variable_info):
    print(f"{name:40} {short:10} {param:30} {level}")


