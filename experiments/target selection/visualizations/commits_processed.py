#!/usr/bin/python3

import plotly.graph_objects as go

libs = ['php', 'openssl', 'sqlite3', 'poppler', 'lua', 'libxml2', 'libsndfile', 'libpng', 'libtiff']
equal = [7821, 7847, 483, 1919, 2285, 625, 1158, 801, 241]
total = [127000, 30000, 25000, 7000, 5000, 5000, 4000, 4000, 3000]
perc = [round((equal[i]/total[i]*100),2) for i in range(len(libs))]
inv = [(100.0-perc[i]) for i in range(len(libs))]
colors = ['rgb(0,128,0)', 'rgb(255,228,181)']

fig = go.Figure(data=[
    go.Bar(name='Processed', x=libs, y=perc, marker_color=colors[0]),
    go.Bar(name='Unprocessed', x=libs, y=inv, marker_color=colors[1])])

fig.update_layout(
    title='Processed commits per library',
    titlefont_size=36,
    legend=dict(font_size=26),
    xaxis=dict(
        title='Library',
        titlefont_size=26,
        tickfont_size=20
    ),
    yaxis=dict(
        title='Commits processed from the repository (%)',
        titlefont_size=26,
        tickfont_size=20
    )
)
fig.update_layout(barmode='stack')
fig.show()
