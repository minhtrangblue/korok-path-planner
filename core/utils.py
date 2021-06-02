"""
Script used to generate the base map html template from folium
"""

import pandas as pd
from PIL import Image
from folium import Map, raster_layers, LatLngPopup, FeatureGroup, Marker, Icon, plugins


# create base map
img = Image.open('data/maps_allseeds.png').convert('RGB')

m = Map(location=[img.height/2, img.width/2],
        tiles=None,
        crs='Simple',
        max_zoom=5,
        min_zoom=-20,
        zoom_start=-10,
        prefer_canvas=True)

# add image overlay
raster_layers.ImageOverlay(image='data/maps_allseeds.png',
                           bounds=[[0, 0], [img.height, img.width]],
                           overlay=False).add_to(m)
m.add_child(LatLngPopup())

# add markers for korok seeds locations
df = pd.read_csv('data/all_seeds.csv')
# plugins.MarkerCluster(locations=[[row['y'],row['x']] for _, row in df.iterrows()],
#                       icons=[folium.Icon(color="green", icon='glyphicon-leaf') for _, row in df.iterrows()],
#                       ).add_to(m)

markers_layer = FeatureGroup(name='markers')
for _, row in df.iterrows():
    Marker(
        location=[row['y'], row['x']],
        icon=Icon(color="green", icon='glyphicon-leaf'),
    ).add_to(markers_layer)
m.add_child(markers_layer)


# add tools menu
plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen').add_to(m)
plugins.Draw(export=True, filename='selected.geojson',
             position='topleft',
             draw_options={'polygon': False,
                           'polyline': False,
                           'rectangle': True,
                           'circle': False,
                           'marker': False,
                           'circlemarker': False},
             edit_options={'allowIntersection': False,
                           'featureGroup': 'selected'}).add_to(m)

# save map as html template
m.save('flaskr/templates/map.html')
