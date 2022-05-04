#!/usr/bin/python3

import plotly.graph_objects as go

libs = ['php', 'openssl', 'sqlite3', 'poppler', 'lua', 'libxml2', 'libsndfile', 'libpng', 'libtiff']
targets = [7821, 7847, 483, 1919, 2285, 625, 1158, 801, 241]
colors = ['rgb(0,128,0)', 'rgb(255,228,181)']

fig = go.Figure(data=[
    go.Bar(name='Processed', x=libs, y=targets, text=targets, textfont=dict(size=20),
            textposition='auto', marker_color=colors[0])])

fig.update_layout(
    title='Commits processed per library',
    titlefont_size=36,
    legend=dict(font_size=26),
    xaxis=dict(
        title='Library',
        titlefont_size=26,
        tickfont_size=20
    ),
    yaxis=dict(
        title='Number of commits processed',
        titlefont_size=26,
        tickfont_size=20
    )
)
fig.update_layout(barmode='stack')
fig.show()
