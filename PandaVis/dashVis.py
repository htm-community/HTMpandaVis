# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

from bakeReader.bakeReader import BakeReader
import json


class DashVis(object):
    def __init__(self):
        self.bakeReader = None

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }

    def run(self):

        self.bakeReader = BakeReader('/media/D/hotgym.db')
        self.bakeReader.OpenDatabase()
        self.bakeReader.LoadDataStreams()


        with open('dashPlots.cfg') as f:
            cfgLayout = json.load(f)

        dimensions = cfgLayout['subplotDimensions']
        print("Creating subplot rows:"+str(dimensions[0])+" cols:"+str(dimensions[1]))

        # Initialize figure with subplots
        fig = make_subplots(
            rows=dimensions[0], cols=dimensions[1])


        for stream in cfgLayout['streams']:
            data = self.bakeReader.dataStreams[stream['name']].allData

            if stream['type'] == 'line':
                fig.add_trace(go.Scatter(x=data[0,:], y=data[1,:]),row=stream['pos'][0], col=stream['pos'][1])
                fig['layout']['']
        # Set theme, margin, and annotation in layout
        fig.update_layout(
            template="plotly_dark",
            margin=dict(r=10, t=25, b=40, l=60),
            annotations=[
                dict(
                    text="abc Source: NOAA",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=0)
            ]
        )


        self.app.layout = html.Div(style={'backgroundColor': self.colors['background']}, children=[
            html.H4(
                children='Dash vis',
                style={
                    'textAlign': 'center',
                    'color': self.colors['text']
                }
            ),

            dcc.Graph(
                id='example-graph',
                figure=fig
            ),
            html.Label('Slider'),
            dcc.Slider(
                min=0,
                max=1000,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1,1000, 100)},
                value=5,
            ),
        ])

if __name__ == '__main__':
    dash = DashVis()
    dash.run()
    dash.app.run_server(debug=True)