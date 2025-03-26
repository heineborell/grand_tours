import xml.etree.ElementTree as ET
import numpy as np
import contextily as ctx  # For map tiles
import geopandas as gpd  # For handling geographical data efficiently
#
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import style
plt.style.use('bmh')

# activity_id = 6929029131
activity_id = 6964331752

# Load and parse the GPX file
file_path = f'gpx_data/activity_{activity_id}.gpx'
tree = ET.parse(file_path)
root = tree.getroot()

# Extract namespaces
namespaces = {'default': 'http://www.topografix.com/GPX/1/1'}

# Extract coordinates and elevation data
latitudes = []
longitudes = []
elevations = []

for trkpt in root.findall('.//default:trkpt', namespaces):
    lat = float(trkpt.get('lat'))
    lon = float(trkpt.get('lon'))
    ele = float(trkpt.find('default:ele', namespaces).text)
    latitudes.append(lat)
    longitudes.append(lon)
    elevations.append(ele)

# Define the number of segments based on the number of points
k = 10  # Adjust as needed
segment_length = len(latitudes) // k

# Define alternating colors
# colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']
colors = ['blue', 'red']

# Create a GeoDataFrame for efficient handling and map overlay
gdf = gpd.GeoDataFrame({
    'latitude': latitudes,
    'longitude': longitudes
}, geometry=gpd.points_from_xy(longitudes, latitudes), crs='EPSG:4326')

# Project to Web Mercator for compatibility with map tiles
gdf = gdf.to_crs(epsg=3857)

# Extract projected coordinates
x_coords = gdf.geometry.x
y_coords = gdf.geometry.y

# Create a figure 
fig = plt.figure(figsize=(10, 8))
ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=3) 
ax2 = plt.subplot2grid((4, 1), (3, 0))        

# Plot the segments with alternating colors on the first subplot
for i in range(k):
    start = i * segment_length
    end = (i + 1) * segment_length if i < k - 1 else len(latitudes)
    ax1.plot(x_coords[start:end], y_coords[start:end], color=colors[i % len(colors)] , label=f'Segment {i + 1}')

##---- Add map tiles using contextily  --------##
## Option 1 - regular street map
# ctx.add_basemap(ax1, source=ctx.providers.OpenStreetMap.Mapnik)
#
## Option 2 - a simplified, grayscale map without labels.
ctx.add_basemap(ax1, source=ctx.providers.CartoDB.PositronNoLabels)
ctx.add_basemap(ax1, source=ctx.providers.CartoDB.PositronNoLabels)
#
## Option 3 - a dark-themed, simplified map without labels.
# ctx.add_basemap(ax1, source=ctx.providers.CartoDB.DarkMatterNoLabels) 

#-------
# Set standard tick marks for longitude and latitude rounded to 3 decimal places
min_lat, max_lat = round(min(latitudes), 3), round(max(latitudes), 3)
min_lon, max_lon = round(min(longitudes), 3), round(max(longitudes), 3)
#
lat_ticks = np.linspace(min_lat, max_lat, 6)
lon_ticks = np.linspace(min_lon, max_lon, 6)
#
# Convert lat/lon tick marks to Web Mercator for plotting
lon_ticks_merc = gpd.GeoSeries(gpd.points_from_xy(lon_ticks, [latitudes[0]] * len(lon_ticks)), crs='EPSG:4326').to_crs(epsg=3857).x
lat_ticks_merc = gpd.GeoSeries(gpd.points_from_xy([longitudes[0]] * len(lat_ticks), lat_ticks), crs='EPSG:4326').to_crs(epsg=3857).y
#
# Set tick positions and labels
ax1.set_xticks(lon_ticks_merc)
ax1.set_yticks(lat_ticks_merc)
ax1.set_xticklabels([f'{lon:.3f}' for lon in lon_ticks])
ax1.set_yticklabels([f'{lat:.3f}' for lat in lat_ticks])
#
ax1.set_xlabel('Longitude' , fontsize = 10)
ax1.set_ylabel('Latitude', fontsize = 10)
ax1.set_title(f"GPX Track for activity_id {activity_id}, k={k}", fontsize = 10)
#ax1.legend([f'Segment {i+1}' for i in range(k)], loc='lower right')
ax1.grid(True, linestyle='--', alpha=0.5)
#---------

# Plot the elevation profile with segment-based shading on the second subplot
distance = np.linspace(0, len(elevations) - 1, len(elevations))  # Use index as a proxy for distance

for i in range(k):
    start = i * segment_length
    end = (i + 1) * segment_length if i < k - 1 else len(elevations)
    ax2.plot(distance[start:end], elevations[start:end], color=colors[i % len(colors)], linewidth=1.5)
    ax2.fill_between(distance[start:end], elevations[start:end], color=colors[i % len(colors)], alpha=0.3)

ax2.set_xlabel('Track Point Index (meaningless for now)', fontsize = 10)
ax2.set_ylabel('Elevation (m)', fontsize = 10)
ax2.set_title('Elevation Profile with Matching Segment Colors', fontsize = 10)
ax2.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("Plots/"+ "activity_id_" + str(activity_id) + "_map_route.png", bbox_inches='tight')
plt.show()
