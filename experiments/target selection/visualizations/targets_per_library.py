#!/usr/bin/python3

import plotly.graph_objects as go

libs = ['php', 'openssl', 'sqlite3', 'poppler', 'lua', 'libxml2', 'libsndfile', 'libpng', 'libtiff']
targets = [9, 12, 1, 2, 1, 1, 1, 2, 1]
colors = ['rgb(0,128,0)', 'rgb(255,228,181)']

fig = go.Figure(data=[
    go.Bar(name='Processed', x=libs, y=targets, text=targets, textfont=dict(size=20),
            textposition='auto', marker_color=colors[0])])

fig.update_layout(
    title='Fuzz targets per library',
    titlefont_size=36,
    legend=dict(font_size=26),
    xaxis=dict(
        title='Library',
        titlefont_size=26,
        tickfont_size=20
    ),
    yaxis=dict(
        title='Number of fuzz targets',
        titlefont_size=26,
        tickfont_size=20
    )
)
fig.update_layout(barmode='stack')
fig.show()
