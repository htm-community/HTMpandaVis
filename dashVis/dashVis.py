# -*- coding: utf-8 -*-

import os
import json
import math
import random
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from bakeReader.bakeReader import BakeReader


class cDashVis(object):
    def __init__(self):
        self.bakeReader = None

        #external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css']
        self.app = dash.Dash(__name__,) #external_stylesheets=external_stylesheets)

        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }

        number_of_colors = 30
        random.seed(1)
        print(random.randint(1,50))
        self.randomColors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                 for i in range(number_of_colors)]


    def run(self, databaseFilePath, layout):

        self.bakeReader = BakeReader(databaseFilePath)
        self.bakeReader.OpenDatabase()
        self.bakeReader.LoadDataStreams()


        with open(os.path.join(os.getcwd(),'..','dashVis','layouts',layout+'.txt')) as f:
            cfgLayout = json.load(f)

        plotsPerRow = cfgLayout['plotsPerRow']


        figures = []
        cnt = 0
        for stream in cfgLayout['streams']:
            try:
                data = self.bakeReader.dataStreams[stream['name']].allData
            except KeyError:
                print('Requested data stream "'+str(stream['name'])+'" was not found in the database!')
                return

            if stream['type'] == 'line':
                fig = go.Figure(data=go.Scatter(x=data[0, :], y=data[1, :],line=dict(color=self.randomColors[cnt])))
                figures.append([stream['name'],fig])

                # Set theme, margin, and annotation in layout
                fig.update_layout(
                    title=stream['name'],
                    xaxis_title="iteration",
                    yaxis_title=stream['yaxis'],
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
                cnt+=1
                if cnt>=len(self.randomColors):
                    cnt=0

        
        
        columnClassName = "col-sm-12"
        if plotsPerRow == 4:
             columnClassName = "col-sm-3"
        elif plotsPerRow == 3:
             columnClassName = "col-sm-4"
        elif plotsPerRow == 2:
            columnClassName = "col-sm-6"
       
        graphs =  [html.Div(
            ([html.Div([dcc.Graph(
                        id='plot_'+x[0],
                        figure=x[1]
                    )], className=columnClassName) for x in figures]
            ),className="row")
                   ]

        childs = [
            html.H4(
                children='Dash vis',
                style={
                    'textAlign': 'center',
                    'color': self.colors['text']
                }
            ),]

        childs += graphs

        
        self.app.layout = html.Div(style={'backgroundColor': self.colors['background']}, children=childs)

        self.app.run_server(debug=True, use_reloader=False)

if __name__ == '__main__':
    dash = cDashVis()
    dash.run()

