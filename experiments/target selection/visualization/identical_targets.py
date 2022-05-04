#!/usr/bin/python3

import plotly.graph_objects as go

libs = ['php', 'openssl', 'sqlite3', 'poppler', 'lua', 'libxml2', 'libsndfile', 'libpng', 'libtiff']
equal = [32198, 57081, 0, 1686, 462, 0, 472, 853, 154]
total = [50454, 90177, 483, 3840, 2285, 625, 1159, 1602, 241]
perc = [round((equal[i]/total[i]*100),2) for i in range(len(libs))]
inv = [(100.0-perc[i]) for i in range(len(libs))]
colors = ['rgb(0,128,0)', 'rgb(255,228,181)']

fig = go.Figure(data=[
    go.Bar(name='Identical Targets', x=libs, y=perc, marker_color=colors[0]),
    go.Bar(name='Different Targets', x=libs, y=inv, marker_color=colors[1])])

fig.update_layout(
    title='Identical fuzz targets per library',
    titlefont_size=36,
    legend=dict(font_size=26),
    xaxis=dict(
        title='Library',
        titlefont_size=26,
        tickfont_size=20
    ),
    yaxis=dict(
        title='Identical fuzz targets (%)',
        titlefont_size=26,
        tickfont_size=20
    )
)
fig.update_layout(barmode='stack')
fig.show()
