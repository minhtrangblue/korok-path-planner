# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import json


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('data/all_seeds.csv')

img = Image.open('data/maps_allseeds.png').convert('RGB')

template = dict(layout=go.Layout(xaxis=dict(range=[0, img.width], showgrid=False, zeroline=False, visible=False),
                     yaxis=dict(range=[0, img.height], showgrid=False, zeroline=False, visible=False),
                     showlegend=False))

def get_plot(selectedData):
    fig = go.Figure(data=go.Scatter(x=selectedData['x'], y=selectedData['y'], mode='markers'),
                    layout=go.Layout(
                        xaxis=dict(range=[0, img.width], showgrid=False, zeroline=False, visible=False),
                        yaxis=dict(range=[0, img.height], showgrid=False, zeroline=False, visible=False),
                        # title="Korok Path",
                        showlegend=False,
                        autosize=True,
                        # uirevision='static',
                        # updatemenus=[dict(type="buttons",
                        #                   buttons=[dict(label="Play",
                        #                                 method="animate",
                        #                                 args=[None])])]
                    ),
                    # frames=[go.Frame(data=go.Scatter(x=[selectedData.iloc[i]['x']], y=[selectedData.iloc[i]['y']],
                    #                                  mode="markers",
                    #                                  marker=dict(color="red", size=10))) for i in range(selectedData.shape[0])]
                    )

    #fig = px.scatter(selectedData, x='x', y='y')
    fig.update_layout(template=template, clickmode='event+select')
    fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=0,
            y=img.height,
            sizex=img.width,
            sizey=img.height,
            sizing="fill",
            opacity=1,
            layer="below")
    )
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1)

    return fig


fig = get_plot(df)
app.layout = html.Div(children=[
    dcc.Graph(
        id='koroks-location',
        figure=fig,
        # config=config,
        style={'height': '100vh'}
    ),
    html.Button('Reset', id='reset_btn'),
    dcc.Markdown("Points selected: "),
    html.Pre(id="selected-data")],
    # style={'display': 'inline-block'}
)



@app.callback(
    # Output('selected-data', 'children'),
    Output('koroks-location', 'figure'),
    Input('reset_btn', 'n_clicks'),
    Input('koroks-location', 'selectedData'))
def display_selected_data(reset_btn, selectedData):
    changed_prop = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if changed_prop == '.':
        fig = get_plot(df)
    elif changed_prop == 'reset_btn.n_clicks':
        fig = get_plot(df)
    elif changed_prop == 'koroks-location.selectedData':
        pidx = [point['pointIndex'] for point in selectedData['points']]
        fig = get_plot(df.iloc[pidx])
    return fig

# m= folium.Map(location=[-50, 50],tiles='file:///C:/Users/Trang/PycharmProjects/KorokPlanner/tiles/{z}/{x}/{y}.png', attr='Reddit', name='Korok Map', max_zoom=5, min_zoom=1, zoom_start=3,crs='Simple')
# m.add_child(folium.LatLngPopup())
# m.save('data/map.html')

m = folium.Map(location=[1000,1200], tiles=None,crs='Simple',max_zoom=5, min_zoom=-20, zoom_start=-10, prefer_canvas=True)
raster_layers.ImageOverlay(image='data/maps_allseeds.png',bounds=[[0,0],[2000,2400]], overlay=False).add_to(m)
m.add_child(folium.LatLngPopup())


df = pd.read_csv('data/all_seeds.csv')


# plugins.MarkerCluster(locations=[[row['y'],row['x']] for _, row in df.iterrows()],
#                       icons=[folium.Icon(color="green", icon='glyphicon-leaf') for _, row in df.iterrows()],
#                       ).add_to(m)

markers_layer = FeatureGroup(name='markers')
for _, row in df.iterrows():
    folium.Marker(
        location=[row['y'], row['x']],
        icon=folium.Icon(color="green", icon='glyphicon-leaf'),
    ).add_to(markers_layer)
m.add_child(markers_layer)

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
m.save('flaskr/templates/map.html')

if __name__ == '__main__':
    app.run_server(debug=True)