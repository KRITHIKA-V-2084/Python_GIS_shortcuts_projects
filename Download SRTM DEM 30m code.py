import srtm
import numpy as np
import rasterio
from rasterio.transform import from_origin

# Define the area
min_lat, max_lat = 18.0, 19.0
min_lon, max_lon = 76.0, 77.0
resolution = 0.0008333  # ~30 meters

# Create the elevation data instance
elevation_data = srtm.get_data()

# Generate grid
lat_vals = np.arange(max_lat, min_lat, -resolution)
lon_vals = np.arange(min_lon, max_lon, resolution)
elevation_grid = np.zeros((len(lat_vals), len(lon_vals)), dtype=np.int16)

# Fill grid with elevation
for i, lat in enumerate(lat_vals):
    for j, lon in enumerate(lon_vals):
        elevation = elevation_data.get_elevation(lat, lon)
        if elevation is None:
            elevation = -32768  # No data
        elevation_grid[i, j] = elevation

# Save to GeoTIFF
transform = from_origin(min_lon, max_lat, resolution, resolution)
with rasterio.open(
    "dem_30m.tif",
    "w",
    driver="GTiff",
    height=elevation_grid.shape[0],
    width=elevation_grid.shape[1],
    count=1,
    dtype=elevation_grid.dtype,
    crs="EPSG:4326",
    transform=transform,
) as dst:
    dst.write(elevation_grid, 1)

print("DEM saved as dem_30m.tif")
