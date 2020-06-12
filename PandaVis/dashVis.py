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
import math


class DashVis(object):
    def __init__(self):
        self.bakeReader = None

        external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css']
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }

    def run(self):

        self.bakeReader = BakeReader("C:\\Users\\43010600\\Data\\Personal\\hotgym.db")
        self.bakeReader.OpenDatabase()
        self.bakeReader.LoadDataStreams()


        with open('dashPlots.cfg') as f:
            cfgLayout = json.load(f)

        plotsPerRow = cfgLayout['plotsPerRow']


        figures = []
        for stream in cfgLayout['streams']:
            data = self.bakeReader.dataStreams[stream['name']].allData

            if stream['type'] == 'line':
                fig = go.Figure(data=go.Scatter(x=data[0, :], y=data[1, :]))
                figures.append([stream['name'],fig])

                # Set theme, margin, and annotation in layout
                fig.update_layout(
                    title=stream['name'],
                    template="plotly_dark",
                    #margin=dict(r=10, t=25, b=40, l=60),
                    # annotations=[
                    #     dict(
                    #         text="abc Source: NOAA",
                    #         showarrow=False,
                    #         xref="paper",
                    #         yref="paper",
                    #         x=0,
                    #         y=0)
                    # ]
                )

        
        
        columnClassName = "twelve columns"
        if plotsPerRow == 3:
             columnClassName = "four columns"
        elif plotsPerRow == 2:
            columnClassName = "six columns"

        columnClassName = "col-sm-4"
       
        graphs =  [html.Div(
            ([html.Div([dcc.Graph(
                        id='plot_'+x[0],
                        figure=x[1]
                    )], className=columnClassName) for x in figures]
            ),className="row")
                   ]

        print(graphs)
        childs = [
            html.H4(
                children='Dash vis',
                style={
                    'textAlign': 'center',
                    'color': self.colors['text']
                }
            ),]

        childs += graphs

        childs+=[
            html.Label('Slider'),
            dcc.Slider(
                min=0,
                max=1000,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1,1000, 100)},
                value=5,
            ),]

        self.app.layout = html.Div(style={'backgroundColor': self.colors['background']}, children=childs)


if __name__ == '__main__':
    dash = DashVis()
    dash.run()
    dash.app.run_server(debug=True)
