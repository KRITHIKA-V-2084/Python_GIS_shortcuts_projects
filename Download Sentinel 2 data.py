from pystac_client import Client
from planetary_computer import sign
from shapely.geometry import box, mapping
import requests
import os

# ---------- 1. Define AOI and Filters ----------
# Define bounding box (or use shapefile)
minx, miny, maxx, maxy = 76.0, 18.0, 77.0, 19.0
aoi = mapping(box(minx, miny, maxx, maxy))

start_date = "2023-01-01"
end_date = "2023-01-31"
max_cloud_cover = 20  # in percent

# ---------- 2. Connect to Planetary Computer STAC ----------
catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

search = catalog.search(
    collections=["sentinel-2-l2a"],
    intersects=aoi,
    datetime=f"{start_date}/{end_date}",
    query={"eo:cloud_cover": {"lt": max_cloud_cover}},
)

items = sorted(search.get_items(), key=lambda x: x.properties["eo:cloud_cover"])
if not items:
    print("No images found.")
    exit()

# ---------- 3. Select Best (Least Cloudy) ----------
best_item = items[0]
print("Best scene:", best_item.id)
print("Cloud cover:", best_item.properties["eo:cloud_cover"], "%")
print("Date:", best_item.datetime)

# ---------- 4. Download Specific Bands ----------
# You can change/add bands like B08 (NIR), B11 (SWIR), etc.
bands_to_download = ["B02", "B03", "B04"]  # Blue, Green, Red
output_dir = "sentinel_download"
os.makedirs(output_dir, exist_ok=True)

for band in bands_to_download:
    asset = best_item.assets[band]
    signed_url = sign(asset.href)  # Authenticate with PC token
    file_path = os.path.join(output_dir, f"{best_item.id}_{band}.tif")
    
    print(f"Downloading {band} to {file_path}")
    r = requests.get(signed_url, stream=True)
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("Download complete.")
