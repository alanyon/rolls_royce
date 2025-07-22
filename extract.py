"""
Module to extract and process ERA5 and METAR data.

Functions:
    main: Main function to run the data extraction and processing.
    assert_coord_equal: Asserts two cubes have the same coord values.
    get_metars: Loads METAR data from an Excel file.
    make_df: Creates a DataFrame from ERA5 data cubes.
    make_map: Creates a map visualisation of ERA5 grid points.
    relative_humidity: Calculates relative humidity.
"""
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import iris
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Name of ERA5 data file
ERA_FILE = '4e3fb9be07438fe7a43509464b9bc36b.grib'
# To stop iris future warnings
iris.FUTURE.date_microseconds = True


def main():
    """
    Main function to run the data extraction and processing.

    Args:
        None
    Returns:
        None
    """
    # Load METAR data from CSV and calculate relative humidity
    get_metars()

    # Load ERA5 data from GRIB file, create map of grid points and
    # collect data into DataFrame
    temp_cube, hum_cube, height_cube = get_era5_data()
    make_map(temp_cube)
    make_df(temp_cube, hum_cube, height_cube)


def assert_coord_equal(cube1, cube2, coord_name):
    """
    Asserts two cubes have the same coordinate values.

    Args:
        cube1 (iris.cube.Cube): First cube.
        cube2 (iris.cube.Cube): Second cube.
        coord_name (str): Name of the coordinate to compare.
    Returns:
        None
    """
    # Get the coordinate from both cubes
    coord1 = cube1.coord(coord_name)
    coord2 = cube2.coord(coord_name)

    # Check coordinate values are numerically equal
    if not np.allclose(coord1.points, coord2.points):
        raise ValueError(f'{coord_name} coordinate values differ between '
                         'cubes.')


def get_era5_data():
    """
    Loads ERA5 data from a GRIB file, extracts temperature, relative
    humidity, and geopotential height, and returns them as cubes.

    Args:
        None
    Returns:
        temp_cube (iris.cube.Cube): Cube containing temperature.
        hum_cube (iris.cube.Cube): Cube containing relative humidity.
        height_cube (iris.cube.Cube): Cube containing height above sea
                                      level.
    """
    # Load ERA5 data from GRIB file
    cubes = iris.load(ERA_FILE)

    # Extract data from cubes
    temp_cube = cubes.extract(iris.Constraint(name='air_temperature'))[0]
    hum_cube = cubes.extract(iris.Constraint(name='relative_humidity'))[0]
    geo_cube = cubes.extract(iris.Constraint(name='geopotential'))[0]

    # Convert temperature to Celsius
    temp_cube.convert_units('Celsius')

    # Convert geopotential to height above sea level
    height_cube = geo_cube / 9.80665

    # Ensure all cubes have the same time, pressure, latitude and
    # longitude coordinates
    for other_cube in [hum_cube, geo_cube]:
        for coord in ['time', 'pressure', 'latitude', 'longitude']:
            assert_coord_equal(temp_cube, other_cube, coord)

    return temp_cube, hum_cube, height_cube


def get_metars():
    """
    Loads METAR data from an Excel file, calculates relative humidity
    and saves to CSV.

    Args:
        None
    Returns:
        None
    """
    # Get data from csv file
    metar_data = pd.read_excel('metar_data.xlsx')

    # Get temps and dewpoints
    temps = metar_data['Temp'].values
    dewpoints = metar_data['Dew'].values

    # Calculate relative humidity
    relative_humidities = relative_humidity(temps, dewpoints)

    # Create a DataFrame with the data and save to csv
    metar_df = pd.DataFrame({
        'Date and Time (UTC)': metar_data['Time'],
        'Temperature (Celsius)': temps,
        'Dew Point (Celsius)': dewpoints,
        'Relative Humidity (%)': relative_humidities
    })

    metar_df.to_csv('metar_data_with_rh.csv', index=False)


