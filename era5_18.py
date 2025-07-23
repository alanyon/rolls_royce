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
    "day": ["18"],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00"
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