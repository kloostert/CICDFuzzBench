#!/usr/bin/python3

import plotly.graph_objects as go
from plotly.subplots import make_subplots

labels = ['Identical Targets', 'Different Targets']
libs = {'php':          [32198, 50454-32198], 
        'openssl':      [57081, 90177-57081], 
        'sqlite3':      [0,     483-0], 
        'poppler':      [1686,  3840-1686], 
        'lua':          [462,   2285-462], 
        'libxml2':      [0,     625-0], 
        'libpng':       [472,   1159-472], 
        'libtiff':      [853,   1602-853], 
        'libsndfile':   [154,   241-154]}

specs = [[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}], 
         [{'type':'domain'}, {'type':'domain'}, {'type':'domain'}], 
         [{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]]
fig = make_subplots(3, 3, specs=specs, subplot_titles=list(libs.keys()))

colors = ['rgb(0,128,0)', 'rgb(255,228,181)']

fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['php'], name='php'), 1, 1)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['openssl'], name='openssl'), 1, 2)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['sqlite3'], name='sqlite3'), 1, 3)

fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['poppler'], name='poppler'), 2, 1)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['lua'], name='lua'), 2, 2)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['libxml2'], name='libxml2'), 2, 3)

fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['libpng'], name='libpng'), 3, 1)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['libtiff'], name='libtiff'), 3, 2)
fig.add_trace(go.Pie(labels=labels, marker_colors=colors, textfont=dict(size=20), values=libs['libsndfile'], name='libsndfile'), 3, 3)

fig.update_layout(
    title='Identical Fuzz Targets per Library',
    titlefont_size=36,
    legend=dict(font_size=26)
)
fig.update_annotations(font_size=26)
fig.show()