def make_df(temp_cube, hum_cube, height_cube):
    """
    Collects data from ERA5 cubes into a DataFrame and saves it as CSV.

    Args:
        temp_cube (iris.cube.Cube): Cube containing temperature.
        hum_cube (iris.cube.Cube): Cube containing relative humidity.
        height_cube (iris.cube.Cube): Cube containing height above sea
                                      level.
    Returns:
        None
    """
    # As all coordinates are the same, we can just use one cube's
    time_points = temp_cube.coord('time').points
    time = temp_cube.coord('time').units.num2date(time_points)
    pressure = temp_cube.coord('pressure').points
    lat = temp_cube.coord('latitude').points
    lon = temp_cube.coord('longitude').points

    # Create full coordinate meshgrid
    time_grid, pressure_grid, lat_grid, lon_grid = np.meshgrid(
        time, pressure, lat, lon, indexing='ij'
    )

    # Put data into dataframe
    era_df = pd.DataFrame({
        'Data and Time (UTC)': time_grid.flatten(),
        'Latitude (degrees)': lat_grid.flatten(),
        'Longitude (degrees)': lon_grid.flatten(),
        'Pressure (hPa)': pressure_grid.flatten(),
        'Temperature (Celsius)': temp_cube.data.flatten(),
        'Relative Humidity (%)': hum_cube.data.flatten(),
        'Height Above Sea Level (m)': height_cube.data.flatten()
    })

    # Save as csv file
    era_df.to_csv('era5_data.csv', index=False)


def make_map(cube):
    """
    Creates a map visualisation of ERA5 grid points and saves it as an
    image.

    Args:
        cube (iris.cube.Cube): ERA5 data cube.
    Returns:
        None
    """
    # Get cube at first time and pressure level
    cube_at_first_time = cube[0, 0, :, :]

    # Get the latitude and longitude coordinates to plot
    lats = cube_at_first_time.coord('latitude').points
    lons = cube_at_first_time.coord('longitude').points

    # Create meshgrid for plotting
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Set the map projection
    projection = ccrs.PlateCarree()

    fig, ax = plt.subplots(figsize=(10, 10),
                           subplot_kw={'projection': projection})

    # Plot lat/lon points as scatter points
    ax.scatter(lon_grid, lat_grid, transform=projection)

    # Plot airport location
    ax.scatter([3.1107], [46.9989], color='red', transform=projection)

    # Add arrow and text identifying airport
    ax.annotate('LFQG', xy=(3.1107, 46.9989),
                xytext=(3.2, 47.1),
                arrowprops={'facecolor': 'black', 'shrink': 0.05},
                fontsize=12, color='black', transform=projection)

    # Add features
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    # Set extent (min lon, max lon, min lat, max lat)
    ax.set_extent([2, 4.3, 46, 48])

    # Save and close plot
    plt.savefig('era5_map.png', bbox_inches='tight')
    plt.close(fig)


def relative_humidity(temp_c, dewpoint_c):
    """
    Calculate relative humidity (%) from air temperature and dew point.
    Based on the Magnus formula:
        RH = 100 * (e_s(Td) / e_s(T))
           = 100 * (exp(a * Td / (b + Td)) / exp(a * T / (b + T)))

    Args:
        temp_c (float or np.ndarray): Air temperature in °C
                                      (can be a scalar or numpy array)
        dewpoint_c (float or np.ndarray): Dew point temperature in °C
                                          (same shape as temp_c)
    Returns:
        rh ((float or np.ndarray): Relative humidity in %
                                   (same shape as input)
    """
    # Constants for Magnus formula
    a = 17.67
    b = 243.5

    # Saturation and actual vapor pressures
    alpha = (a * dewpoint_c) / (b + dewpoint_c)
    beta = (a * temp_c) / (b + temp_c)

    # Calculate relative humidity
    rh = 100 * (np.exp(alpha) / np.exp(beta))

    return rh


if __name__ == "__main__":
    main()
    print('Finished')
