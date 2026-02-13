import ee
import os
import json

# Load service account key from GitHub Secret
service_account_json = os.environ["EE_SERVICE_ACCOUNT"]
service_account_info = json.loads(service_account_json)

credentials = ee.ServiceAccountCredentials(
    service_account_info["client_email"],
    key_data=service_account_json
)

ee.Initialize(credentials)

# Load your government land asset
govtArea = ee.FeatureCollection(
    "projects/civic-ripsaw-483614-e7/assets/thoothukudi_all_markings_1770985974520"
)

# Load Sentinel-2 images (OLD YEAR)
oldImage = (ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(govtArea)
    .filterDate("2023-01-01", "2023-12-31")
    .median()
)

# Load Sentinel-2 images (NEW YEAR)
newImage = (ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(govtArea)
    .filterDate("2025-01-01", "2025-12-31")
    .median()
)

# NDVI calculation
ndvi2023 = oldImage.normalizedDifference(["B8", "B4"])
ndvi2025 = newImage.normalizedDifference(["B8", "B4"])

ndviDiff = ndvi2025.subtract(ndvi2023)

# Detect strong vegetation change
strongChange = ndviDiff.abs().gt(0.2)

# Calculate change area
changeArea = strongChange.multiply(ee.Image.pixelArea())

stats = changeArea.reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=govtArea,
    scale=10,
    maxPixels=1e13
)

changedArea = stats.getInfo()

print("Changed Area (sqm):", changedArea)
