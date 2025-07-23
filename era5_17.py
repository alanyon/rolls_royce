import cdsapi

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "geopotential",
        "relative_humidity",
        "temperature"
    ],
    "year": ["2023"],
    "month": ["07"],
    "day": ["17"],
    "time": [
        "22:00", "23:00"
    ],
    "pressure_level": [
        "350", "400", "450", "500", "550", "600", "650", "700", "750", "775", 
        "800", "825", "850", "875", "900", "925", "950", "975", "1000"
    ],
    "data_format": "grib",
    "download_format": "unarchived",
    "area": [47.4989, 2.3607, 46.4989, 3.8607],  # North, West, South, East
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()