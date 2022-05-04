#!/usr/bin/python3

import plotly.graph_objects as go
import random
import json
import statistics

iter = 10
runs = ['5 minutes', '10 minutes', '15 minutes', '20 minutes', '30 minutes', '1 hours', '2 hours', '4 hours', '8 hours']
libs = {'php': 15, 'openssl': 17, 'sqlite3': 15, 'poppler': 59, 'lua': 14,
        'libxml2': 43, 'libpng': 106, 'libtiff': 37, 'libsndfile': 50}

fig_reached = go.Figure()
fig_triggered = go.Figure()
fig_detected = go.Figure()
fig = go.Figure()

for lib in libs:
    dir = f"./results/{lib}/"
    start = [x for x in range(libs[lib], libs[lib] + (len(runs)-1) * iter + 1, iter)]
    stop =  [x for x in range(libs[lib] + iter - 1, libs[lib] + (len(runs)-1) * iter + iter, iter)]
    
    bugs = {'reached': [], 'triggered': [], 'detected': []}
    means = {'reached': [], 'triggered': [], 'detected': []}
    std_devs = {'reached': [], 'triggered': [], 'detected': []}
    for i in range(len(start)):
        for j in range(start[i], stop[i] + 1):
            count = {'reached': [], 'triggered': [], 'detected': []}
            with open(f'{dir}{j:04d}/final_results', 'r') as file:
                data = json.load(file)
            for metric in data:
                for fuzzer in data[metric]:
                    count[metric] = [*count[metric], *data[metric][fuzzer]]
                bugs[metric].append(len(set(count[metric])))
        for metric in bugs:
            means[metric].append(statistics.mean(bugs[metric]))
            std_devs[metric].append(statistics.stdev(bugs[metric]))
        bugs = {'reached': [], 'triggered': [], 'detected': []}

    fig_reached.add_trace(go.Bar(x=runs, y=means['reached'], name=lib,
                                 error_y=dict(type='data', array=std_devs['reached'])))
    fig_triggered.add_trace(go.Bar(x=runs, y=means['triggered'], name=lib,
                                 error_y=dict(type='data', array=std_devs['triggered'])))
    fig_detected.add_trace(go.Bar(x=runs, y=means['detected'], name=lib,
                                 error_y=dict(type='data', array=std_devs['detected'])))

# Layout for the reached figure
fig_reached.update_layout(
    yaxis_range=[0,17],
    xaxis=dict(
        title='Fuzz duration',
        titlefont_size=15,
        tickfont_size=13
    ),
    yaxis=dict(
        title='Reached bugs',
        titlefont_size=15,
        tickfont_size=13,
        tickmode = 'linear',
        tick0 = 0,
        dtick = 2
    ),
    legend=dict(
        font_size=15,
    ),
    barmode='group'
)

# Layout for the triggered figure
fig_triggered.update_layout(
    yaxis_range=[0,7],
    xaxis=dict(
        title='Fuzz duration',
        titlefont_size=15,
        tickfont_size=13
    ),
    yaxis=dict(
        title='Triggered bugs',
        titlefont_size=15,
        tickfont_size=13,
        tickmode = 'linear',
        tick0 = 0,
        dtick = 1
    ),
    legend=dict(
        font_size=15,
    ),
    barmode='group'
)

# Layout for the detected figure
fig_detected.update_layout(
    yaxis_range=[0,4],
    xaxis=dict(
        title='Fuzz duration',
        titlefont_size=15,
        tickfont_size=13
    ),
    yaxis=dict(
        title='Detected bugs',
        titlefont_size=15,
        tickfont_size=13,
        tickmode = 'linear',
        tick0 = 0,
        dtick = 1
    ),
    legend=dict(
        font_size=15,
    ),
    barmode='group'
)

# Render the figures
fig_reached.show()
fig_triggered.show()
fig_detected.show()
