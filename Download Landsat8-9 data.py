from pystac_client import Client
from planetary_computer import sign
from shapely.geometry import box, mapping
import os, requests

# ---------- 1. Define AOI ----------
minx, miny, maxx, maxy = 76.0, 18.0, 77.0, 19.0  # Change this to your bounding box
aoi = mapping(box(minx, miny, maxx, maxy))

# ---------- 2. Date and Cloud Filter ----------
start_date = "2020-01-01"
end_date = "2020-01-31"
max_cloud_cover = 20  # in percent

# ---------- 3. Connect to STAC and Search Landsat ----------
catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

search = catalog.search(
    collections=["landsat-8-c2-l2"],  # Level-2 surface reflectance
    intersects=aoi,
    datetime=f"{start_date}/{end_date}",
    query={"eo:cloud_cover": {"lt": max_cloud_cover}},
)

items = sorted(search.get_items(), key=lambda x: x.properties["eo:cloud_cover"])
if not items:
    print("No matching Landsat scenes found.")
    exit()

# ---------- 4. Select Least Cloudy Image ----------
best_item = items[0]
print("Scene ID:", best_item.id)
print("Cloud Cover:", best_item.properties["eo:cloud_cover"])
print("Acquisition Date:", best_item.datetime)

# ---------- 5. Download Selected Bands ----------
# Landsat bands: SR_B2 = Blue, SR_B3 = Green, SR_B4 = Red, SR_B5 = NIR, etc.
bands_to_download = ["SR_B2", "SR_B3", "SR_B4"]  # RGB bands

output_dir = "landsat_download"
os.makedirs(output_dir, exist_ok=True)

for band in bands_to_download:
    asset = best_item.assets[band]
    signed_url = sign(asset.href)
    filename = os.path.join(output_dir, f"{best_item.id}_{band}.tif")

    print(f"Downloading {band} to {filename}")
    r = requests.get(signed_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("Download complete.")
